from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models import Employee, Tenant
from app.auth import get_current_tenant

router = APIRouter()

@router.post("/", response_model=Employee)
def create_employee(
    employee: Employee, 
    db: Session = Depends(get_session),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Sync/Create an employee record from external system.
    Automatically scopes to the authenticated tenant.
    """
    # Force tenant_id from auth context
    employee.tenant_id = current_tenant.id

    # Check if exists by external_id within this tenant
    statement = select(Employee).where(
        (Employee.external_id == employee.external_id) & 
        (Employee.tenant_id == current_tenant.id)
    )
    existing_employee = db.exec(statement).first()
    
    if existing_employee:
        # Update logic
        for key, value in employee.dict(exclude_unset=True).items():
            # Prevent overwriting tenant_id or id if passed in body (though id is optional in input model usually)
            if key not in ["id", "tenant_id"]:
                setattr(existing_employee, key, value)
        db.add(existing_employee)
        db.commit()
        db.refresh(existing_employee)
        return existing_employee
        
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

@router.get("/", response_model=List[Employee])
def list_employees(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_session),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    statement = select(Employee).where(Employee.tenant_id == current_tenant.id).offset(skip).limit(limit)
    employees = db.exec(statement).all()
    return employees

@router.get("/{employee_id}", response_model=Employee)
def get_employee(
    employee_id: int, 
    db: Session = Depends(get_session),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    # Ensure fetching only from current tenant
    statement = select(Employee).where(
        (Employee.id == employee_id) & 
        (Employee.tenant_id == current_tenant.id)
    )
    employee = db.exec(statement).first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee
