"""
Product routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.models import Product, User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get products with optional filtering
    
    Example request:
    ```
    curl -X GET "http://localhost:8000/products/?category=shirts&is_active=true" \
         -H "Authorization: Bearer <token>"
    ```
    """
    statement = select(Product)
    
    if category:
        statement = statement.where(Product.category == category)
    if is_active is not None:
        statement = statement.where(Product.is_active == is_active)
    
    statement = statement.offset(skip).limit(limit)
    products = await db.exec(statement)
    return products.all()


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific product by ID
    
    Example response:
    ```json
    {
        "id": 1,
        "name": "Cotton T-Shirt",
        "description": "100% cotton t-shirt",
        "sku": "TSH001",
        "category": "shirts",
        "unit_price": 25.00,
        "cost_price": 15.00,
        "is_active": true
    }
    ```
    """
    statement = select(Product).where(Product.id == product_id)
    product = await db.exec(statement)
    product = product.first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new product
    
    Example request:
    ```json
    {
        "name": "Cotton T-Shirt",
        "description": "100% cotton t-shirt",
        "sku": "TSH001",
        "category": "shirts",
        "unit_price": 25.00,
        "cost_price": 15.00
    }
    ```
    """
    # Check if SKU already exists
    statement = select(Product).where(Product.sku == product_data.sku)
    existing_product = await db.exec(statement)
    if existing_product.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )
    
    db_product = Product(**product_data.dict())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    
    return db_product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update a product
    """
    statement = select(Product).where(Product.id == product_id)
    product = await db.exec(statement)
    product = product.first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if new SKU already exists (if provided)
    if product_data.sku and product_data.sku != product.sku:
        statement = select(Product).where(Product.sku == product_data.sku)
        existing_product = await db.exec(statement)
        if existing_product.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists"
            )
    
    # Update fields
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    await db.commit()
    await db.refresh(product)
    
    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a product (soft delete by setting is_active=False)
    """
    statement = select(Product).where(Product.id == product_id)
    product = await db.exec(statement)
    product = product.first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product.is_active = False
    await db.commit()
    
    return {"message": "Product deleted successfully"}
