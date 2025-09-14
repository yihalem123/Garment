"""
Shop schemas
"""
from typing import Optional
from pydantic import BaseModel


class ShopCreate(BaseModel):
    """Shop creation schema"""
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class ShopUpdate(BaseModel):
    """Shop update schema"""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class ShopResponse(BaseModel):
    """Shop response schema"""
    id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True
