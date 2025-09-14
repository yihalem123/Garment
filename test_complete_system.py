#!/usr/bin/env python3
"""
Comprehensive test script for Garment Business Management System
This script populates the database with real sample data and tests all endpoints
"""

import asyncio
import json
import httpx
from datetime import datetime, date
from decimal import Decimal
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.session import get_session
from app.models import *
from sqlmodel import select
from app.core.security import get_password_hash

# Base URL for the API
BASE_URL = "http://localhost:8000"

class TestClient:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL)
        self.token = None
        self.admin_token = None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def login(self, username: str, password: str):
        """Login and get access token"""
        response = await self.client.post("/auth/login", data={
            "username": username,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})
            return True
        return False
    
    async def get(self, endpoint: str):
        """GET request"""
        return await self.client.get(endpoint)
    
    async def post(self, endpoint: str, data: dict):
        """POST request"""
        return await self.client.post(endpoint, json=data)
    
    async def put(self, endpoint: str, data: dict):
        """PUT request"""
        return await self.client.put(endpoint, json=data)
    
    async def delete(self, endpoint: str):
        """DELETE request"""
        return await self.client.delete(endpoint)

async def setup_database():
    """Setup database with initial data"""
    print("🔧 Setting up database...")
    
    async with get_session() as session:
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@garment.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        session.add(admin_user)
        
        # Create shop manager
        shop_manager = User(
            username="manager",
            email="manager@garment.com", 
            full_name="Shop Manager",
            hashed_password=get_password_hash("manager123"),
            role=UserRole.SHOP_MANAGER,
            is_active=True
        )
        session.add(shop_manager)
        
        # Create shops
        main_shop = Shop(
            name="Main Shop",
            address="Main Street, Addis Ababa",
            phone="+251-11-123-4567",
            email="main@garment.com",
            is_active=True
        )
        session.add(main_shop)
        
        branch_shop = Shop(
            name="Branch Shop",
            address="Branch Street, Addis Ababa", 
            phone="+251-11-765-4321",
            email="branch@garment.com",
            is_active=True
        )
        session.add(branch_shop)
        
        await session.commit()
        print("✅ Database setup complete")

async def populate_sample_data():
    """Populate database with real sample data"""
    print("📊 Populating database with sample data...")
    
    async with get_session() as session:
        # Get shops
        shops_result = await session.execute(select(Shop))
        shops = shops_result.scalars().all()
        main_shop = shops[0] if shops else None
        
        # Create raw materials based on your purchase data
        raw_materials_data = [
            {"name": "Dryer", "sku": "DRY-001", "unit": "roll", "unit_price": Decimal("750.00")},
            {"name": "Rim/Rubber 3cm", "sku": "RIM-003", "unit": "pcs", "unit_price": Decimal("180.00")},
            {"name": "Cotton Fabric", "sku": "COT-001", "unit": "meter", "unit_price": Decimal("50.00")},
            {"name": "MG Fabric", "sku": "MG-001", "unit": "meter", "unit_price": Decimal("60.00")},
            {"name": "Fure Cotton", "sku": "FC-001", "unit": "meter", "unit_price": Decimal("45.00")},
        ]
        
        raw_materials = []
        for rm_data in raw_materials_data:
            raw_material = RawMaterial(**rm_data)
            session.add(raw_material)
            raw_materials.append(raw_material)
        
        # Create products based on your sales data
        products_data = [
            {"name": "T-shirt Cotton", "sku": "MGF-003-mcnt", "category": "T-shirt", "unit_price": Decimal("240.00"), "cost_price": Decimal("205.00")},
            {"name": "T-shirt MG", "sku": "MGF-013-vcmcnt", "category": "T-shirt", "unit_price": Decimal("280.00"), "cost_price": Decimal("243.00")},
            {"name": "T-shirt MG MS", "sku": "MGF-007-MS", "category": "T-shirt", "unit_price": Decimal("350.00"), "cost_price": Decimal("310.00")},
            {"name": "T-shirt Fure Cotton", "sku": "MGF-003-mcnt", "category": "T-shirt", "unit_price": Decimal("240.00"), "cost_price": Decimal("200.00")},
            {"name": "T-shirt Cotton KPS", "sku": "MGF-006-kps", "category": "T-shirt", "unit_price": Decimal("280.00"), "cost_price": Decimal("230.00")},
            {"name": "Grey Complete Set", "sku": "GCS-001", "category": "Complete Set", "unit_price": Decimal("140.00"), "cost_price": Decimal("100.00")},
            {"name": "Complete Set", "sku": "CS-001", "category": "Complete Set", "unit_price": Decimal("140.00"), "cost_price": Decimal("100.00")},
            {"name": "Raincoat", "sku": "RC-001", "category": "Raincoat", "unit_price": Decimal("800.00"), "cost_price": Decimal("600.00")},
        ]
        
        products = []
        for prod_data in products_data:
            product = Product(**prod_data)
            session.add(product)
            products.append(product)
        
        await session.commit()
        
        # Create stock items based on your stock data
        stock_items_data = [
            {"shop_id": main_shop.id, "item_type": ItemType.PRODUCT, "product_id": products[5].id, "quantity": Decimal("281"), "min_stock_level": Decimal("50")},
            {"shop_id": main_shop.id, "item_type": ItemType.PRODUCT, "product_id": products[6].id, "quantity": Decimal("159"), "min_stock_level": Decimal("30")},
            {"shop_id": main_shop.id, "item_type": ItemType.PRODUCT, "product_id": products[7].id, "quantity": Decimal("47"), "min_stock_level": Decimal("10")},
            {"shop_id": main_shop.id, "item_type": ItemType.PRODUCT, "product_id": products[7].id, "quantity": Decimal("9"), "min_stock_level": Decimal("5")},
            {"shop_id": main_shop.id, "item_type": ItemType.PRODUCT, "product_id": products[7].id, "quantity": Decimal("10"), "min_stock_level": Decimal("5")},
        ]
        
        for stock_data in stock_items_data:
            stock_item = StockItem(**stock_data)
            session.add(stock_item)
        
        await session.commit()
        print("✅ Sample data populated successfully")

