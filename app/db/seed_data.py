"""
Seed data for the garment management system
"""
import asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.core.security import get_password_hash
from app.models import (
    User, Shop, Product, RawMaterial, FabricRule,
    StockItem, ItemType, UserRole
)


async def create_seed_data():
    """Create initial seed data"""
    async with async_session_maker() as db:
        # Create shops
        shops = [
            Shop(
                name="Main Warehouse",
                address="123 Industrial Ave, City Center",
                phone="+1-555-0100",
                email="warehouse@garment.com"
            ),
            Shop(
                name="Downtown Store",
                address="456 Main St, Downtown",
                phone="+1-555-0101",
                email="downtown@garment.com"
            ),
            Shop(
                name="Mall Branch",
                address="789 Shopping Mall, Suburb",
                phone="+1-555-0102",
                email="mall@garment.com"
            )
        ]
        
        for shop in shops:
            db.add(shop)
        await db.flush()  # Get IDs
        
        # Create users
        users = [
            User(
                email="admin@garment.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                shop_id=None
            ),
            User(
                email="manager@garment.com",
                hashed_password=get_password_hash("manager123"),
                full_name="Store Manager",
                role=UserRole.SHOP_MANAGER,
                shop_id=shops[1].id  # Downtown Store
            ),
            User(
                email="staff@garment.com",
                hashed_password=get_password_hash("staff123"),
                full_name="Store Staff",
                role=UserRole.STAFF,
                shop_id=shops[1].id  # Downtown Store
            )
        ]
        
        for user in users:
            db.add(user)
        await db.flush()
        
        # Create raw materials
        raw_materials = [
            RawMaterial(
                name="Cotton Fabric",
                description="100% cotton fabric for shirts and dresses",
                sku="CF001",
                unit="kg",
                unit_price=Decimal("5.50")
            ),
            RawMaterial(
                name="Polyester Fabric",
                description="Polyester blend fabric for sportswear",
                sku="PF001",
                unit="kg",
                unit_price=Decimal("4.00")
            ),
            RawMaterial(
                name="Denim Fabric",
                description="Heavy denim fabric for jeans",
                sku="DF001",
                unit="kg",
                unit_price=Decimal("6.00")
            ),
            RawMaterial(
                name="Silk Fabric",
                description="Premium silk fabric for luxury items",
                sku="SF001",
                unit="kg",
                unit_price=Decimal("25.00")
            ),
            RawMaterial(
                name="Thread",
                description="Cotton thread for sewing",
                sku="TH001",
                unit="spool",
                unit_price=Decimal("2.00")
            ),
            RawMaterial(
                name="Zippers",
                description="Metal zippers for various garments",
                sku="ZP001",
                unit="piece",
                unit_price=Decimal("1.50")
            )
        ]
        
        for raw_material in raw_materials:
            db.add(raw_material)
        await db.flush()
        
        # Create products
        products = [
            Product(
                name="Cotton T-Shirt",
                description="Comfortable 100% cotton t-shirt",
                sku="TSH001",
                category="shirts",
                unit_price=Decimal("25.00"),
                cost_price=Decimal("15.00")
            ),
            Product(
                name="Denim Jeans",
                description="Classic blue denim jeans",
                sku="JNS001",
                category="pants",
                unit_price=Decimal("45.00"),
                cost_price=Decimal("28.00")
            ),
            Product(
                name="Silk Blouse",
                description="Elegant silk blouse for formal wear",
                sku="BLU001",
                category="shirts",
                unit_price=Decimal("85.00"),
                cost_price=Decimal("55.00")
            ),
            Product(
                name="Sport Shorts",
                description="Comfortable polyester sport shorts",
                sku="SHT001",
                category="shorts",
                unit_price=Decimal("20.00"),
                cost_price=Decimal("12.00")
            ),
            Product(
                name="Cotton Dress",
                description="Summer cotton dress",
                sku="DRS001",
                category="dresses",
                unit_price=Decimal("35.00"),
                cost_price=Decimal("22.00")
            )
        ]
        
        for product in products:
            db.add(product)
        await db.flush()
        
        # Create fabric rules (consumption per unit)
        fabric_rules = [
            # Cotton T-Shirt
            FabricRule(
                product_id=products[0].id,
                raw_material_id=raw_materials[0].id,  # Cotton Fabric
                consumption_per_unit=Decimal("0.3")  # 0.3 kg per t-shirt
            ),
            FabricRule(
                product_id=products[0].id,
                raw_material_id=raw_materials[4].id,  # Thread
                consumption_per_unit=Decimal("0.1")  # 0.1 spool per t-shirt
            ),
            
            # Denim Jeans
            FabricRule(
                product_id=products[1].id,
                raw_material_id=raw_materials[2].id,  # Denim Fabric
                consumption_per_unit=Decimal("0.8")  # 0.8 kg per jeans
            ),
            FabricRule(
                product_id=products[1].id,
                raw_material_id=raw_materials[5].id,  # Zippers
                consumption_per_unit=Decimal("1.0")  # 1 zipper per jeans
            ),
            
            # Silk Blouse
            FabricRule(
                product_id=products[2].id,
                raw_material_id=raw_materials[3].id,  # Silk Fabric
                consumption_per_unit=Decimal("0.4")  # 0.4 kg per blouse
            ),
            
            # Sport Shorts
            FabricRule(
                product_id=products[3].id,
                raw_material_id=raw_materials[1].id,  # Polyester Fabric
                consumption_per_unit=Decimal("0.2")  # 0.2 kg per shorts
            ),
            
            # Cotton Dress
            FabricRule(
                product_id=products[4].id,
                raw_material_id=raw_materials[0].id,  # Cotton Fabric
                consumption_per_unit=Decimal("0.6")  # 0.6 kg per dress
            )
        ]
        
        for rule in fabric_rules:
            db.add(rule)
        await db.flush()
        
        # Create initial stock items
        stock_items = [
            # Raw materials in main warehouse
            StockItem(
                shop_id=shops[0].id,  # Main Warehouse
                item_type=ItemType.RAW_MATERIAL,
                raw_material_id=raw_materials[0].id,  # Cotton Fabric
                quantity=Decimal("100.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("20.0")
            ),
            StockItem(
                shop_id=shops[0].id,
                item_type=ItemType.RAW_MATERIAL,
                raw_material_id=raw_materials[1].id,  # Polyester Fabric
                quantity=Decimal("80.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("15.0")
            ),
            StockItem(
                shop_id=shops[0].id,
                item_type=ItemType.RAW_MATERIAL,
                raw_material_id=raw_materials[2].id,  # Denim Fabric
                quantity=Decimal("60.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("10.0")
            ),
            StockItem(
                shop_id=shops[0].id,
                item_type=ItemType.RAW_MATERIAL,
                raw_material_id=raw_materials[3].id,  # Silk Fabric
                quantity=Decimal("20.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("5.0")
            ),
            StockItem(
                shop_id=shops[0].id,
                item_type=ItemType.RAW_MATERIAL,
                raw_material_id=raw_materials[4].id,  # Thread
                quantity=Decimal("200.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("50.0")
            ),
            StockItem(
                shop_id=shops[0].id,
                item_type=ItemType.RAW_MATERIAL,
                raw_material_id=raw_materials[5].id,  # Zippers
                quantity=Decimal("150.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("30.0")
            ),
            
            # Products in main warehouse
            StockItem(
                shop_id=shops[0].id,
                item_type=ItemType.PRODUCT,
                product_id=products[0].id,  # Cotton T-Shirt
                quantity=Decimal("50.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("10.0")
            ),
            StockItem(
                shop_id=shops[0].id,
                item_type=ItemType.PRODUCT,
                product_id=products[1].id,  # Denim Jeans
                quantity=Decimal("30.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("5.0")
            ),
            StockItem(
                shop_id=shops[0].id,
                item_type=ItemType.PRODUCT,
                product_id=products[2].id,  # Silk Blouse
                quantity=Decimal("15.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("3.0")
            ),
            StockItem(
                shop_id=shops[0].id,
                item_type=ItemType.PRODUCT,
                product_id=products[3].id,  # Sport Shorts
                quantity=Decimal("40.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("8.0")
            ),
            StockItem(
                shop_id=shops[0].id,
                item_type=ItemType.PRODUCT,
                product_id=products[4].id,  # Cotton Dress
                quantity=Decimal("25.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("5.0")
            ),
            
            # Products in downtown store
            StockItem(
                shop_id=shops[1].id,  # Downtown Store
                item_type=ItemType.PRODUCT,
                product_id=products[0].id,  # Cotton T-Shirt
                quantity=Decimal("20.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("5.0")
            ),
            StockItem(
                shop_id=shops[1].id,
                item_type=ItemType.PRODUCT,
                product_id=products[1].id,  # Denim Jeans
                quantity=Decimal("15.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("3.0")
            ),
            StockItem(
                shop_id=shops[1].id,
                item_type=ItemType.PRODUCT,
                product_id=products[2].id,  # Silk Blouse
                quantity=Decimal("8.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("2.0")
            ),
            
            # Products in mall branch
            StockItem(
                shop_id=shops[2].id,  # Mall Branch
                item_type=ItemType.PRODUCT,
                product_id=products[0].id,  # Cotton T-Shirt
                quantity=Decimal("15.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("5.0")
            ),
            StockItem(
                shop_id=shops[2].id,
                item_type=ItemType.PRODUCT,
                product_id=products[3].id,  # Sport Shorts
                quantity=Decimal("12.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("3.0")
            ),
            StockItem(
                shop_id=shops[2].id,
                item_type=ItemType.PRODUCT,
                product_id=products[4].id,  # Cotton Dress
                quantity=Decimal("10.0"),
                reserved_quantity=Decimal("0.0"),
                min_stock_level=Decimal("3.0")
            )
        ]
        
        for stock_item in stock_items:
            db.add(stock_item)
        
        await db.commit()
        print("Seed data created successfully!")


if __name__ == "__main__":
    asyncio.run(create_seed_data())
