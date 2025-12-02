"""
Inventory schemas
"""
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel


class StockItemResponse(BaseModel):
    """Stock item response schema"""
    id: int
    shop_id: int
    item_type: str
    product_id: Optional[int] = None
    raw_material_id: Optional[int] = None
    quantity: Decimal
    reserved_quantity: Decimal
    min_stock_level: Decimal
    available_quantity: Decimal  # quantity - reserved_quantity
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    raw_material_name: Optional[str] = None
    shop_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class StockMovementResponse(BaseModel):
    """Stock movement response schema"""
    id: int
    shop_id: int
    item_type: str
    product_id: Optional[int] = None
    raw_material_id: Optional[int] = None
    quantity: Decimal
    reason: str
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class StockAdjustmentRequest(BaseModel):
    """Stock adjustment request schema"""
    shop_id: int
    item_type: str
    product_id: Optional[int] = None
    raw_material_id: Optional[int] = None
    quantity: Decimal  # positive for additions, negative for deductions
    reason: str = "adjustment"
    notes: Optional[str] = None


class StockQueryParams(BaseModel):
    """Stock query parameters"""
    shop_id: Optional[int] = None
    item_type: Optional[str] = None
    product_id: Optional[int] = None
    raw_material_id: Optional[int] = None
    low_stock_only: bool = False
