"""
Product and Raw Material models
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.inventory import StockItem
    from app.models.purchase import PurchaseLine
    from app.models.production import ProductionLine, ProductionConsumption
    from app.models.sale import SaleLine
    from app.models.fabric_rule import FabricRule


class Product(SQLModel, table=True):
    """Product model"""
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    sku: str = Field(unique=True, index=True)
    category: Optional[str] = None
    unit_price: Decimal = Field(decimal_places=2)
    cost_price: Optional[Decimal] = Field(default=None, decimal_places=2)
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    stock_items: List["StockItem"] = Relationship(back_populates="product")
    production_lines: List["ProductionLine"] = Relationship(back_populates="product")
    sale_lines: List["SaleLine"] = Relationship(back_populates="product")
    fabric_rules: List["FabricRule"] = Relationship(back_populates="product")


class RawMaterial(SQLModel, table=True):
    """Raw Material model"""
    __tablename__ = "raw_materials"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    sku: str = Field(unique=True, index=True)
    unit: str = Field(default="kg")  # kg, meters, pieces, etc.
    unit_price: Decimal = Field(decimal_places=2)
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    stock_items: List["StockItem"] = Relationship(back_populates="raw_material")
    purchase_lines: List["PurchaseLine"] = Relationship(back_populates="raw_material")
    production_consumptions: List["ProductionConsumption"] = Relationship(back_populates="raw_material")
    fabric_rules: List["FabricRule"] = Relationship(back_populates="raw_material")


class FabricRule(SQLModel, table=True):
    """Fabric consumption rules for production"""
    __tablename__ = "fabric_rules"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id")
    raw_material_id: int = Field(foreign_key="raw_materials.id")
    consumption_per_unit: Decimal = Field(decimal_places=3)  # e.g., 2.5 kg per shirt
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    product: Product = Relationship(back_populates="fabric_rules")
    raw_material: RawMaterial = Relationship(back_populates="fabric_rules")
