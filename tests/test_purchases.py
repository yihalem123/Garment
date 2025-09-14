"""
Test purchase functionality
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models import Purchase, PurchaseLine, StockItem, ItemType


class TestPurchases:
    """Test purchase endpoints and functionality"""
    
    async def test_purchase_increases_raw_stock(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_raw_material
    ):
        """Test that purchase properly increases raw material stock"""
        # Create initial stock item
        initial_stock = StockItem(
            shop_id=1,
            item_type=ItemType.RAW_MATERIAL,
            raw_material_id=test_raw_material.id,
            quantity=50.0,
            reserved_quantity=0.0,
            min_stock_level=10.0
        )
        db_session.add(initial_stock)
        await db_session.commit()
        
        initial_quantity = initial_stock.quantity
        
        # Create purchase
        purchase_data = {
            "supplier_name": "Test Supplier",
            "supplier_invoice": "INV-001",
            "purchase_date": "2024-01-15",
            "notes": "Test purchase",
            "purchase_lines": [
                {
                    "raw_material_id": test_raw_material.id,
                    "quantity": 25.0,
                    "unit_price": 5.00
                }
            ]
        }
        
        response = await client.post(
            "/purchases/",
            json=purchase_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_amount"] == 125.00  # 25 * 5
        assert len(data["purchase_lines"]) == 1
        
        # Check that stock was increased
        from sqlalchemy import select
        statement = select(StockItem).where(StockItem.id == initial_stock.id)
        updated_stock = await db_session.exec(statement)
        updated_stock = updated_stock.first()
        
        assert updated_stock.quantity == initial_quantity + 25.0
    
    async def test_purchase_creates_new_stock_item(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_raw_material
    ):
        """Test that purchase creates new stock item if none exists"""
        # Don't create initial stock item
        
        # Create purchase
        purchase_data = {
            "supplier_name": "Test Supplier 2",
            "supplier_invoice": "INV-002",
            "purchase_date": "2024-01-15",
            "purchase_lines": [
                {
                    "raw_material_id": test_raw_material.id,
                    "quantity": 30.0,
                    "unit_price": 4.00
                }
            ]
        }
        
        response = await client.post(
            "/purchases/",
            json=purchase_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Check that new stock item was created
        from sqlalchemy import select
        statement = select(StockItem).where(
            StockItem.raw_material_id == test_raw_material.id
        )
        stock_item = await db_session.exec(statement)
        stock_item = stock_item.first()
        
        assert stock_item is not None
        assert stock_item.quantity == 30.0
        assert stock_item.item_type == ItemType.RAW_MATERIAL
    
    async def test_get_purchases(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting purchases list"""
        response = await client.get(
            "/purchases/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_purchase_by_id(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_raw_material
    ):
        """Test getting a specific purchase by ID"""
        # Create a purchase
        purchase_data = {
            "supplier_name": "Test Supplier 3",
            "supplier_invoice": "INV-003",
            "purchase_date": "2024-01-15",
            "purchase_lines": [
                {
                    "raw_material_id": test_raw_material.id,
                    "quantity": 20.0,
                    "unit_price": 3.00
                }
            ]
        }
        
        create_response = await client.post(
            "/purchases/",
            json=purchase_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 200
        purchase_id = create_response.json()["id"]
        
        # Get the purchase
        response = await client.get(
            f"/purchases/{purchase_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == purchase_id
        assert data["supplier_name"] == "Test Supplier 3"
