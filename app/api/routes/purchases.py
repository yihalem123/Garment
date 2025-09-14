"""
Purchase routes
"""
from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.models import (
    Purchase, PurchaseLine, StockItem, StockMovement, 
    User, ItemType, MovementReason, PurchaseStatus
)
from app.schemas.purchase import PurchaseCreate, PurchaseResponse
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[PurchaseResponse])
async def get_purchases(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all purchases
    
    Example request:
    ```
    curl -X GET "http://localhost:8000/purchases/" \
         -H "Authorization: Bearer <token>"
    ```
    """
    statement = select(Purchase).options(
        selectinload(Purchase.purchase_lines)
    ).offset(skip).limit(limit).order_by(Purchase.created_at.desc())
    result = await db.execute(statement)
    return result.scalars().all()


@router.get("/{purchase_id}", response_model=PurchaseResponse)
async def get_purchase(
    purchase_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific purchase by ID
    """
    statement = select(Purchase).options(
        selectinload(Purchase.purchase_lines)
    ).where(Purchase.id == purchase_id)
    result = await db.execute(statement)
    purchase = result.scalar_one_or_none()
    
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase not found"
        )
    
    return purchase


@router.post("/", response_model=PurchaseResponse)
async def create_purchase(
    purchase_data: PurchaseCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new purchase and update stock
    
    This endpoint:
    1. Creates the purchase and purchase lines
    2. Updates raw material stock quantities
    3. Creates stock movement records
    4. All operations are wrapped in a database transaction
    
    Example request:
    ```json
    {
        "supplier_name": "Fabric Supplier Co.",
        "supplier_invoice": "INV-001",
        "purchase_date": "2024-01-15",
        "notes": "Monthly fabric order",
        "purchase_lines": [
            {
                "raw_material_id": 1,
                "quantity": 100.0,
                "unit_price": 5.00
            },
            {
                "raw_material_id": 2,
                "quantity": 50.0,
                "unit_price": 3.00
            }
        ]
    }
    ```
    """
    # Transaction handled by session dependency
    # Calculate total amount
    total_amount = sum(
        line.quantity * line.unit_price 
        for line in purchase_data.purchase_lines
    )
    
    # Create purchase
    db_purchase = Purchase(
        supplier_name=purchase_data.supplier_name,
        supplier_invoice=purchase_data.supplier_invoice,
        total_amount=total_amount,
        purchase_date=purchase_data.purchase_date,
        notes=purchase_data.notes,
        status=PurchaseStatus.RECEIVED  # Assume received immediately
    )
    
    db.add(db_purchase)
    await db.flush()  # Get the ID
    
    # Create purchase lines and update stock
    for line_data in purchase_data.purchase_lines:
        # Create purchase line
        purchase_line = PurchaseLine(
            purchase_id=db_purchase.id,
            raw_material_id=line_data.raw_material_id,
            quantity=line_data.quantity,
            unit_price=line_data.unit_price,
            total_price=line_data.quantity * line_data.unit_price
        )
        db.add(purchase_line)
        
        # Find or create stock item
        statement = select(StockItem).where(
            StockItem.raw_material_id == line_data.raw_material_id,
            StockItem.item_type == ItemType.RAW_MATERIAL
        )
        result = await db.execute(statement)
        stock_item = result.scalar_one_or_none()
        
        if not stock_item:
            # Create new stock item (assuming shop_id=1 for main warehouse)
            stock_item = StockItem(
                shop_id=1,  # Main warehouse
                item_type=ItemType.RAW_MATERIAL,
                raw_material_id=line_data.raw_material_id,
                quantity=line_data.quantity,
                reserved_quantity=Decimal('0'),
                min_stock_level=Decimal('10')
            )
            db.add(stock_item)
        else:
            # Update existing stock
            stock_item.quantity += line_data.quantity
        
        # Create stock movement
        stock_movement = StockMovement(
            shop_id=1,  # Main warehouse
            item_type=ItemType.RAW_MATERIAL,
            raw_material_id=line_data.raw_material_id,
            quantity=line_data.quantity,
            reason=MovementReason.PURCHASE,
            reference_id=db_purchase.id,
            reference_type="purchase"
        )
        db.add(stock_movement)
    
    await db.commit()
    await db.refresh(db_purchase)
    
    # Eager load relationships for response serialization
    statement = select(Purchase).options(
        selectinload(Purchase.purchase_lines)
    ).where(Purchase.id == db_purchase.id)
    result = await db.execute(statement)
    purchase_with_relations = result.scalar_one()
    
    return purchase_with_relations
