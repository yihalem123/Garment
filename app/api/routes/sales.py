"""
Sales routes
"""
from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.models import (
    Sale, SaleLine, Payment, StockItem, StockMovement,
    User, ItemType, MovementReason, SaleStatus, PaymentMethod
)
from app.schemas.sale import SaleCreate, SaleResponse
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[SaleResponse])
async def get_sales(
    skip: int = 0,
    limit: int = 100,
    shop_id: int = None,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all sales with optional shop filtering
    
    For shop managers, automatically filters by their shop_id.
    For admins, allows filtering by any shop_id.
    
    Example request:
    ```
    curl -X GET "http://localhost:8000/sales/?shop_id=1" \
         -H "Authorization: Bearer <token>"
    ```
    """
    statement = select(Sale).options(
        selectinload(Sale.sale_lines),
        selectinload(Sale.payments)
    )
    
    # Shop manager role-based filtering
    if current_user.role == "shop_manager":
        # Shop managers can only see their shop's sales
        if current_user.shop_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Shop manager must be assigned to a shop"
            )
        statement = statement.where(Sale.shop_id == current_user.shop_id)
    elif current_user.role == "admin":
        # Admins can filter by any shop or see all
        if shop_id:
            statement = statement.where(Sale.shop_id == shop_id)
    else:
        # Staff can only see their shop's sales if assigned
        if current_user.shop_id:
            statement = statement.where(Sale.shop_id == current_user.shop_id)
        elif shop_id:
            statement = statement.where(Sale.shop_id == shop_id)
    
    statement = statement.offset(skip).limit(limit).order_by(Sale.created_at.desc())
    result = await db.execute(statement)
    return result.scalars().all()


@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific sale by ID
    """
    statement = select(Sale).options(
        selectinload(Sale.sale_lines),
        selectinload(Sale.payments)
    ).where(Sale.id == sale_id)
    result = await db.execute(statement)
    sale = result.scalar_one_or_none()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found"
        )
    
    return sale


@router.post("/", response_model=SaleResponse)
async def create_sale(
    sale_data: SaleCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new sale with atomic stock updates
    
    For shop managers, automatically uses their shop_id.
    For admins, allows creating sales for any shop.
    
    This endpoint:
    1. Validates stock availability
    2. Creates sale and sale lines
    3. Deducts product stock
    4. Creates stock movement records
    5. Records payments if provided
    6. All operations are wrapped in a database transaction
    
    Returns 409 Conflict if insufficient stock is available.
    
    Example request:
    ```json
    {
        "sale_number": "SALE-2024-001",
        "shop_id": 1,
        "customer_name": "John Doe",
        "customer_phone": "+1234567890",
        "discount_amount": 10.00,
        "sale_date": "2024-01-15",
        "notes": "Customer purchase",
        "sale_lines": [
            {
                "product_id": 1,
                "quantity": 2.0,
                "unit_price": 25.00
            }
        ],
        "payments": [
            {
                "amount": 40.00,
                "payment_method": "cash",
                "payment_date": "2024-01-15",
                "reference": "RCP-001",
                "notes": "Cash payment received"
            }
        ]
    }
    ```
    """
    # Shop manager role-based restrictions
    if current_user.role == "shop_manager":
        # Shop managers can only create sales for their shop
        if current_user.shop_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Shop manager must be assigned to a shop"
            )
        # Override shop_id with the manager's shop
        sale_data.shop_id = current_user.shop_id
    elif current_user.role == "staff":
        # Staff can only create sales for their assigned shop
        if current_user.shop_id:
            sale_data.shop_id = current_user.shop_id
        elif not sale_data.shop_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff must be assigned to a shop or specify shop_id"
            )
    
    # Check if sale number already exists
    statement = select(Sale).where(Sale.sale_number == sale_data.sale_number)
    result = await db.execute(statement)
    existing_sale = result.scalar_one_or_none()
    if existing_sale:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sale with this number already exists"
        )
    
    # Calculate total amount
    total_amount = sum(
        line.quantity * line.unit_price 
        for line in sale_data.sale_lines
    )
    final_amount = total_amount - sale_data.discount_amount
    
    # Validate stock availability
    for line_data in sale_data.sale_lines:
        statement = select(StockItem).where(
            and_(
                StockItem.shop_id == sale_data.shop_id,
                StockItem.product_id == line_data.product_id,
                StockItem.item_type == ItemType.PRODUCT
            )
        )
        result = await db.execute(statement)
        stock_item = result.scalar_one_or_none()
        # stock_item is already a single object from scalar_one_or_none()
        
        if not stock_item:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No stock found for product ID {line_data.product_id} at shop {sale_data.shop_id}"
            )
        
        available_quantity = stock_item.quantity - stock_item.reserved_quantity
        if available_quantity < line_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Insufficient stock for product ID {line_data.product_id}. "
                       f"Available: {available_quantity}, Required: {line_data.quantity}"
            )
    
    # Create sale
    db_sale = Sale(
        sale_number=sale_data.sale_number,
        shop_id=sale_data.shop_id,
        customer_name=sale_data.customer_name,
        customer_phone=sale_data.customer_phone,
        total_amount=total_amount,
        discount_amount=sale_data.discount_amount,
        final_amount=final_amount,
        sale_date=sale_data.sale_date,
        notes=sale_data.notes,
        status=SaleStatus.COMPLETED
    )
    
    db.add(db_sale)
    await db.flush()  # Get the ID
    
    # Create sale lines and update stock
    for line_data in sale_data.sale_lines:
        # Create sale line
        sale_line = SaleLine(
            sale_id=db_sale.id,
            product_id=line_data.product_id,
            quantity=line_data.quantity,
            unit_price=line_data.unit_price,
            total_price=line_data.quantity * line_data.unit_price
        )
        db.add(sale_line)
        
        # Deduct stock
        statement = select(StockItem).where(
            and_(
                StockItem.shop_id == sale_data.shop_id,
                StockItem.product_id == line_data.product_id,
                StockItem.item_type == ItemType.PRODUCT
            )
        )
        result = await db.execute(statement)
        stock_item = result.scalar_one_or_none()
        # stock_item is already a single object from scalar_one_or_none()
        
        stock_item.quantity -= line_data.quantity
        
        # Create stock movement
        stock_movement = StockMovement(
            shop_id=sale_data.shop_id,
            item_type=ItemType.PRODUCT,
            product_id=line_data.product_id,
            quantity=-line_data.quantity,  # Negative for deduction
            reason=MovementReason.SALE,
            reference_id=db_sale.id,
            reference_type="sale"
        )
        db.add(stock_movement)
    
    # Create payments if provided
    # Note: Payment system supports only cash and bank transfers
    # No POS integration - all payment details are text-based entries
    if sale_data.payments:
        for payment_data in sale_data.payments:
            payment = Payment(
                sale_id=db_sale.id,
                amount=payment_data.amount,
                payment_method=PaymentMethod(payment_data.payment_method),
                payment_date=payment_data.payment_date,
                reference=payment_data.reference,  # Receipt number for cash, transaction ref for bank transfer
                notes=payment_data.notes
            )
            db.add(payment)
    
    await db.commit()
    await db.refresh(db_sale)
    
    # Eager load relationships for response serialization
    statement = select(Sale).options(
        selectinload(Sale.sale_lines),
        selectinload(Sale.payments)
    ).where(Sale.id == db_sale.id)
    result = await db.execute(statement)
    sale_with_relations = result.scalar_one()
    
    return sale_with_relations
