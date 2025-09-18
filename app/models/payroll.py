"""
Payroll models
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum
from decimal import Decimal

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.employee import Employee


class PayrollStatus(str, Enum):
    """Payroll status"""
    PENDING = "pending"
    PROCESSED = "processed"
    PAID = "paid"
    CANCELLED = "cancelled"


class PayrollRecord(SQLModel, table=True):
    """Payroll record for tracking employee payments"""
    __tablename__ = "payroll_records"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Employee Information
    employee_id: int = Field(foreign_key="employees.id", description="Employee ID")
    payroll_period_start: datetime = Field(description="Payroll period start date")
    payroll_period_end: datetime = Field(description="Payroll period end date")
    
    # Salary Details
    base_salary: Decimal = Field(description="Base salary for the period")
    hours_worked: Optional[Decimal] = Field(default=None, description="Hours worked (for hourly employees)")
    overtime_hours: Optional[Decimal] = Field(default=None, description="Overtime hours")
    hourly_rate: Optional[Decimal] = Field(default=None, description="Hourly rate")
    overtime_rate: Optional[Decimal] = Field(default=None, description="Overtime rate multiplier")
    
    # Calculations
    regular_pay: Decimal = Field(description="Regular pay amount")
    overtime_pay: Optional[Decimal] = Field(default=None, description="Overtime pay amount")
    commission_pay: Optional[Decimal] = Field(default=None, description="Commission pay amount")
    bonus_pay: Optional[Decimal] = Field(default=None, description="Bonus pay amount")
    
    # Deductions
    tax_deduction: Optional[Decimal] = Field(default=None, description="Tax deduction")
    insurance_deduction: Optional[Decimal] = Field(default=None, description="Insurance deduction")
    other_deductions: Optional[Decimal] = Field(default=None, description="Other deductions")
    
    # Final Amounts
    gross_pay: Decimal = Field(description="Gross pay amount")
    total_deductions: Decimal = Field(description="Total deductions")
    net_pay: Decimal = Field(description="Net pay amount")
    
    # Payment Information
    payment_date: Optional[datetime] = Field(default=None, description="Date when payment was made")
    payment_method: Optional[str] = Field(default=None, description="Payment method (bank_transfer, cash, check)")
    payment_reference: Optional[str] = Field(default=None, description="Payment reference number")
    status: PayrollStatus = Field(default=PayrollStatus.PENDING, description="Payroll status")
    
    # Notes
    notes: Optional[str] = Field(default=None, description="Additional notes")
    
    # System Fields
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    employee: "Employee" = Relationship(back_populates="payroll_records")
    
    def calculate_gross_pay(self) -> Decimal:
        """Calculate gross pay"""
        gross = self.regular_pay
        if self.overtime_pay:
            gross += self.overtime_pay
        if self.commission_pay:
            gross += self.commission_pay
        if self.bonus_pay:
            gross += self.bonus_pay
        return gross
    
    def calculate_net_pay(self) -> Decimal:
        """Calculate net pay after deductions"""
        total_deductions = Decimal('0')
        if self.tax_deduction:
            total_deductions += self.tax_deduction
        if self.insurance_deduction:
            total_deductions += self.insurance_deduction
        if self.other_deductions:
            total_deductions += self.other_deductions
        
        return self.gross_pay - total_deductions


class PayrollSummary(SQLModel, table=True):
    """Payroll summary for management overview"""
    __tablename__ = "payroll_summaries"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Period Information
    period_start: datetime = Field(description="Payroll period start")
    period_end: datetime = Field(description="Payroll period end")
    shop_id: Optional[int] = Field(default=None, foreign_key="shops.id", description="Shop ID (if shop-specific)")
    
    # Summary Statistics
    total_employees: int = Field(description="Total employees in payroll")
    total_gross_pay: Decimal = Field(description="Total gross pay")
    total_deductions: Decimal = Field(description="Total deductions")
    total_net_pay: Decimal = Field(description="Total net pay")
    
    # Status
    is_processed: bool = Field(default=False, description="Is payroll processed")
    processed_at: Optional[datetime] = Field(default=None, description="When payroll was processed")
    processed_by: Optional[int] = Field(default=None, foreign_key="users.id", description="Who processed the payroll")
    
    # System Fields
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
