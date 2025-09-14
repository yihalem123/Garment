"""
Test sales functionality
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models import Sale, SaleLine, StockItem, ItemType


class TestSales:
    """Test sales endpoints and functionality"""
    
    async def test_sale_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_shop,
        test_product,
        test_stock_item
    ):
        """Test successful sale creation"""
        sale_data = {
            "sale_number": "SALE-001",
            "shop_id": test_shop.id,
            "customer_name": "John Doe",
            "customer_phone": "+1234567890",
            "discount_amount": 5.00,
            "sale_date": "2024-01-15",
            "notes": "Test sale",
            "sale_lines": [
                {
                    "product_id": test_product.id,
                    "quantity": 2.0,
                    "unit_price": 25.00
                }
            ],
            "payments": [
                {
                    "amount": 45.00,
                    "payment_method": "cash",
                    "payment_date": "2024-01-15",
                    "reference": "RCP-001",
                    "notes": "Cash payment"
                }
            ]
        }
        
        response = await client.post(
            "/sales/",
            json=sale_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sale_number"] == "SALE-001"
        assert data["final_amount"] == 45.00  # (2 * 25) - 5
        assert len(data["sale_lines"]) == 1
        assert len(data["payments"]) == 1
    
    async def test_sale_insufficient_stock(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_shop,
        test_product,
        test_stock_item
    ):
        """Test sale with insufficient stock"""
        sale_data = {
            "sale_number": "SALE-002",
            "shop_id": test_shop.id,
            "customer_name": "Jane Doe",
            "sale_date": "2024-01-15",
            "sale_lines": [
                {
                    "product_id": test_product.id,
                    "quantity": 150.0,  # More than available stock
                    "unit_price": 25.00
                }
            ]
        }
        
        response = await client.post(
            "/sales/",
            json=sale_data,
            headers=auth_headers
        )
        
        assert response.status_code == 409  # Conflict - insufficient stock
        assert "Insufficient stock" in response.json()["detail"]
    
    async def test_sale_stock_deduction(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_shop,
        test_product,
        test_stock_item
    ):
        """Test that sale properly deducts stock"""
        initial_quantity = test_stock_item.quantity
        
        sale_data = {
            "sale_number": "SALE-003",
            "shop_id": test_shop.id,
            "customer_name": "Bob Smith",
            "sale_date": "2024-01-15",
            "sale_lines": [
                {
                    "product_id": test_product.id,
                    "quantity": 5.0,
                    "unit_price": 25.00
                }
            ]
        }
        
        response = await client.post(
            "/sales/",
            json=sale_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Check that stock was deducted
        from sqlalchemy import select
        statement = select(StockItem).where(StockItem.id == test_stock_item.id)
        updated_stock = await db_session.exec(statement)
        updated_stock = updated_stock.first()
        
        assert updated_stock.quantity == initial_quantity - 5.0
    
    async def test_get_sales(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_shop
    ):
        """Test getting sales list"""
        response = await client.get(
            f"/sales/?shop_id={test_shop.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_sale_by_id(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_shop,
        test_product,
        test_stock_item
    ):
        """Test getting a specific sale by ID"""
        # First create a sale
        sale_data = {
            "sale_number": "SALE-004",
            "shop_id": test_shop.id,
            "customer_name": "Alice Johnson",
            "sale_date": "2024-01-15",
            "sale_lines": [
                {
                    "product_id": test_product.id,
                    "quantity": 1.0,
                    "unit_price": 25.00
                }
            ]
        }
        
        create_response = await client.post(
            "/sales/",
            json=sale_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 200
        sale_id = create_response.json()["id"]
        
        # Then get the sale
        response = await client.get(
            f"/sales/{sale_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sale_id
        assert data["sale_number"] == "SALE-004"
