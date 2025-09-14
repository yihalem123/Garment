"""
Shop model
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.inventory import StockItem
    from app.models.sale import Sale
    from app.models.transfer import Transfer


class Shop(SQLModel, table=True):
    """Shop model"""
    __tablename__ = "shops"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    users: List["User"] = Relationship(back_populates="shop")
    stock_items: List["StockItem"] = Relationship(back_populates="shop")
    sales: List["Sale"] = Relationship(back_populates="shop")
    transfers_from: List["Transfer"] = Relationship(
        back_populates="from_shop",
        sa_relationship_kwargs={"foreign_keys": "Transfer.from_shop_id"}
    )
    transfers_to: List["Transfer"] = Relationship(
        back_populates="to_shop", 
        sa_relationship_kwargs={"foreign_keys": "Transfer.to_shop_id"}
    )
