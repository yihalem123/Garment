"""
Employee schemas
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):
    """Employee creation schema"""
    employee_id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    position: str
    department: str
    base_salary: Decimal
    hourly_rate: Optional[Decimal] = None
    overtime_rate: Optional[Decimal] = None
    commission_rate: Optional[Decimal] = None
    work_hours_per_week: Optional[int] = 40
    shop_id: Optional[int] = None
    manager_id: Optional[int] = None
    hire_date: datetime


class EmployeeUpdate(BaseModel):
    """Employee update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    employment_status: Optional[str] = None
    base_salary: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    overtime_rate: Optional[Decimal] = None
    commission_rate: Optional[Decimal] = None
    work_hours_per_week: Optional[int] = None
    shop_id: Optional[int] = None
    manager_id: Optional[int] = None
    termination_date: Optional[datetime] = None


class EmployeeResponse(BaseModel):
    """Employee response schema"""
    id: int
    employee_id: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    position: str
    department: str
    employment_status: str
    hire_date: datetime
    termination_date: Optional[datetime] = None
    base_salary: Decimal
    hourly_rate: Optional[Decimal] = None
    overtime_rate: Optional[Decimal] = None
    commission_rate: Optional[Decimal] = None
    work_hours_per_week: Optional[int] = None
    shop_id: Optional[int] = None
    manager_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """Employee list response with shop information"""
    id: int
    employee_id: str
    full_name: str
    email: str
    position: str
    department: str
    employment_status: str
    base_salary: Decimal
    shop_name: Optional[str] = None
    manager_name: Optional[str] = None
    hire_date: datetime
    
    class Config:
        from_attributes = True
