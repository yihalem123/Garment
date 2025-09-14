"""
Test inventory functionality
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models import StockItem, StockMovement, ItemType, MovementReason


class TestInventory:
    """Test inventory endpoints and functionality"""
    
    async def test_get_stocks(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_shop,
        test_stock_item
    ):
        """Test getting stock items"""
        response = await client.get(
            f"/inventory/stocks?shop_id={test_shop.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that available_quantity is calculated correctly
        stock_item = data[0]
        assert "available_quantity" in stock_item
        assert stock_item["available_quantity"] == stock_item["quantity"] - stock_item["reserved_quantity"]
    
    async def test_stock_adjustment(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_shop,
        test_product,
        test_stock_item
    ):
        """Test stock adjustment functionality"""
        initial_quantity = test_stock_item.quantity
        
        adjustment_data = {
            "shop_id": test_shop.id,
            "item_type": "product",
            "product_id": test_product.id,
            "quantity": 10.0,
            "reason": "adjustment",
            "notes": "Stock count correction"
        }
        
        response = await client.post(
            "/inventory/stocks/adjust",
            json=adjustment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Check that stock was adjusted
        from sqlalchemy import select
        statement = select(StockItem).where(StockItem.id == test_stock_item.id)
        updated_stock = await db_session.exec(statement)
        updated_stock = updated_stock.first()
        
        assert updated_stock.quantity == initial_quantity + 10.0
        
        # Check that stock movement was created
        statement = select(StockMovement).where(
            StockMovement.shop_id == test_shop.id
        )
        movements = await db_session.exec(statement)
        movements = movements.all()
        
        assert len(movements) >= 1
        movement = movements[-1]  # Get the latest movement
        assert movement.quantity == 10.0
        assert movement.reason == MovementReason.ADJUSTMENT
    
    async def test_get_stock_movements(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_shop
    ):
        """Test getting stock movements"""
        response = await client.get(
            f"/inventory/stock-movements?shop_id={test_shop.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_low_stock_filter(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_shop,
        test_product
    ):
        """Test low stock filtering"""
        # Create a low stock item
        low_stock_item = StockItem(
            shop_id=test_shop.id,
            item_type=ItemType.PRODUCT,
            product_id=test_product.id,
            quantity=5.0,  # Below minimum
            reserved_quantity=0.0,
            min_stock_level=10.0
        )
        db_session.add(low_stock_item)
        await db_session.commit()
        
        # Test low stock filter
        response = await client.get(
            f"/inventory/stocks?shop_id={test_shop.id}&low_stock_only=true",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All returned items should be low stock
        for item in data:
            assert item["quantity"] <= item["min_stock_level"]
