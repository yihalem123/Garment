"""
Payroll schemas
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel


class PayrollRecordCreate(BaseModel):
    """Payroll record creation schema"""
    employee_id: int
    payroll_period_start: datetime
    payroll_period_end: datetime
    base_salary: Decimal
    hours_worked: Optional[Decimal] = None
    overtime_hours: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    overtime_rate: Optional[Decimal] = None
    commission_pay: Optional[Decimal] = None
    bonus_pay: Optional[Decimal] = None
    tax_deduction: Optional[Decimal] = None
    insurance_deduction: Optional[Decimal] = None
    other_deductions: Optional[Decimal] = None
    notes: Optional[str] = None


class PayrollRecordUpdate(BaseModel):
    """Payroll record update schema"""
    payment_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class PayrollRecordResponse(BaseModel):
    """Payroll record response schema"""
    id: int
    employee_id: int
    employee_name: str
    payroll_period_start: datetime
    payroll_period_end: datetime
    base_salary: Decimal
    hours_worked: Optional[Decimal] = None
    overtime_hours: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    overtime_rate: Optional[Decimal] = None
    regular_pay: Decimal
    overtime_pay: Optional[Decimal] = None
    commission_pay: Optional[Decimal] = None
    bonus_pay: Optional[Decimal] = None
    tax_deduction: Optional[Decimal] = None
    insurance_deduction: Optional[Decimal] = None
    other_deductions: Optional[Decimal] = None
    gross_pay: Decimal
    total_deductions: Decimal
    net_pay: Decimal
    payment_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PayrollSummaryResponse(BaseModel):
    """Payroll summary response schema"""
    id: int
    period_start: datetime
    period_end: datetime
    shop_id: Optional[int] = None
    shop_name: Optional[str] = None
    total_employees: int
    total_gross_pay: Decimal
    total_deductions: Decimal
    total_net_pay: Decimal
    is_processed: bool
    processed_at: Optional[datetime] = None
    processed_by: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PayrollProcessingRequest(BaseModel):
    """Payroll processing request schema"""
    period_start: datetime
    period_end: datetime
    shop_id: Optional[int] = None
    include_inactive: bool = False


class PayrollPaymentRequest(BaseModel):
    """Payroll payment request schema"""
    payroll_record_ids: list[int]
    payment_method: str
    payment_reference: Optional[str] = None
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None
