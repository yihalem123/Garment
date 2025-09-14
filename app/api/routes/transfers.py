"""
Transfer routes
"""
from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.models import (
    Transfer, TransferLine, StockItem, StockMovement,
    User, ItemType, MovementReason, TransferStatus
)
from app.schemas.transfer import TransferCreate, TransferResponse
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[TransferResponse])
async def get_transfers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all transfers
    
    Example request:
    ```
    curl -X GET "http://localhost:8000/transfers/" \
         -H "Authorization: Bearer <token>"
    ```
    """
    statement = select(Transfer).options(
        selectinload(Transfer.transfer_lines)
    ).offset(skip).limit(limit).order_by(Transfer.created_at.desc())
    result = await db.execute(statement)
    return result.scalars().all()


@router.get("/{transfer_id}", response_model=TransferResponse)
async def get_transfer(
    transfer_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific transfer by ID
    """
    statement = select(Transfer).options(
        selectinload(Transfer.transfer_lines)
    ).where(Transfer.id == transfer_id)
    result = await db.execute(statement)
    transfer = result.scalar_one_or_none()
    
    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )
    
    return transfer


@router.post("/", response_model=TransferResponse)
async def create_transfer(
    transfer_data: TransferCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new transfer
    
    This endpoint creates a transfer and reserves stock at the source shop.
    Use the receive endpoint to complete the transfer.
    
    Example request:
    ```json
    {
        "transfer_number": "TR-2024-001",
        "from_shop_id": 1,
        "to_shop_id": 2,
        "transfer_date": "2024-01-15",
        "notes": "Stock transfer to branch",
        "transfer_lines": [
            {
                "product_id": 1,
                "quantity": 50.0,
                "unit_cost": 25.00
            }
        ]
    }
    ```
    """
    # Check if transfer number already exists
    statement = select(Transfer).where(Transfer.transfer_number == transfer_data.transfer_number)
    result = await db.execute(statement)
    existing_transfer = result.scalar_one_or_none()
    if existing_transfer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer with this number already exists"
        )
    
    # Validate stock availability at source shop
    for line_data in transfer_data.transfer_lines:
        statement = select(StockItem).where(
            and_(
                StockItem.shop_id == transfer_data.from_shop_id,
                StockItem.product_id == line_data.product_id,
                StockItem.item_type == ItemType.PRODUCT
            )
        )
        result = await db.execute(statement)
        stock_item = result.scalar_one_or_none()
        # stock_item is already a single object from scalar_one_or_none()
        
        if not stock_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No stock found for product ID {line_data.product_id} at source shop"
            )
        
        available_quantity = stock_item.quantity - stock_item.reserved_quantity
        if available_quantity < line_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Insufficient stock for product ID {line_data.product_id}. "
                       f"Available: {available_quantity}, Required: {line_data.quantity}"
            )
    
    # Create transfer
    db_transfer = Transfer(
        transfer_number=transfer_data.transfer_number,
        from_shop_id=transfer_data.from_shop_id,
        to_shop_id=transfer_data.to_shop_id,
        transfer_date=transfer_data.transfer_date,
        notes=transfer_data.notes,
        status=TransferStatus.PENDING
    )
    
    db.add(db_transfer)
    await db.flush()  # Get the ID
    
    # Create transfer lines and reserve stock
    for line_data in transfer_data.transfer_lines:
        # Create transfer line
        transfer_line = TransferLine(
            transfer_id=db_transfer.id,
            product_id=line_data.product_id,
            quantity=line_data.quantity,
            unit_cost=line_data.unit_cost,
            total_cost=line_data.quantity * line_data.unit_cost
        )
        db.add(transfer_line)
        
        # Reserve stock at source shop
        statement = select(StockItem).where(
            and_(
                StockItem.shop_id == transfer_data.from_shop_id,
                StockItem.product_id == line_data.product_id,
                StockItem.item_type == ItemType.PRODUCT
            )
        )
        result = await db.execute(statement)
        stock_item = result.scalar_one_or_none()
        # stock_item is already a single object from scalar_one_or_none()
        
        stock_item.reserved_quantity += line_data.quantity
        
        # Create stock movement for reservation
        stock_movement = StockMovement(
            shop_id=transfer_data.from_shop_id,
            item_type=ItemType.PRODUCT,
            product_id=line_data.product_id,
            quantity=-line_data.quantity,  # Negative for deduction
            reason=MovementReason.TRANSFER_OUT,
            reference_id=db_transfer.id,
            reference_type="transfer"
        )
        db.add(stock_movement)
    
    await db.commit()
    await db.refresh(db_transfer)
    
    # Eager load relationships for response serialization
    statement = select(Transfer).options(
        selectinload(Transfer.transfer_lines)
    ).where(Transfer.id == db_transfer.id)
    result = await db.execute(statement)
    transfer_with_relations = result.scalar_one()
    
    return transfer_with_relations


@router.post("/{transfer_id}/receive", response_model=TransferResponse)
async def receive_transfer(
    transfer_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Receive a transfer
    
    This endpoint:
    1. Validates the transfer exists and is pending
    2. Deducts reserved stock from source shop
    3. Adds stock to destination shop
    4. Creates stock movement records
    5. Updates transfer status
    
    Example request:
    ```
    curl -X POST "http://localhost:8000/transfers/1/receive" \
         -H "Authorization: Bearer <token>"
    ```
    """
    async with db.begin():
        # Get transfer
        statement = select(Transfer).where(Transfer.id == transfer_id)
        result = await db.execute(statement)
        transfer = result.scalar_one_or_none()
        # transfer is already a single object from scalar_one_or_none()
        
        if not transfer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found"
            )
        
        if transfer.status != TransferStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transfer is not in pending status"
            )
        
        # Get transfer lines
        statement = select(TransferLine).where(TransferLine.transfer_id == transfer_id)
        result = await db.execute(statement)
        transfer_lines = result.scalars().all()
        
        # Process each transfer line
        for line in transfer_lines:
            # Deduct reserved stock from source shop
            statement = select(StockItem).where(
                and_(
                    StockItem.shop_id == transfer.from_shop_id,
                    StockItem.product_id == line.product_id,
                    StockItem.item_type == ItemType.PRODUCT
                )
            )
            result = await db.execute(statement)
            source_stock_item = result.scalar_one_or_none()
            # source_stock_item is already a single object from scalar_one_or_none()
            
            source_stock_item.quantity -= line.quantity
            source_stock_item.reserved_quantity -= line.quantity
            
            # Add stock to destination shop
            statement = select(StockItem).where(
                and_(
                    StockItem.shop_id == transfer.to_shop_id,
                    StockItem.product_id == line.product_id,
                    StockItem.item_type == ItemType.PRODUCT
                )
            )
            result = await db.execute(statement)
            dest_stock_item = result.scalar_one_or_none()
            # dest_stock_item is already a single object from scalar_one_or_none()
            
            if not dest_stock_item:
                # Create new stock item at destination
                dest_stock_item = StockItem(
                    shop_id=transfer.to_shop_id,
                    item_type=ItemType.PRODUCT,
                    product_id=line.product_id,
                    quantity=line.quantity,
                    reserved_quantity=Decimal('0'),
                    min_stock_level=Decimal('10')
                )
                db.add(dest_stock_item)
            else:
                dest_stock_item.quantity += line.quantity
            
            # Create stock movement for destination
            stock_movement = StockMovement(
                shop_id=transfer.to_shop_id,
                item_type=ItemType.PRODUCT,
                product_id=line.product_id,
                quantity=line.quantity,
                reason=MovementReason.TRANSFER_IN,
                reference_id=transfer_id,
                reference_type="transfer"
            )
            db.add(stock_movement)
        
        # Update transfer status
        transfer.status = TransferStatus.RECEIVED
        
        await db.commit()
        await db.refresh(transfer)
    
    return transfer
