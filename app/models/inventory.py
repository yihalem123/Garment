"""
Inventory models
"""
from datetime import datetime`nfrom typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.shop import Shop
    from app.models.product import Product, RawMaterial


class ItemType(str, Enum):
    """Stock item types"""
    PRODUCT = "product"
    RAW_MATERIAL = "raw_material"


class MovementReason(str, Enum):
    """Stock movement reasons"""
    PURCHASE = "purchase"
    PRODUCTION_ADD = "production_add"
    PRODUCTION_CONSUME = "production_consume"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    SALE = "sale"
    RETURN = "return"
    ADJUSTMENT = "adjustment"


class StockItem(SQLModel, table=True):
    """Stock item model"""
    __tablename__ = "stock_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    shop_id: int = Field(foreign_key="shops.id")
    item_type: ItemType
    product_id: Optional[int] = Field(default=None, foreign_key="products.id")
    raw_material_id: Optional[int] = Field(default=None, foreign_key="raw_materials.id")
    quantity: Decimal = Field(decimal_places=3)
    reserved_quantity: Decimal = Field(default=0, decimal_places=3)
    min_stock_level: Decimal = Field(default=0, decimal_places=3)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    shop: "Shop" = Relationship(back_populates="stock_items")
    product: Optional["Product"] = Relationship(back_populates="stock_items")
    raw_material: Optional["RawMaterial"] = Relationship(back_populates="stock_items")


class StockMovement(SQLModel, table=True):
    """Stock movement model"""
    __tablename__ = "stock_movements"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    shop_id: int = Field(foreign_key="shops.id")
    item_type: ItemType
    product_id: Optional[int] = Field(default=None, foreign_key="products.id")
    raw_material_id: Optional[int] = Field(default=None, foreign_key="raw_materials.id")
    quantity: Decimal = Field(decimal_places=3)  # positive for additions, negative for deductions
    reason: MovementReason
    reference_id: Optional[int] = None  # ID of related record (purchase, sale, etc.)
    reference_type: Optional[str] = None  # Type of related record
    notes: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    shop: "Shop" = Relationship()
    product: Optional["Product"] = Relationship()
    raw_material: Optional["RawMaterial"] = Relationship()
