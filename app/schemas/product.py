"""
Product schemas
"""
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel


class ProductCreate(BaseModel):
    """Product creation schema"""
    name: str
    description: Optional[str] = None
    sku: str
    category: Optional[str] = None
    unit_price: Decimal
    cost_price: Optional[Decimal] = None


class ProductUpdate(BaseModel):
    """Product update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    unit_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Product response schema"""
    id: int
    name: str
    description: Optional[str] = None
    sku: str
    category: Optional[str] = None
    unit_price: Decimal
    cost_price: Optional[Decimal] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class RawMaterialCreate(BaseModel):
    """Raw material creation schema"""
    name: str
    description: Optional[str] = None
    sku: str
    unit: str = "kg"
    unit_price: Decimal


class RawMaterialUpdate(BaseModel):
    """Raw material update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    unit: Optional[str] = None
    unit_price: Optional[Decimal] = None
    is_active: Optional[bool] = None


class RawMaterialResponse(BaseModel):
    """Raw material response schema"""
    id: int
    name: str
    description: Optional[str] = None
    sku: str
    unit: str
    unit_price: Decimal
    is_active: bool
    
    class Config:
        from_attributes = True


class FabricRuleCreate(BaseModel):
    """Fabric rule creation schema"""
    product_id: int
    raw_material_id: int
    consumption_per_unit: Decimal


class FabricRuleResponse(BaseModel):
    """Fabric rule response schema"""
    id: int
    product_id: int
    raw_material_id: int
    consumption_per_unit: Decimal
    
    class Config:
        from_attributes = True
