#!/usr/bin/env python3
"""
Script to create realistic sample data for the garment business
"""
import asyncio
import sys
from decimal import Decimal
from datetime import datetime, timedelta
import random

sys.path.append('.')

from app.db.session import get_session
from app.models import (
    User, Shop, Product, RawMaterial, StockItem, 
    Sale, SaleLine, Purchase, PurchaseLine,
    ProductionRun, ProductionLine, Employee,
    ItemType, MovementReason, SaleStatus, ProductionStatus,
    EmploymentStatus, PayrollRecord, PayrollStatus, PurchaseStatus
)
from sqlalchemy import select, delete

async def create_realistic_data():
    async for db in get_session():
        try:
            print("Creating realistic sample data...")

            # Clear existing data
            await db.execute(delete(SaleLine))
            await db.execute(delete(Sale))
            await db.execute(delete(PurchaseLine))
            await db.execute(delete(Purchase))
            await db.execute(delete(StockItem))
            await db.execute(delete(Product))
            await db.execute(delete(RawMaterial))
            await db.execute(delete(Employee))
            await db.execute(delete(Shop))
            await db.commit()

            # 1. Create Shops
            shops = []
            shop_data = [
                {"name": "Main Warehouse", "address": "123 Main St, Addis Ababa", "phone": "+251-11-123-4567"},
                {"name": "Branch Store", "address": "456 Branch Ave, Addis Ababa", "phone": "+251-11-234-5678"},
                {"name": "Outlet Store", "address": "789 Outlet Rd, Addis Ababa", "phone": "+251-11-345-6789"},
            ]
            
            for shop_info in shop_data:
                shop = Shop(**shop_info)
                db.add(shop)
                shops.append(shop)
            
            await db.commit()

            # 2. Create Products with realistic prices
            products = []
            product_data = [
                ("Cotton T-Shirt", "TSH-001", Decimal("150.00"), Decimal("80.00")),
                ("Denim Jeans", "JNS-001", Decimal("450.00"), Decimal("250.00")),
                ("Wool Sweater", "SWT-001", Decimal("350.00"), Decimal("180.00")),
                ("Leather Jacket", "JCK-001", Decimal("1200.00"), Decimal("600.00")),
                ("Silk Dress", "DRS-001", Decimal("800.00"), Decimal("400.00")),
                ("Cotton Pants", "PTS-001", Decimal("200.00"), Decimal("100.00")),
                ("Wool Scarf", "SCF-001", Decimal("80.00"), Decimal("40.00")),
                ("Leather Shoes", "SHO-001", Decimal("600.00"), Decimal("300.00")),
            ]
            
            for name, sku, unit_price, cost_price in product_data:
                product = Product(name=name, sku=sku, unit_price=unit_price, cost_price=cost_price)
                db.add(product)
                products.append(product)
            
            await db.commit()

            # 3. Create Raw Materials
            raw_materials = []
            material_data = [
                ("Cotton Fabric", "FAB-001", Decimal("25.00"), Decimal("15.00")),
                ("Denim Fabric", "FAB-002", Decimal("35.00"), Decimal("20.00")),
                ("Wool Yarn", "YRN-001", Decimal("45.00"), Decimal("25.00")),
                ("Leather", "LTH-001", Decimal("80.00"), Decimal("50.00")),
                ("Silk Fabric", "FAB-003", Decimal("120.00"), Decimal("70.00")),
                ("Cotton Thread", "THR-001", Decimal("5.00"), Decimal("3.00")),
                ("Zippers", "ZIP-001", Decimal("15.00"), Decimal("8.00")),
                ("Buttons", "BTN-001", Decimal("2.00"), Decimal("1.00")),
            ]
            
            for name, sku, unit_price, cost_price in material_data:
                material = RawMaterial(name=name, sku=sku, unit_price=unit_price, cost_price=cost_price)
                db.add(material)
                raw_materials.append(material)
            
            await db.commit()

            # 4. Create Stock Items
            for shop in shops:
                for product in products:
                    stock_item = StockItem(
                        shop_id=shop.id,
                        item_type=ItemType.PRODUCT,
                        product_id=product.id,
                        quantity=Decimal(str(random.randint(20, 100))),
                        reserved_quantity=Decimal("0"),
                        min_stock_level=Decimal("5"),
                        max_stock_level=Decimal("200")
                    )
                    db.add(stock_item)
                
                for material in raw_materials:
                    stock_item = StockItem(
                        shop_id=shop.id,
                        item_type=ItemType.RAW_MATERIAL,
                        raw_material_id=material.id,
                        quantity=Decimal(str(random.randint(50, 200))),
                        reserved_quantity=Decimal("0"),
                        min_stock_level=Decimal("10"),
                        max_stock_level=Decimal("500")
                    )
                    db.add(stock_item)
            
            await db.commit()

            # 5. Create Employees
            employees = []
            employee_data = [
                ("EMP001", "John Doe", "john.doe@garment.com", "+251-91-123-4567", "Store Manager", "Retail", Decimal("4500.00"), shops[0].id),
                ("EMP002", "Jane Smith", "jane.smith@garment.com", "+251-91-234-5678", "Sales Associate", "Retail", Decimal("3200.00"), shops[0].id),
                ("EMP003", "Mike Johnson", "mike.johnson@garment.com", "+251-91-345-6789", "Branch Manager", "Retail", Decimal("5000.00"), shops[1].id),
                ("EMP004", "Sarah Wilson", "sarah.wilson@garment.com", "+251-91-456-7890", "Cashier", "Retail", Decimal("2800.00"), shops[1].id),
                ("EMP005", "David Brown", "david.brown@garment.com", "+251-91-567-8901", "Outlet Manager", "Retail", Decimal("4200.00"), shops[2].id),
            ]
            
            for emp_id, name, email, phone, position, dept, salary, shop_id in employee_data:
                first_name, last_name = name.split(' ', 1) if ' ' in name else (name, '')
                employee = Employee(
                    employee_id=emp_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    position=position,
                    department=dept,
                    employment_status=EmploymentStatus.ACTIVE,
                    base_salary=salary,
                    shop_id=shop_id,
                    hire_date=datetime.now() - timedelta(days=random.randint(30, 365))
                )
                db.add(employee)
                employees.append(employee)
            
            await db.commit()

            # 6. Create realistic sales for the last 3 months
            sales = []
            for month_offset in range(3):  # Last 3 months
                month_start = datetime.now() - timedelta(days=30 * (month_offset + 1))
                month_end = datetime.now() - timedelta(days=30 * month_offset)
                
                # Create 20-40 sales per month
                num_sales = random.randint(20, 40)
                for i in range(num_sales):
                    sale_date = month_start + timedelta(days=random.randint(0, 29))
                    shop = random.choice(shops)
                    
                    sale = Sale(
                        sale_number=f"SALE-{month_offset+1:02d}-{i+1:03d}",
                        shop_id=shop.id,
                        customer_name=f"Customer {i+1}",
                        sale_date=sale_date.strftime("%Y-%m-%d"),
                        total_amount=Decimal("0"),
                        discount_amount=Decimal("0"),
                        final_amount=Decimal("0"),
                        status=SaleStatus.COMPLETED,
                        notes=f"Sale {i+1}"
                    )
                    db.add(sale)
                    sales.append(sale)
            
            await db.commit()

            # 7. Create Sale Lines with realistic quantities
            for sale in sales:
                num_lines = random.randint(1, 4)
                selected_products = random.sample(products, min(num_lines, len(products)))
                
                for product in selected_products:
                    quantity = random.randint(1, 3)
                    unit_price = product.unit_price
                    total_price = unit_price * quantity
                    
                    sale_line = SaleLine(
                        sale_id=sale.id,
                        product_id=product.id,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price
                    )
                    db.add(sale_line)
                
                # Update sale totals
                sale_lines = await db.execute(select(SaleLine).where(SaleLine.sale_id == sale.id))
                lines = sale_lines.scalars().all()
                
                total_amount = sum(line.total_price for line in lines)
                tax_amount = total_amount * Decimal("0.15")  # 15% tax
                final_amount = total_amount + tax_amount
                
                sale.total_amount = total_amount
                sale.final_amount = final_amount
            
            await db.commit()

            # 8. Create realistic purchases
            purchases = []
            for month_offset in range(3):  # Last 3 months
                month_start = datetime.now() - timedelta(days=30 * (month_offset + 1))
                month_end = datetime.now() - timedelta(days=30 * month_offset)
                
                # Create 5-15 purchases per month
                num_purchases = random.randint(5, 15)
                for i in range(num_purchases):
                    purchase_date = month_start + timedelta(days=random.randint(0, 29))
                    shop = random.choice(shops)
                    
                    purchase = Purchase(
                        supplier_name=f"Supplier {i+1}",
                        purchase_date=purchase_date.strftime("%Y-%m-%d"),
                        total_amount=Decimal("0"),
                        status=PurchaseStatus.RECEIVED,
                        notes=f"Purchase {i+1}"
                    )
                    db.add(purchase)
                    purchases.append(purchase)
            
            await db.commit()

            # 9. Create Purchase Lines
            for purchase in purchases:
                num_lines = random.randint(1, 3)
                selected_materials = random.sample(raw_materials, min(num_lines, len(raw_materials)))
                
                for material in selected_materials:
                    quantity = random.randint(10, 100)
                    unit_price = material.unit_price
                    total_price = unit_price * quantity
                    
                    purchase_line = PurchaseLine(
                        purchase_id=purchase.id,
                        raw_material_id=material.id,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price
                    )
                    db.add(purchase_line)
                
                # Update purchase totals
                purchase_lines = await db.execute(select(PurchaseLine).where(PurchaseLine.purchase_id == purchase.id))
                lines = purchase_lines.scalars().all()
                
                total_amount = sum(line.total_price for line in lines)
                
                purchase.total_amount = total_amount
            
            await db.commit()

            # 10. Create Payroll Records for last 3 months
            for employee in employees:
                for month_offset in range(3):
                    payroll_date = datetime.now() - timedelta(days=30 * month_offset)
                    
                    payroll_record = PayrollRecord(
                        employee_id=employee.id,
                        payroll_period_start=payroll_date - timedelta(days=30),
                        payroll_period_end=payroll_date,
                        base_salary=employee.base_salary,
                        regular_pay=employee.base_salary,
                        gross_pay=employee.base_salary,
                        total_deductions=Decimal("0"),
                        net_pay=employee.base_salary,
                        payment_date=payroll_date,
                        status=PayrollStatus.PAID,
                        notes=f"Monthly salary for {employee.first_name} {employee.last_name}"
                    )
                    db.add(payroll_record)
            
            await db.commit()

            print("✅ Realistic sample data created successfully!")
            print(f"📊 Summary:")
            print(f"   - Shops: {len(shops)}")
            print(f"   - Products: {len(products)}")
            print(f"   - Raw Materials: {len(raw_materials)}")
            print(f"   - Sales: {len(sales)}")
            print(f"   - Purchases: {len(purchases)}")
            print(f"   - Employees: {len(employees)}")

        except Exception as e:
            print(f"❌ Error creating realistic data: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(create_realistic_data())
