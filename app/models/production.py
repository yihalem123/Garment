"""
Production models
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.raw_material import RawMaterial


class ProductionStatus(str, Enum):
    """Production status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductionRun(SQLModel, table=True):
    """Production run model"""
    __tablename__ = "production_runs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    run_number: str = Field(unique=True, index=True)
    status: ProductionStatus = Field(default=ProductionStatus.PLANNED)
    planned_quantity: Decimal = Field(decimal_places=3)
    actual_quantity: Optional[Decimal] = Field(default=None, decimal_places=3)
    labor_cost: Decimal = Field(default=0, decimal_places=2)
    overhead_cost: Decimal = Field(default=0, decimal_places=2)
    total_cost: Optional[Decimal] = Field(default=None, decimal_places=2)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    production_lines: List["ProductionLine"] = Relationship(back_populates="production_run")
    production_consumptions: List["ProductionConsumption"] = Relationship(back_populates="production_run")


class ProductionLine(SQLModel, table=True):
    """Production line item model"""
    __tablename__ = "production_lines"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    production_run_id: int = Field(foreign_key="production_runs.id")
    product_id: int = Field(foreign_key="products.id")
    planned_quantity: Decimal = Field(decimal_places=3)
    actual_quantity: Optional[Decimal] = Field(default=None, decimal_places=3)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    production_run: ProductionRun = Relationship(back_populates="production_lines")
    product: Product = Relationship(back_populates="production_lines")


class ProductionConsumption(SQLModel, table=True):
    """Production consumption model"""
    __tablename__ = "production_consumptions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    production_run_id: int = Field(foreign_key="production_runs.id")
    raw_material_id: int = Field(foreign_key="raw_materials.id")
    planned_consumption: Decimal = Field(decimal_places=3)
    actual_consumption: Optional[Decimal] = Field(default=None, decimal_places=3)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    production_run: ProductionRun = Relationship(back_populates="production_consumptions")
    raw_material: RawMaterial = Relationship(back_populates="production_consumptions")
