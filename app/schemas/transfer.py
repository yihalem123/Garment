"""
Transfer schemas
"""
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel


class TransferLineCreate(BaseModel):
    """Transfer line creation schema"""
    product_id: int
    quantity: Decimal
    unit_cost: Decimal


class TransferLineResponse(BaseModel):
    """Transfer line response schema"""
    id: int
    transfer_id: int
    product_id: int
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    
    class Config:
        from_attributes = True


class TransferCreate(BaseModel):
    """Transfer creation schema"""
    transfer_number: str
    from_shop_id: int
    to_shop_id: int
    transfer_date: str
    notes: Optional[str] = None
    transfer_lines: List[TransferLineCreate]


class TransferResponse(BaseModel):
    """Transfer response schema"""
    id: int
    transfer_number: str
    from_shop_id: int
    to_shop_id: int
    status: str
    transfer_date: str
    received_date: Optional[str] = None
    notes: Optional[str] = None
    transfer_lines: List[TransferLineResponse]
    
    class Config:
        from_attributes = True
