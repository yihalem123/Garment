"""
Return model
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from decimal import Decimal
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.sale import Sale


class ReturnReason(str, Enum):
    """Return reasons"""
    DEFECTIVE = "defective"
    WRONG_SIZE = "wrong_size"
    CUSTOMER_CHANGE_MIND = "customer_change_mind"
    OTHER = "other"


class Return(SQLModel, table=True):
    """Return model"""
    __tablename__ = "returns"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    return_number: str = Field(unique=True, index=True)
    sale_id: Optional[int] = Field(default=None, foreign_key="sales.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: Decimal = Field(decimal_places=3)
    unit_price: Decimal = Field(decimal_places=2)
    total_amount: Decimal = Field(decimal_places=2)
    reason: ReturnReason
    notes: Optional[str] = None
    return_date: str
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    sale: Optional["Sale"] = Relationship()
