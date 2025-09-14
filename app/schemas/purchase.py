"""
Purchase schemas
"""
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel


class PurchaseLineCreate(BaseModel):
    """Purchase line creation schema"""
    raw_material_id: int
    quantity: Decimal
    unit_price: Decimal


class PurchaseLineResponse(BaseModel):
    """Purchase line response schema"""
    id: int
    purchase_id: int
    raw_material_id: int
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    
    class Config:
        from_attributes = True


class PurchaseCreate(BaseModel):
    """Purchase creation schema"""
    supplier_name: str
    supplier_invoice: Optional[str] = None
    purchase_date: str
    notes: Optional[str] = None
    purchase_lines: List[PurchaseLineCreate]


class PurchaseResponse(BaseModel):
    """Purchase response schema"""
    id: int
    supplier_name: str
    supplier_invoice: Optional[str] = None
    total_amount: Decimal
    status: str
    purchase_date: str
    received_date: Optional[str] = None
    notes: Optional[str] = None
    purchase_lines: List[PurchaseLineResponse]
    
    class Config:
        from_attributes = True