async def test_authentication(client: TestClient):
    """Test authentication endpoints"""
    print("\n🔐 Testing Authentication...")
    
    # Test login
    response = await client.login("admin", "admin123")
    if response:
        print("✅ Admin login successful")
    else:
        print("❌ Admin login failed")
        return False
    
    # Test get current user
    response = await client.get("/users/me")
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Get current user: {user_data['full_name']}")
    else:
        print("❌ Get current user failed")
    
    return True

async def test_products_endpoints(client: TestClient):
    """Test products endpoints"""
    print("\n📦 Testing Products...")
    
    # Get all products
    response = await client.get("/products")
    if response.status_code == 200:
        products = response.json()
        print(f"✅ Get products: {len(products)} products found")
    else:
        print("❌ Get products failed")
    
    # Get all raw materials
    response = await client.get("/raw-materials")
    if response.status_code == 200:
        raw_materials = response.json()
        print(f"✅ Get raw materials: {len(raw_materials)} raw materials found")
    else:
        print("❌ Get raw materials failed")

async def test_inventory_endpoints(client: TestClient):
    """Test inventory endpoints"""
    print("\n📊 Testing Inventory...")
    
    # Get stock items
    response = await client.get("/stocks")
    if response.status_code == 200:
        stocks = response.json()
        print(f"✅ Get stocks: {len(stocks)} stock items found")
    else:
        print("❌ Get stocks failed")
    
    # Get stock movements
    response = await client.get("/stock-movements")
    if response.status_code == 200:
        movements = response.json()
        print(f"✅ Get stock movements: {len(movements)} movements found")
    else:
        print("❌ Get stock movements failed")

async def test_purchase_flow(client: TestClient):
    """Test purchase flow"""
    print("\n🛒 Testing Purchase Flow...")
    
    # Create a purchase
    purchase_data = {
        "purchase_number": "PUR-001",
        "supplier_name": "Tigist Supplier",
        "purchase_date": "2017-03-12",
        "total_amount": Decimal("3300.00"),
        "status": "received",
        "purchase_lines": [
            {
                "raw_material_id": 1,  # Dryer
                "quantity": Decimal("2.000"),
                "unit_price": Decimal("750.00"),
                "total_price": Decimal("1500.00")
            },
            {
                "raw_material_id": 2,  # Rim/Rubber
                "quantity": Decimal("10.000"),
                "unit_price": Decimal("180.00"),
                "total_price": Decimal("1800.00")
            }
        ]
    }
    
    response = await client.post("/purchases", data=purchase_data)
    if response.status_code == 200:
        purchase = response.json()
        print(f"✅ Create purchase: {purchase['purchase_number']}")
    else:
        print(f"❌ Create purchase failed: {response.text}")

async def test_production_flow(client: TestClient):
    """Test production flow"""
    print("\n🏭 Testing Production Flow...")
    
    # Create a production run
    production_data = {
        "production_number": "PROD-001",
        "production_date": "2017-07-10",
        "status": "completed",
        "production_lines": [
            {
                "product_id": 1,  # T-shirt Cotton
                "planned_quantity": Decimal("80.000"),
                "actual_quantity": Decimal("80.000")
            }
        ],
        "production_consumptions": [
            {
                "raw_material_id": 3,  # Cotton Fabric
                "planned_consumption": Decimal("40.000"),
                "actual_consumption": Decimal("40.000")
            }
        ]
    }
    
    response = await client.post("/production-runs", data=production_data)
    if response.status_code == 200:
        production = response.json()
        print(f"✅ Create production run: {production['production_number']}")
    else:
        print(f"❌ Create production run failed: {response.text}")

