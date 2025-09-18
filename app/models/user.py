"""
User model
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum
from decimal import Decimal

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.shop import Shop


class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    SHOP_MANAGER = "shop_manager"
    STAFF = "staff"


class User(SQLModel, table=True):
    """User model"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    role: UserRole = Field(default=UserRole.STAFF)
    is_active: bool = Field(default=True)
    shop_id: Optional[int] = Field(default=None, foreign_key="shops.id")
    
    # Salary and employment information
    salary: Optional[Decimal] = Field(default=None, description="Monthly salary")
    position: Optional[str] = Field(default=None, description="Job position/title")
    department: Optional[str] = Field(default=None, description="Department")
    hire_date: Optional[datetime] = Field(default=None, description="Date of hire")
    phone: Optional[str] = Field(default=None, description="Phone number")
    address: Optional[str] = Field(default=None, description="Address")
    
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    shop: Optional["Shop"] = Relationship(back_populates="users")
