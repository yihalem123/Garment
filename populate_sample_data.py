#!/usr/bin/env python3
"""
Sample data population script for Garment Business Management System
Populates database with real business data from your Excel files
"""

import asyncio
import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.session import get_session
from app.models import *
from app.core.security import get_password_hash

async def populate_sample_data():
    """Populate database with real sample data"""
    print("📊 Populating database with real business sample data...")
    
    from app.db.session import async_session_maker
    async with async_session_maker() as session:
        # Create users
        admin_user = User(
            username="admin",
            email="admin@garment.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        session.add(admin_user)
        
        manager_user = User(
            username="manager",
            email="manager@garment.com",
            full_name="Shop Manager",
            hashed_password=get_password_hash("manager123"),
            role=UserRole.SHOP_MANAGER,
            is_active=True
        )
        session.add(manager_user)
        
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
        
        # Create raw materials based on your purchase data
        raw_materials = [
            RawMaterial(
                name="Dryer",
                sku="DRY-001",
                unit="roll",
                unit_price=Decimal("750.00"),
                description="Dryer material for production"
            ),
            RawMaterial(
                name="Rim/Rubber 3cm",
                sku="RIM-003",
                unit="pcs", 
                unit_price=Decimal("180.00"),
                description="3cm rim/rubber material"
            ),
            RawMaterial(
                name="Cotton Fabric",
                sku="COT-001",
                unit="meter",
                unit_price=Decimal("50.00"),
                description="Cotton fabric material"
            ),
            RawMaterial(
                name="MG Fabric",
                sku="MG-001",
                unit="meter",
                unit_price=Decimal("60.00"),
                description="MG fabric material"
            ),
            RawMaterial(
                name="Fure Cotton",
                sku="FC-001",
                unit="meter",
                unit_price=Decimal("45.00"),
                description="Fure cotton material"
            ),
        ]
        
        for rm in raw_materials:
            session.add(rm)
        
        # Create products based on your sales data
        products = [
            Product(
                name="T-shirt Cotton",
                sku="MGF-003-mcnt",
                category="T-shirt",
                unit_price=Decimal("240.00"),
                cost_price=Decimal("205.00"),
                description="Cotton T-shirt"
            ),
            Product(
                name="T-shirt MG",
                sku="MGF-013-vcmcnt", 
                category="T-shirt",
                unit_price=Decimal("280.00"),
                cost_price=Decimal("243.00"),
                description="MG T-shirt"
            ),
            Product(
                name="T-shirt MG MS",
                sku="MGF-007-MS",
                category="T-shirt",
                unit_price=Decimal("350.00"),
                cost_price=Decimal("310.00"),
                description="MG MS T-shirt"
            ),
            Product(
                name="T-shirt Fure Cotton",
                sku="MGF-003-mcnt-fc",
                category="T-shirt",
                unit_price=Decimal("240.00"),
                cost_price=Decimal("200.00"),
                description="Fure Cotton T-shirt"
            ),
            Product(
                name="T-shirt Cotton KPS",
                sku="MGF-006-kps",
                category="T-shirt",
                unit_price=Decimal("280.00"),
                cost_price=Decimal("230.00"),
                description="Cotton KPS T-shirt"
            ),
            Product(
                name="Grey Complete Set",
                sku="GCS-001",
                category="Complete Set",
                unit_price=Decimal("140.00"),
                cost_price=Decimal("100.00"),
                description="Grey complete set"
            ),
            Product(
                name="Complete Set",
                sku="CS-001",
                category="Complete Set", 
                unit_price=Decimal("140.00"),
                cost_price=Decimal("100.00"),
                description="Complete set"
            ),
            Product(
                name="Raincoat",
                sku="RC-001",
                category="Raincoat",
                unit_price=Decimal("800.00"),
                cost_price=Decimal("600.00"),
                description="Raincoat"
            ),
        ]
        
        for product in products:
            session.add(product)
        
        await session.commit()
        
        # Create stock items based on your stock data
        stock_items = [
            StockItem(
                shop_id=main_shop.id,
                item_type=ItemType.PRODUCT,
                product_id=products[5].id,  # Grey Complete Set
                quantity=Decimal("281.000"),
                min_stock_level=Decimal("50.000")
            ),
            StockItem(
                shop_id=main_shop.id,
                item_type=ItemType.PRODUCT,
                product_id=products[6].id,  # Complete Set
                quantity=Decimal("159.000"),
                min_stock_level=Decimal("30.000")
            ),
            StockItem(
                shop_id=main_shop.id,
                item_type=ItemType.PRODUCT,
                product_id=products[7].id,  # Raincoat
                quantity=Decimal("47.000"),
                min_stock_level=Decimal("10.000")
            ),
            StockItem(
                shop_id=main_shop.id,
                item_type=ItemType.PRODUCT,
                product_id=products[7].id,  # Raincoat (another batch)
                quantity=Decimal("9.000"),
                min_stock_level=Decimal("5.000")
            ),
            StockItem(
                shop_id=main_shop.id,
                item_type=ItemType.PRODUCT,
                product_id=products[7].id,  # Raincoat (another batch)
                quantity=Decimal("10.000"),
                min_stock_level=Decimal("5.000")
            ),
        ]
        
        for stock in stock_items:
            session.add(stock)
        
        # Create purchases based on your purchase data
        purchase1 = Purchase(
            supplier_name="Tigist",
            purchase_date="2017-03-12",
            total_amount=Decimal("3300.00"),
            status=PurchaseStatus.RECEIVED,
            notes="Purchase from Tigist supplier"
        )
        session.add(purchase1)
        
        await session.commit()
        
        # Create purchase lines
        purchase_lines = [
            PurchaseLine(
                purchase_id=purchase1.id,
                raw_material_id=raw_materials[0].id,  # Dryer
                quantity=Decimal("2.000"),
                unit_price=Decimal("750.00"),
                total_price=Decimal("1500.00")
            ),
            PurchaseLine(
                purchase_id=purchase1.id,
                raw_material_id=raw_materials[1].id,  # Rim/Rubber
                quantity=Decimal("10.000"),
                unit_price=Decimal("180.00"),
                total_price=Decimal("1800.00")
            ),
        ]
        
        for line in purchase_lines:
            session.add(line)
        
        # Create production runs based on your production data
        production1 = ProductionRun(
            run_number="PROD-2017-001",
            status=ProductionStatus.COMPLETED,
            planned_quantity=Decimal("200.000"),
            actual_quantity=Decimal("200.000"),
            start_date="2017-07-10",
            end_date="2017-07-10",
            notes="Production run for T-shirts"
        )
        session.add(production1)
        
        await session.commit()
        
        # Create production lines
        production_lines = [
            ProductionLine(
                production_run_id=production1.id,
                product_id=products[0].id,  # T-shirt Cotton
                planned_quantity=Decimal("80.000"),
                actual_quantity=Decimal("80.000")
            ),
            ProductionLine(
                production_run_id=production1.id,
                product_id=products[0].id,  # T-shirt Cotton (another batch)
                planned_quantity=Decimal("120.000"),
                actual_quantity=Decimal("120.000")
            ),
        ]
        
        for line in production_lines:
            session.add(line)
        
        # Create transfers based on your transfer data
        transfer1 = Transfer(
            transfer_number="TRF-2017-001",
            from_shop_id=main_shop.id,
            to_shop_id=branch_shop.id,
            transfer_date="2017-07-12",
            status=TransferStatus.RECEIVED,
            notes="Transfer to branch shop"
        )
        session.add(transfer1)
        
        await session.commit()
        
        # Create transfer lines
        transfer_lines = [
            TransferLine(
                transfer_id=transfer1.id,
                product_id=products[1].id,  # T-shirt MG
                quantity=Decimal("337.000"),
                unit_cost=Decimal("243.00"),
                total_cost=Decimal("81891.00")
            ),
            TransferLine(
                transfer_id=transfer1.id,
                product_id=products[2].id,  # T-shirt MG MS
                quantity=Decimal("231.000"),
                unit_cost=Decimal("310.00"),
                total_cost=Decimal("71610.00")
            ),
        ]
        
        for line in transfer_lines:
            session.add(line)
        
        # Create sales based on your sales data
        sale1 = Sale(
            sale_number="SALE-2017-001",
            shop_id=main_shop.id,
            sale_date="2017-07-15",
            customer_name="John Doe",
            customer_phone="+251-91-123-4567",
            total_amount=Decimal("43200.00"),
            final_amount=Decimal("43200.00"),
            status=SaleStatus.COMPLETED,
            notes="Sale of cotton T-shirts"
        )
        session.add(sale1)
        
        await session.commit()
        
        # Create sale lines
        sale_lines = [
            SaleLine(
                sale_id=sale1.id,
                product_id=products[0].id,  # T-shirt Cotton
                quantity=Decimal("180.000"),
                unit_price=Decimal("240.00"),
                total_price=Decimal("43200.00")
            ),
        ]
        
        for line in sale_lines:
            session.add(line)
        
        # Create payment
        payment1 = Payment(
            sale_id=sale1.id,
            payment_method=PaymentMethod.CASH,
            amount=Decimal("43200.00"),
            payment_date="2017-07-15",
            reference="RCP-001",
            notes="Cash payment"
        )
        session.add(payment1)
        
        # Create returns based on your return data
        return1 = Return(
            return_number="RET-2017-001",
            sale_id=sale1.id,
            product_id=products[0].id,  # T-shirt Cotton
            quantity=Decimal("3.000"),
            unit_price=Decimal("1500.00"),
            total_amount=Decimal("4500.00"),
            reason=ReturnReason.DEFECTIVE,
            return_date="2017-07-20",
            notes="Defective product return"
        )
        session.add(return1)
        
        await session.commit()
        
        print("✅ Sample data populated successfully!")
        print(f"   - {len(raw_materials)} raw materials")
        print(f"   - {len(products)} products")
        print(f"   - {len(stock_items)} stock items")
        print(f"   - 1 purchase with {len(purchase_lines)} lines")
        print(f"   - 1 production run with {len(production_lines)} lines")
        print(f"   - 1 transfer with {len(transfer_lines)} lines")
        print(f"   - 1 sale with {len(sale_lines)} lines and 1 payment")
        print(f"   - 1 return")

async def main():
    """Main function"""
    print("🚀 Populating Garment Business Management System with Sample Data")
    print("=" * 70)
    
    try:
        await populate_sample_data()
        print("\n🎉 Sample data population completed successfully!")
        print("\n📋 You can now:")
        print("   - Visit http://localhost:8000/docs to explore the API")
        print("   - Run test_endpoints.py to test individual endpoints")
        print("   - Run test_complete_system.py for comprehensive testing")
        
    except Exception as e:
        print(f"❌ Error populating sample data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
