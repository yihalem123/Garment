"""
Sale schemas
"""
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel


class SaleLineCreate(BaseModel):
    """Sale line creation schema"""
    product_id: int
    quantity: Decimal
    unit_price: Decimal


class SaleLineResponse(BaseModel):
    """Sale line response schema"""
    id: int
    sale_id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    
    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    """Payment creation schema"""
    amount: Decimal
    payment_method: str  # "cash" or "bank_transfer"
    payment_date: str
    reference: Optional[str] = None  # For bank transfers: transaction reference, for cash: receipt number
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    """Payment response schema"""
    id: int
    sale_id: int
    amount: Decimal
    payment_method: str  # "cash" or "bank_transfer"
    payment_date: str
    reference: Optional[str] = None  # Transaction reference or receipt number
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class SaleCreate(BaseModel):
    """Sale creation schema"""
    sale_number: str
    shop_id: int
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    discount_amount: Decimal = 0
    sale_date: str
    notes: Optional[str] = None
    sale_lines: List[SaleLineCreate]
    payments: Optional[List[PaymentCreate]] = None


class SaleResponse(BaseModel):
    """Sale response schema"""
    id: int
    sale_number: str
    shop_id: int
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    total_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    status: str
    sale_date: str
    notes: Optional[str] = None
    sale_lines: List[SaleLineResponse]
    payments: List[PaymentResponse]
    
    class Config:
        from_attributes = True
