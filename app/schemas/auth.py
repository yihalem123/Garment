"""
Authentication schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    email: Optional[str] = None


class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    password: str
    full_name: str
    role: str = "staff"
    shop_id: Optional[int] = None


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    shop_id: Optional[int] = None
    
    class Config:
        from_attributes = True
