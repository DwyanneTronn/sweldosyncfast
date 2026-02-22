from typing import Optional, List
from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship, JSON
from enum import Enum
from pydantic import BaseModel

# --- Enums ---
class PayrollStatus(str, Enum):
    DRAFT = "draft"
    COMPUTED = "computed"
    FINALIZED = "finalized"

class LineItemCategory(str, Enum):
    BASIC = "basic"
    OVERTIME = "overtime"
    ALLOWANCE_TAXABLE = "allowance_taxable"
    ALLOWANCE_NON_TAXABLE = "allowance_non_taxable"
    DEDUCTION = "deduction" # Generic deduction
    ABSENCE = "absence" # Deduction

# --- Shared Models ---
class Tenant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    api_key: str = Field(index=True) # Simple API Key Auth
    is_active: bool = True

class StatutoryTable(SQLModel, table=True):
    """
    Stores tax tables, SSS tables, etc. dynamically.
    'data' field stores the JSON structure of brackets.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tax_type: str = Field(index=True) # "SSS", "PHIC", "HDMF", "WITHHOLDING_TAX"
    effective_date: date
    region: str = "PH"
    data: dict = Field(default={}, sa_type=JSON) 

# --- Employee Domain ---
class Employee(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    external_id: str = Field(index=True) # ID from the external HR system
    first_name: str
    last_name: str
    email: Optional[str] = None
    tin: Optional[str] = None
    sss_no: Optional[str] = None
    phic_no: Optional[str] = None
    hdmf_no: Optional[str] = None
    daily_rate: float
    monthly_rate: float
    
    # Relationships
    payroll_results: List["PayrollResult"] = Relationship(back_populates="employee")

# --- Payroll Domain ---
class PayrollRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True)
    period_start: date
    period_end: date
    payout_date: date
    status: PayrollStatus = Field(default=PayrollStatus.DRAFT)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    line_items: List["PayrollLineItem"] = Relationship(back_populates="payroll_run")
    results: List["PayrollResult"] = Relationship(back_populates="payroll_run")

class PayrollLineItem(SQLModel, table=True):
    """
    Raw ingested items from external system (The 'Metering' input).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    payroll_run_id: int = Field(foreign_key="payrollrun.id", index=True)
    employee_id: int = Field(foreign_key="employee.id", index=True)
    description: str
    amount: float # Positive for earnings, negative for deductions/absences
    category: LineItemCategory
    
    payroll_run: PayrollRun = Relationship(back_populates="line_items")

class PayrollResult(SQLModel, table=True):
    """
    The final computed 'Billing' line.
    Contains the Net Pay and statutory breakdowns.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    payroll_run_id: int = Field(foreign_key="payrollrun.id", index=True)
    employee_id: int = Field(foreign_key="employee.id", index=True)
    
    gross_income: float = 0.0
    total_deductions: float = 0.0
    net_pay: float = 0.0
    
    # Statutory Deductions (Computed by this engine)
    sss_contribution: float = 0.0
    phic_contribution: float = 0.0
    hdmf_contribution: float = 0.0
    withholding_tax: float = 0.0
    
    payroll_run: PayrollRun = Relationship(back_populates="results")
    employee: Employee = Relationship(back_populates="payroll_results")

# --- Pydantic Schemas for API ---
class LineItemInput(BaseModel):
    description: str
    amount: float
    category: LineItemCategory

class EmployeePayrollInput(BaseModel):
    external_employee_id: str
    items: List[LineItemInput]

class BatchIngestPayload(BaseModel):
    period_start: date
    period_end: date
    payout_date: date
    employees: List[EmployeePayrollInput]
