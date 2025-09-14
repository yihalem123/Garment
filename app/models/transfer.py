"""
Transfer models
"""
from datetime import datetime`nfrom typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.shop import Shop
    from app.models.product import Product


class TransferStatus(str, Enum):
    """Transfer status"""
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class Transfer(SQLModel, table=True):
    """Transfer model"""
    __tablename__ = "transfers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    transfer_number: str = Field(unique=True, index=True)
    from_shop_id: int = Field(foreign_key="shops.id")
    to_shop_id: int = Field(foreign_key="shops.id")
    status: TransferStatus = Field(default=TransferStatus.PENDING)
    transfer_date: str
    received_date: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    from_shop: "Shop" = Relationship(
        back_populates="transfers_from",
        sa_relationship_kwargs={"foreign_keys": "Transfer.from_shop_id"}
    )
    to_shop: "Shop" = Relationship(
        back_populates="transfers_to",
        sa_relationship_kwargs={"foreign_keys": "Transfer.to_shop_id"}
    )
    transfer_lines: List["TransferLine"] = Relationship(back_populates="transfer")


class TransferLine(SQLModel, table=True):
    """Transfer line item model"""
    __tablename__ = "transfer_lines"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    transfer_id: int = Field(foreign_key="transfers.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: Decimal = Field(decimal_places=3)
    unit_cost: Decimal = Field(decimal_places=2)
    total_cost: Decimal = Field(decimal_places=2)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    # Relationships
    transfer: Transfer = Relationship(back_populates="transfer_lines")
    product: Product = Relationship()