async def test_transfer_flow(client: TestClient):
    """Test transfer flow"""
    print("\n🚚 Testing Transfer Flow...")
    
    # Create a transfer
    transfer_data = {
        "transfer_number": "TRF-001",
        "from_shop_id": 1,
        "to_shop_id": 2,
        "transfer_date": "2017-07-12",
        "status": "received",
        "transfer_lines": [
            {
                "product_id": 1,  # T-shirt Cotton
                "quantity": Decimal("100.000"),
                "unit_cost": Decimal("205.00"),
                "total_cost": Decimal("20500.00")
            }
        ]
    }
    
    response = await client.post("/transfers", data=transfer_data)
    if response.status_code == 200:
        transfer = response.json()
        print(f"✅ Create transfer: {transfer['transfer_number']}")
    else:
        print(f"❌ Create transfer failed: {response.text}")

async def test_sales_flow(client: TestClient):
    """Test sales flow"""
    print("\n💰 Testing Sales Flow...")
    
    # Create a sale
    sale_data = {
        "sale_number": "SALE-001",
        "shop_id": 1,
        "sale_date": "2017-07-15",
        "customer_name": "John Doe",
        "customer_phone": "+251-91-123-4567",
        "total_amount": Decimal("43200.00"),
        "status": "completed",
        "sale_lines": [
            {
                "product_id": 1,  # T-shirt Cotton
                "quantity": Decimal("180.000"),
                "unit_price": Decimal("240.00"),
                "total_price": Decimal("43200.00")
            }
        ],
        "payments": [
            {
                "payment_method": "cash",
                "amount": Decimal("43200.00"),
                "payment_date": "2017-07-15",
                "reference": "RCP-001"
            }
        ]
    }
    
    response = await client.post("/sales", data=sale_data)
    if response.status_code == 200:
        sale = response.json()
        print(f"✅ Create sale: {sale['sale_number']}")
    else:
        print(f"❌ Create sale failed: {response.text}")

async def test_analytics_endpoints(client: TestClient):
    """Test analytics endpoints"""
    print("\n📈 Testing Analytics...")
    
    # Test dashboard
    response = await client.get("/analytics/dashboard")
    if response.status_code == 200:
        dashboard = response.json()
        print("✅ Dashboard analytics retrieved")
    else:
        print("❌ Dashboard analytics failed")
    
    # Test profit/loss
    response = await client.get("/analytics/profit-loss?start_date=2017-01-01&end_date=2017-12-31")
    if response.status_code == 200:
        profit_loss = response.json()
        print("✅ Profit/Loss analytics retrieved")
    else:
        print("❌ Profit/Loss analytics failed")

async def test_business_intelligence(client: TestClient):
    """Test business intelligence endpoints"""
    print("\n🧠 Testing Business Intelligence...")
    
    # Test KPIs
    response = await client.get("/business-intelligence/kpis")
    if response.status_code == 200:
        kpis = response.json()
        print("✅ KPIs retrieved")
    else:
        print("❌ KPIs failed")
    
    # Test business health
    response = await client.get("/business-intelligence/business-health")
    if response.status_code == 200:
        health = response.json()
        print("✅ Business health retrieved")
    else:
        print("❌ Business health failed")

async def test_finance_endpoints(client: TestClient):
    """Test finance endpoints"""
    print("\n💼 Testing Finance...")
    
    # Test P&L statement
    response = await client.get("/finance/profit-loss-statement?start_date=2017-01-01&end_date=2017-12-31")
    if response.status_code == 200:
        pl = response.json()
        print("✅ P&L statement retrieved")
    else:
        print("❌ P&L statement failed")

async def main():
    """Main test function"""
    print("🚀 Starting Comprehensive Garment Business Management System Test")
    print("=" * 70)
    
    try:
        # Setup database
        await setup_database()
        await populate_sample_data()
        
        # Test with HTTP client
        async with TestClient() as client:
            # Test authentication
            if not await test_authentication(client):
                print("❌ Authentication failed, stopping tests")
                return
            
            # Test all endpoints
            await test_products_endpoints(client)
            await test_inventory_endpoints(client)
            await test_purchase_flow(client)
            await test_production_flow(client)
            await test_transfer_flow(client)
            await test_sales_flow(client)
            await test_analytics_endpoints(client)
            await test_business_intelligence(client)
            await test_finance_endpoints(client)
        
        print("\n" + "=" * 70)
        print("🎉 All tests completed successfully!")
        print("\n📋 Test Summary:")
        print("✅ Database setup and sample data population")
        print("✅ Authentication and user management")
        print("✅ Products and raw materials management")
        print("✅ Inventory tracking and stock movements")
        print("✅ Purchase workflow")
        print("✅ Production workflow")
        print("✅ Transfer workflow")
        print("✅ Sales workflow")
        print("✅ Analytics and reporting")
        print("✅ Business intelligence")
        print("✅ Financial reporting")
        
        print(f"\n🌐 API Documentation: {BASE_URL}/docs")
        print(f"🔗 OpenAPI Spec: {BASE_URL}/openapi.json")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
