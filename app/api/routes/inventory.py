"""
Inventory routes
"""
from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.session import get_session
from app.models import StockItem, StockMovement, User, ItemType, MovementReason
from app.schemas.inventory import (
    StockItemResponse, StockMovementResponse, 
    StockAdjustmentRequest, StockQueryParams
)
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/stocks", response_model=List[StockItemResponse])
async def get_stocks(
    shop_id: Optional[int] = Query(None),
    item_type: Optional[str] = Query(None),
    product_id: Optional[int] = Query(None),
    raw_material_id: Optional[int] = Query(None),
    low_stock_only: bool = Query(False),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get stock items with filtering
    
    Example request:
    ```
    curl -X GET "http://localhost:8000/inventory/stocks?shop_id=1&item_type=product" \
         -H "Authorization: Bearer <token>"
    ```
    """
    statement = select(StockItem)
    
    conditions = []
    if shop_id:
        conditions.append(StockItem.shop_id == shop_id)
    if item_type:
        conditions.append(StockItem.item_type == item_type)
    if product_id:
        conditions.append(StockItem.product_id == product_id)
    if raw_material_id:
        conditions.append(StockItem.raw_material_id == raw_material_id)
    if low_stock_only:
        conditions.append(StockItem.quantity <= StockItem.min_stock_level)
    
    if conditions:
        statement = statement.where(and_(*conditions))
    
    stock_items = await db.exec(statement)
    results = stock_items.all()
    
    # Add available_quantity field
    response_items = []
    for item in results:
        item_dict = item.dict()
        item_dict["available_quantity"] = item.quantity - item.reserved_quantity
        response_items.append(StockItemResponse(**item_dict))
    
    return response_items


@router.post("/stocks/adjust")
async def adjust_stock(
    adjustment: StockAdjustmentRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Adjust stock quantity
    
    Example request:
    ```json
    {
        "shop_id": 1,
        "item_type": "product",
        "product_id": 1,
        "quantity": 10.0,
        "reason": "adjustment",
        "notes": "Stock count correction"
    }
    ```
    """
    async with db.begin():
        # Find existing stock item
        conditions = [
            StockItem.shop_id == adjustment.shop_id,
            StockItem.item_type == adjustment.item_type
        ]
        
        if adjustment.product_id:
            conditions.append(StockItem.product_id == adjustment.product_id)
        if adjustment.raw_material_id:
            conditions.append(StockItem.raw_material_id == adjustment.raw_material_id)
        
        statement = select(StockItem).where(and_(*conditions))
        stock_item = await db.exec(statement)
        stock_item = stock_item.first()
        
        if not stock_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock item not found"
            )
        
        # Update stock quantity
        stock_item.quantity += adjustment.quantity
        
        # Create stock movement record
        stock_movement = StockMovement(
            shop_id=adjustment.shop_id,
            item_type=adjustment.item_type,
            product_id=adjustment.product_id,
            raw_material_id=adjustment.raw_material_id,
            quantity=adjustment.quantity,
            reason=MovementReason(adjustment.reason),
            notes=adjustment.notes
        )
        
        db.add(stock_movement)
        await db.commit()
    
    return {"message": "Stock adjusted successfully"}


@router.get("/stock-movements", response_model=List[StockMovementResponse])
async def get_stock_movements(
    shop_id: Optional[int] = Query(None),
    item_type: Optional[str] = Query(None),
    product_id: Optional[int] = Query(None),
    raw_material_id: Optional[int] = Query(None),
    reason: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get stock movements with filtering
    
    Example request:
    ```
    curl -X GET "http://localhost:8000/inventory/stock-movements?shop_id=1&reason=purchase" \
         -H "Authorization: Bearer <token>"
    ```
    """
    statement = select(StockMovement)
    
    conditions = []
    if shop_id:
        conditions.append(StockMovement.shop_id == shop_id)
    if item_type:
        conditions.append(StockMovement.item_type == item_type)
    if product_id:
        conditions.append(StockMovement.product_id == product_id)
    if raw_material_id:
        conditions.append(StockMovement.raw_material_id == raw_material_id)
    if reason:
        conditions.append(StockMovement.reason == reason)
    
    if conditions:
        statement = statement.where(and_(*conditions))
    
    statement = statement.order_by(StockMovement.created_at.desc())
    statement = statement.offset(skip).limit(limit)
    
    stock_movements = await db.exec(statement)
    return stock_movements.all()
