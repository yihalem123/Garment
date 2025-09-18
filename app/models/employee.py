"""
Employee model
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum
from decimal import Decimal

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.shop import Shop
    from app.models.payroll import PayrollRecord


class EmploymentStatus(str, Enum):
    """Employment status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"


class Employee(SQLModel, table=True):
    """Employee model - separate from User for better management"""
    __tablename__ = "employees"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Basic Information
    employee_id: str = Field(unique=True, index=True, description="Employee ID (e.g., EMP001)")
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
    email: str = Field(unique=True, index=True, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    address: Optional[str] = Field(default=None, description="Address")
    
    # Employment Details
    position: str = Field(description="Job position/title")
    department: str = Field(description="Department")
    employment_status: EmploymentStatus = Field(default=EmploymentStatus.ACTIVE)
    hire_date: datetime = Field(description="Date of hire")
    termination_date: Optional[datetime] = Field(default=None, description="Date of termination")
    
    # Salary Information
    base_salary: Decimal = Field(description="Monthly base salary")
    hourly_rate: Optional[Decimal] = Field(default=None, description="Hourly rate (if applicable)")
    overtime_rate: Optional[Decimal] = Field(default=None, description="Overtime rate multiplier")
    commission_rate: Optional[Decimal] = Field(default=None, description="Commission rate (%)")
    
    # Work Details
    work_hours_per_week: Optional[int] = Field(default=40, description="Standard work hours per week")
    shop_id: Optional[int] = Field(default=None, foreign_key="shops.id", description="Assigned shop")
    manager_id: Optional[int] = Field(default=None, foreign_key="employees.id", description="Manager ID")
    
    # System Fields
    is_active: bool = Field(default=True, description="Is employee active in system")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    shop: Optional["Shop"] = Relationship(back_populates="employees")
    payroll_records: list["PayrollRecord"] = Relationship(back_populates="employee")
    manager: Optional["Employee"] = Relationship(
        back_populates="subordinates",
        sa_relationship_kwargs={"foreign_keys": "Employee.manager_id", "remote_side": "Employee.id"}
    )
    subordinates: list["Employee"] = Relationship(
        back_populates="manager",
        sa_relationship_kwargs={"foreign_keys": "Employee.manager_id"}
    )
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def annual_salary(self) -> Decimal:
        """Calculate annual salary"""
        return self.base_salary * 12
    
    def calculate_monthly_pay(self, hours_worked: Optional[Decimal] = None) -> Decimal:
        """Calculate monthly pay based on salary type"""
        if self.hourly_rate and hours_worked:
            # Hourly employee
            base_pay = self.hourly_rate * hours_worked
            if hours_worked > 160:  # Overtime calculation (40 hours/week * 4 weeks)
                overtime_hours = hours_worked - 160
                overtime_pay = overtime_hours * self.hourly_rate * (self.overtime_rate or 1.5)
                return base_pay + overtime_pay
            return base_pay
        else:
            # Salaried employee
            return self.base_salary
