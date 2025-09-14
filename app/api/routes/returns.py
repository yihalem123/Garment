"""
Returns routes
"""
from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.session import get_session
from app.models import (
    Return, StockItem, StockMovement,
    User, ItemType, MovementReason, ReturnReason
)
from app.schemas.return_model import ReturnCreate, ReturnResponse
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ReturnResponse])
async def get_returns(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all returns
    
    Example request:
    ```
    curl -X GET "http://localhost:8000/returns/" \
         -H "Authorization: Bearer <token>"
    ```
    """
    statement = select(Return).offset(skip).limit(limit).order_by(Return.created_at.desc())
    returns = await db.exec(statement)
    return returns.all()


@router.get("/{return_id}", response_model=ReturnResponse)
async def get_return(
    return_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific return by ID
    """
    statement = select(Return).where(Return.id == return_id)
    return_item = await db.exec(statement)
    return_item = return_item.first()
    
    if not return_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Return not found"
        )
    
    return return_item


@router.post("/", response_model=ReturnResponse)
async def create_return(
    return_data: ReturnCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new return and adjust stock
    
    This endpoint:
    1. Creates the return record
    2. Adds product stock back to inventory
    3. Creates stock movement record
    4. All operations are wrapped in a database transaction
    
    Example request:
    ```json
    {
        "return_number": "RET-2024-001",
        "sale_id": 1,
        "product_id": 1,
        "quantity": 1.0,
        "unit_price": 25.00,
        "reason": "defective",
        "notes": "Product was damaged",
        "return_date": "2024-01-16"
    }
    ```
    """
    async with db.begin():
        # Check if return number already exists
        statement = select(Return).where(Return.return_number == return_data.return_number)
        existing_return = await db.exec(statement)
        if existing_return.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return with this number already exists"
            )
        
        # Calculate total amount
        total_amount = return_data.quantity * return_data.unit_price
        
        # Create return
        db_return = Return(
            return_number=return_data.return_number,
            sale_id=return_data.sale_id,
            product_id=return_data.product_id,
            quantity=return_data.quantity,
            unit_price=return_data.unit_price,
            total_amount=total_amount,
            reason=ReturnReason(return_data.reason),
            notes=return_data.notes,
            return_date=return_data.return_date
        )
        
        db.add(db_return)
        await db.flush()  # Get the ID
        
        # Determine shop_id - use shop from sale if available, otherwise default to shop 1
        shop_id = 1  # Default to main warehouse
        if return_data.sale_id:
            from app.models import Sale
            statement = select(Sale).where(Sale.id == return_data.sale_id)
            sale = await db.exec(statement)
            sale = sale.first()
            if sale:
                shop_id = sale.shop_id
        
        # Find or create stock item
        statement = select(StockItem).where(
            and_(
                StockItem.shop_id == shop_id,
                StockItem.product_id == return_data.product_id,
                StockItem.item_type == ItemType.PRODUCT
            )
        )
        stock_item = await db.exec(statement)
        stock_item = stock_item.first()
        
        if not stock_item:
            # Create new stock item
            stock_item = StockItem(
                shop_id=shop_id,
                item_type=ItemType.PRODUCT,
                product_id=return_data.product_id,
                quantity=return_data.quantity,
                reserved_quantity=Decimal('0'),
                min_stock_level=Decimal('10')
            )
            db.add(stock_item)
        else:
            # Add to existing stock
            stock_item.quantity += return_data.quantity
        
        # Create stock movement
        stock_movement = StockMovement(
            shop_id=shop_id,
            item_type=ItemType.PRODUCT,
            product_id=return_data.product_id,
            quantity=return_data.quantity,
            reason=MovementReason.RETURN,
            reference_id=db_return.id,
            reference_type="return"
        )
        db.add(stock_movement)
        
        await db.commit()
        await db.refresh(db_return)
    
    return db_return
