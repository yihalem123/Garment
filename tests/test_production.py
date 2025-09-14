"""
Test production functionality
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models import (
    ProductionRun, ProductionLine, ProductionConsumption,
    StockItem, RawMaterial, ItemType, ProductionStatus
)


class TestProduction:
    """Test production endpoints and functionality"""
    
    async def test_production_complete_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_product,
        test_raw_material
    ):
        """Test successful production run completion"""
        # Create stock items for raw material and product
        raw_material_stock = StockItem(
            shop_id=1,
            item_type=ItemType.RAW_MATERIAL,
            raw_material_id=test_raw_material.id,
            quantity=100.0,
            reserved_quantity=0.0,
            min_stock_level=10.0
        )
        db_session.add(raw_material_stock)
        
        product_stock = StockItem(
            shop_id=1,
            item_type=ItemType.PRODUCT,
            product_id=test_product.id,
            quantity=0.0,
            reserved_quantity=0.0,
            min_stock_level=10.0
        )
        db_session.add(product_stock)
        await db_session.commit()
        
        # Create production run
        production_data = {
            "run_number": "PR-001",
            "planned_quantity": 10.0,
            "labor_cost": 100.00,
            "overhead_cost": 50.00,
            "start_date": "2024-01-15",
            "notes": "Test production run",
            "production_lines": [
                {
                    "product_id": test_product.id,
                    "planned_quantity": 10.0
                }
            ],
            "production_consumptions": [
                {
                    "raw_material_id": test_raw_material.id,
                    "planned_consumption": 25.0
                }
            ]
        }
        
        create_response = await client.post(
            "/production/",
            json=production_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 200
        production_run_id = create_response.json()["id"]
        
        # Complete the production run
        complete_response = await client.post(
            f"/production/{production_run_id}/complete",
            headers=auth_headers
        )
        
        assert complete_response.status_code == 200
        data = complete_response.json()
        assert data["status"] == ProductionStatus.COMPLETED
        assert data["total_cost"] is not None
        
        # Verify stock changes
        from sqlalchemy import select
        
        # Check raw material stock was deducted
        statement = select(StockItem).where(StockItem.id == raw_material_stock.id)
        updated_raw_stock = await db_session.exec(statement)
        updated_raw_stock = updated_raw_stock.first()
        assert updated_raw_stock.quantity == 75.0  # 100 - 25
        
        # Check product stock was added
        statement = select(StockItem).where(StockItem.id == product_stock.id)
        updated_product_stock = await db_session.exec(statement)
        updated_product_stock = updated_product_stock.first()
        assert updated_product_stock.quantity == 10.0
    
    async def test_production_insufficient_raw_material(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_product,
        test_raw_material
    ):
        """Test production run with insufficient raw material"""
        # Create stock item with insufficient raw material
        raw_material_stock = StockItem(
            shop_id=1,
            item_type=ItemType.RAW_MATERIAL,
            raw_material_id=test_raw_material.id,
            quantity=10.0,  # Less than required
            reserved_quantity=0.0,
            min_stock_level=10.0
        )
        db_session.add(raw_material_stock)
        await db_session.commit()
        
        # Create production run
        production_data = {
            "run_number": "PR-002",
            "planned_quantity": 10.0,
            "labor_cost": 100.00,
            "overhead_cost": 50.00,
            "start_date": "2024-01-15",
            "production_lines": [
                {
                    "product_id": test_product.id,
                    "planned_quantity": 10.0
                }
            ],
            "production_consumptions": [
                {
                    "raw_material_id": test_raw_material.id,
                    "planned_consumption": 25.0  # More than available
                }
            ]
        }
        
        create_response = await client.post(
            "/production/",
            json=production_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 200
        production_run_id = create_response.json()["id"]
        
        # Try to complete the production run
        complete_response = await client.post(
            f"/production/{production_run_id}/complete",
            headers=auth_headers
        )
        
        assert complete_response.status_code == 409  # Conflict - insufficient stock
        assert "Insufficient stock" in complete_response.json()["detail"]
    
    async def test_get_production_runs(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting production runs list"""
        response = await client.get(
            "/production/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_production_run_by_id(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_product
    ):
        """Test getting a specific production run by ID"""
        # Create a production run
        production_data = {
            "run_number": "PR-003",
            "planned_quantity": 5.0,
            "labor_cost": 50.00,
            "overhead_cost": 25.00,
            "start_date": "2024-01-15",
            "production_lines": [
                {
                    "product_id": test_product.id,
                    "planned_quantity": 5.0
                }
            ]
        }
        
        create_response = await client.post(
            "/production/",
            json=production_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 200
        production_run_id = create_response.json()["id"]
        
        # Get the production run
        response = await client.get(
            f"/production/{production_run_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == production_run_id
        assert data["run_number"] == "PR-003"
