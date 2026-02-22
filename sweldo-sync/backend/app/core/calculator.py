from typing import List
from decimal import Decimal, ROUND_HALF_UP

# Placeholder for statutory logic. In a real app, these would query the StatutoryTable model.
# Using simple logic for the prototype.

def compute_sss(gross_income: Decimal) -> Decimal:
    """
    Simplified SSS computation. 
    Real logic would look up the bracket in the database.
    """
    # Example: 4.5% of gross, capped at specific amounts
    rate = Decimal("0.045")
    contribution = gross_income * rate
    # Cap at some arbitrary max for prototype (e.g. 1350)
    if contribution > Decimal("1350.00"):
        return Decimal("1350.00")
    return contribution.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def compute_philhealth(gross_income: Decimal) -> Decimal:
    """
    Simplified PhilHealth computation.
    """
    # Example: 4% shared (2% employee share)
    rate = Decimal("0.02") 
    contribution = gross_income * rate
    return contribution.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def compute_hdmf(gross_income: Decimal) -> Decimal:
    """
    Simplified Pag-IBIG (HDMF) computation.
    """
    # Usually 100 pesos max for employee
    rate = Decimal("0.02")
    contribution = gross_income * rate
    if contribution > Decimal("100.00"):
        return Decimal("100.00")
    return contribution.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def compute_tax(taxable_income: Decimal) -> Decimal:
    """
    Simplified Withholding Tax computation.
    """
    # Very basic progressive tax stub
    if taxable_income <= Decimal("20833.00"):
        return Decimal("0.00")
    elif taxable_income <= Decimal("33333.00"):
        # 20% in excess of 20,833
        excess = taxable_income - Decimal("20833.00")
        return (excess * Decimal("0.20")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        # 2500 + 25% in excess of 33,333
        excess = taxable_income - Decimal("33333.00")
        base = Decimal("2500.00")
        return (base + (excess * Decimal("0.25"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class PayrollCalculator:
    def process_employee_payroll(self, gross_income: Decimal) -> dict:
        sss = compute_sss(gross_income)
        phic = compute_philhealth(gross_income)
        hdmf = compute_hdmf(gross_income)
        
        total_statutory = sss + phic + hdmf
        taxable_income = gross_income - total_statutory
        
        tax = compute_tax(taxable_income)
        total_deductions = total_statutory + tax
        net_pay = gross_income - total_deductions
        
        return {
            "gross_income": gross_income,
            "sss_contribution": sss,
            "phic_contribution": phic,
            "hdmf_contribution": hdmf,
            "withholding_tax": tax,
            "total_deductions": total_deductions,
            "net_pay": net_pay
        }
