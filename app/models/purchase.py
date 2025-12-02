"""
Purchase models
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.product import RawMaterial


class PurchaseStatus(str, Enum):
    """Purchase status"""
    PENDING = "pending"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class Purchase(SQLModel, table=True):
    """Purchase model"""
    __tablename__ = "purchases"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field(unique=True, index=True)  # Auto-generated order ID
    supplier_name: str
    supplier_invoice: Optional[str] = None
    total_amount: Decimal = Field(decimal_places=2)
    status: PurchaseStatus = Field(default=PurchaseStatus.PENDING)
    purchase_date: str
    received_date: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    purchase_lines: List["PurchaseLine"] = Relationship(back_populates="purchase")


class PurchaseLine(SQLModel, table=True):
    """Purchase line item model"""
    __tablename__ = "purchase_lines"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    purchase_id: int = Field(foreign_key="purchases.id")
    raw_material_id: Optional[int] = Field(default=None, foreign_key="raw_materials.id")
    item_name: Optional[str] = None  # For custom items
    item_description: Optional[str] = None  # For custom items
    quantity: Decimal = Field(decimal_places=3)
    unit_price: Decimal = Field(decimal_places=2)
    total_price: Decimal = Field(decimal_places=2)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    purchase: "Purchase" = Relationship(back_populates="purchase_lines")
    raw_material: "RawMaterial" = Relationship(back_populates="purchase_lines")
