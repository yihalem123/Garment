"""
Return schemas
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class ReturnCreate(BaseModel):
    """Return creation schema"""
    return_number: str
    sale_id: Optional[int] = None
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    reason: str
    notes: Optional[str] = None
    return_date: str


class ReturnResponse(BaseModel):
    """Return response schema"""
    id: int
    return_number: str
    sale_id: Optional[int] = None
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal
    reason: str
    notes: Optional[str] = None
    return_date: str
    
    class Config:
        from_attributes = True
