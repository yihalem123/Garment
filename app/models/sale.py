"""
Sale models
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.shop import Shop
    from app.models.product import Product


class SaleStatus(str, Enum):
    """Sale status"""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    """Payment methods"""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"


class Sale(SQLModel, table=True):
    """Sale model"""
    __tablename__ = "sales"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    sale_number: str = Field(unique=True, index=True)
    shop_id: int = Field(foreign_key="shops.id")
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    total_amount: Decimal = Field(decimal_places=2)
    discount_amount: Decimal = Field(default=0, decimal_places=2)
    final_amount: Decimal = Field(decimal_places=2)
    status: SaleStatus = Field(default=SaleStatus.PENDING)
    sale_date: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    shop: "Shop" = Relationship(back_populates="sales")
    sale_lines: List["SaleLine"] = Relationship(back_populates="sale")
    payments: List["Payment"] = Relationship(back_populates="sale")


class SaleLine(SQLModel, table=True):
    """Sale line item model"""
    __tablename__ = "sale_lines"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    sale_id: int = Field(foreign_key="sales.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: Decimal = Field(decimal_places=3)
    unit_price: Decimal = Field(decimal_places=2)
    total_price: Decimal = Field(decimal_places=2)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    sale: Sale = Relationship(back_populates="sale_lines")
    product: Product = Relationship(back_populates="sale_lines")


class Payment(SQLModel, table=True):
    """Payment model"""
    __tablename__ = "payments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    sale_id: int = Field(foreign_key="sales.id")
    amount: Decimal = Field(decimal_places=2)
    payment_method: PaymentMethod
    payment_date: str
    reference: Optional[str] = None  # Transaction reference, check number, etc.
    notes: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    sale: Sale = Relationship(back_populates="payments")
