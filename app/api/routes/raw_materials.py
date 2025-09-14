"""
Raw Materials routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.models import RawMaterial, User
from app.schemas.product import RawMaterialCreate, RawMaterialResponse, RawMaterialUpdate
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[RawMaterialResponse])
async def get_raw_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get raw materials with optional filtering
    
    Example request:
    ```
    curl -X GET "http://localhost:8000/raw-materials/?is_active=true" \
         -H "Authorization: Bearer <token>"
    ```
    """
    statement = select(RawMaterial)
    
    if is_active is not None:
        statement = statement.where(RawMaterial.is_active == is_active)
    
    statement = statement.offset(skip).limit(limit)
    result = await db.execute(statement)
    return result.scalars().all()


@router.get("/{raw_material_id}", response_model=RawMaterialResponse)
async def get_raw_material(
    raw_material_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific raw material by ID
    
    Example response:
    ```json
    {
        "id": 1,
        "name": "Cotton Fabric",
        "description": "100% cotton fabric",
        "sku": "CF001",
        "unit": "kg",
        "unit_price": 5.00,
        "is_active": true
    }
    ```
    """
    statement = select(RawMaterial).where(RawMaterial.id == raw_material_id)
    result = await db.execute(statement)
    raw_material = result.scalar_one_or_none()
    
    if not raw_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Raw material not found"
        )
    
    return raw_material


@router.post("/", response_model=RawMaterialResponse)
async def create_raw_material(
    raw_material_data: RawMaterialCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new raw material
    
    Example request:
    ```json
    {
        "name": "Cotton Fabric",
        "description": "100% cotton fabric",
        "sku": "CF001",
        "unit": "kg",
        "unit_price": 5.00
    }
    ```
    """
    # Check if SKU already exists
    statement = select(RawMaterial).where(RawMaterial.sku == raw_material_data.sku)
    result = await db.execute(statement)
    existing_raw_material = result.scalar_one_or_none()
    if existing_raw_material:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Raw material with this SKU already exists"
        )
    
    db_raw_material = RawMaterial(**raw_material_data.dict())
    db.add(db_raw_material)
    await db.commit()
    await db.refresh(db_raw_material)
    
    return db_raw_material


@router.put("/{raw_material_id}", response_model=RawMaterialResponse)
async def update_raw_material(
    raw_material_id: int,
    raw_material_data: RawMaterialUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update a raw material
    """
    statement = select(RawMaterial).where(RawMaterial.id == raw_material_id)
    result = await db.execute(statement)
    raw_material = result.scalar_one_or_none()
    
    if not raw_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Raw material not found"
        )
    
    # Check if new SKU already exists (if provided)
    if raw_material_data.sku and raw_material_data.sku != raw_material.sku:
        statement = select(RawMaterial).where(RawMaterial.sku == raw_material_data.sku)
        existing_raw_material = await db.execute(statement)
        if existing_raw_material:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Raw material with this SKU already exists"
            )
    
    # Update fields
    update_data = raw_material_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(raw_material, field, value)
    
    await db.commit()
    await db.refresh(raw_material)
    
    return raw_material


@router.delete("/{raw_material_id}")
async def delete_raw_material(
    raw_material_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a raw material (soft delete by setting is_active=False)
    """
    statement = select(RawMaterial).where(RawMaterial.id == raw_material_id)
    result = await db.execute(statement)
    raw_material = result.scalar_one_or_none()
    
    if not raw_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Raw material not found"
        )
    
    raw_material.is_active = False
    await db.commit()
    
    return {"message": "Raw material deleted successfully"}
