from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List
from datetime import date
from decimal import Decimal

from app.database import get_session, engine
from app.models import (
    PayrollRun, 
    PayrollLineItem, 
    Employee, 
    BatchIngestPayload, 
    PayrollResult, 
    LineItemCategory, 
    PayrollStatus,
    Tenant
)
from app.auth import get_current_tenant
from app.core.calculator import PayrollCalculator

router = APIRouter()
calculator = PayrollCalculator()

def process_batch(payroll_run_id: int, db_session: Session = None):
    """
    Background task to process payroll calculations.
    Creates its own session to avoid DetachedInstanceError or Closed Session issues.
    """
    if db_session:
        # Use provided session (for testing)
        _process_logic(payroll_run_id, db_session)
    else:
        # Create new session
        with Session(engine) as db:
            _process_logic(payroll_run_id, db)

def _process_logic(payroll_run_id: int, db: Session):
    payroll_run = db.get(PayrollRun, payroll_run_id)
    if not payroll_run:
        return
        
    payroll_run.status = PayrollStatus.COMPUTED
    db.add(payroll_run)
    db.commit()

    # Get all line items for this run
    statement = select(PayrollLineItem).where(PayrollLineItem.payroll_run_id == payroll_run_id)
    line_items = db.exec(statement).all()
    
    # Group by employee
    employee_items = {}
    for item in line_items:
        if item.employee_id not in employee_items:
            employee_items[item.employee_id] = []
        employee_items[item.employee_id].append(item)
        
    # Calculate for each employee
    for emp_id, items in employee_items.items():
        gross_income = Decimal("0.00")
        total_deductions_from_items = Decimal("0.00")
        
        for item in items:
            amount = Decimal(str(item.amount))
            if item.category in [LineItemCategory.BASIC, LineItemCategory.OVERTIME, LineItemCategory.ALLOWANCE_TAXABLE]:
                gross_income += amount
            elif item.category in [LineItemCategory.DEDUCTION, LineItemCategory.ABSENCE]:
                # Deductions are typically negative in net pay calc, 
                # but if they come in as positive numbers representing a deduction, we sum them here.
                total_deductions_from_items += amount

        # Compute statutory based on Gross Income
        computed = calculator.process_employee_payroll(gross_income)
        
        # Total Deductions = Statutory + Tax + Other Deductions (from line items)
        final_total_deductions = computed["total_deductions"] + total_deductions_from_items
        final_net_pay = gross_income - final_total_deductions

        # Create Result
        result = PayrollResult(
            payroll_run_id=payroll_run_id,
            employee_id=emp_id,
            gross_income=float(gross_income),
            total_deductions=float(final_total_deductions),
            net_pay=float(final_net_pay),
            sss_contribution=float(computed["sss_contribution"]),
            phic_contribution=float(computed["phic_contribution"]),
            hdmf_contribution=float(computed["hdmf_contribution"]),
            withholding_tax=float(computed["withholding_tax"])
        )
        db.add(result)
    
    db.commit()


@router.post("/batch/ingest", response_model=PayrollRun)
async def ingest_payroll_batch(
    payload: BatchIngestPayload, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    # 1. Create Payroll Run Record
    payroll_run = PayrollRun(
        tenant_id=current_tenant.id,
        period_start=payload.period_start,
        period_end=payload.period_end,
        payout_date=payload.payout_date,
        status=PayrollStatus.DRAFT
    )
    db.add(payroll_run)
    db.commit()
    db.refresh(payroll_run)
    
    # 2. Process Line Items
    for emp_input in payload.employees:
        # Find Employee belonging to THIS tenant
        statement = select(Employee).where(
            (Employee.external_id == emp_input.external_employee_id) &
            (Employee.tenant_id == current_tenant.id)
        )
        employee = db.exec(statement).first()
        
        if not employee:
            # Skip if employee not found
            continue
            
        for item in emp_input.items:
            db_item = PayrollLineItem(
                payroll_run_id=payroll_run.id,
                employee_id=employee.id,
                description=item.description,
                amount=item.amount,
                category=item.category
            )
            db.add(db_item)
            
    db.commit()
    
    # 3. Trigger Calculation Background Task
    background_tasks.add_task(process_batch, payroll_run.id)
    
    return payroll_run

@router.get("/batch/{run_id}", response_model=PayrollRun)
def get_payroll_run(
    run_id: int, 
    db: Session = Depends(get_session),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    run = db.get(PayrollRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
        
    if run.tenant_id != current_tenant.id:
        raise HTTPException(status_code=403, detail="Access forbidden")
        
    return run

@router.get("/batch/{run_id}/results", response_model=List[PayrollResult])
def get_payroll_results(
    run_id: int, 
    db: Session = Depends(get_session),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    # First verify run ownership
    run = db.get(PayrollRun, run_id)
    if not run or run.tenant_id != current_tenant.id:
        raise HTTPException(status_code=404, detail="Payroll run not found or access denied")
        
    statement = select(PayrollResult).where(PayrollResult.payroll_run_id == run_id)
    results = db.exec(statement).all()
    return results
