"""
Shop routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_session
from app.models import Shop, User
from app.schemas.shop import ShopResponse
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ShopResponse])
async def get_shops(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get all shops
    
    Returns a list of all shops in the system.
    """
    result = await db.execute(select(Shop))
    shops = result.scalars().all()
    return shops


@router.get("/{shop_id}", response_model=ShopResponse)
async def get_shop(
    shop_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific shop by ID
    
    Returns the shop details for the given shop ID.
    """
    result = await db.execute(select(Shop).where(Shop.id == shop_id))
    shop = result.scalar_one_or_none()
    
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    
    return shop
