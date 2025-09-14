"""
Background tasks for notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.celery_app import celery_app
from app.core.config import settings
from app.db.session import async_session_maker
from app.models import StockItem, User, ItemType


@celery_app.task
def send_low_stock_notification():
    """
    Daily task to check for low stock items and send email notifications
    
    This task:
    1. Finds all stock items below minimum stock level
    2. Groups them by shop
    3. Sends email notifications to shop managers and admins
    """
    async def _send_notifications():
        async with async_session_maker() as db:
            # Find low stock items
            statement = select(StockItem).where(
                StockItem.quantity <= StockItem.min_stock_level
            )
            low_stock_items = await db.exec(statement)
            low_stock_items = low_stock_items.all()
            
            if not low_stock_items:
                return {"message": "No low stock items found"}
            
            # Group by shop
            shop_low_stock = {}
            for item in low_stock_items:
                if item.shop_id not in shop_low_stock:
                    shop_low_stock[item.shop_id] = []
                shop_low_stock[item.shop_id].append(item)
            
            # Get shop managers and admins
            statement = select(User).where(
                User.role.in_(["admin", "shop_manager"])
            )
            users = await db.exec(statement)
            users = users.all()
            
            # Send notifications
            notifications_sent = 0
            for user in users:
                if user.email:
                    try:
                        _send_email_notification(user.email, shop_low_stock)
                        notifications_sent += 1
                    except Exception as e:
                        print(f"Failed to send email to {user.email}: {e}")
            
            return {
                "message": f"Low stock notifications sent to {notifications_sent} users",
                "low_stock_items_count": len(low_stock_items),
                "shops_affected": len(shop_low_stock)
            }
    
    # Run the async function
    import asyncio
    return asyncio.run(_send_notifications())


def _send_email_notification(email: str, shop_low_stock: Dict[int, List[StockItem]]):
    """Send email notification about low stock items"""
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        print("SMTP not configured, skipping email notification")
        return
    
    # Create email content
    subject = "Low Stock Alert - Garment Management System"
    
    body = "The following items are below minimum stock levels:\n\n"
    
    for shop_id, items in shop_low_stock.items():
        body += f"Shop ID: {shop_id}\n"
        body += "-" * 30 + "\n"
        
        for item in items:
            item_name = "Unknown Item"
            if item.product_id:
                item_name = f"Product ID: {item.product_id}"
            elif item.raw_material_id:
                item_name = f"Raw Material ID: {item.raw_material_id}"
            
            body += f"• {item_name}\n"
            body += f"  Current Stock: {item.quantity}\n"
            body += f"  Minimum Level: {item.min_stock_level}\n"
            body += f"  Item Type: {item.item_type}\n\n"
        
        body += "\n"
    
    body += "Please review and reorder as necessary.\n\n"
    body += "Best regards,\nGarment Management System"
    
    # Create message
    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USER
    msg["To"] = email
    msg["Subject"] = subject
    
    msg.attach(MIMEText(body, "plain"))
    
    # Send email
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_TLS:
            server.starttls()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(settings.SMTP_USER, email, text)


@celery_app.task
def generate_daily_sales_report(shop_id: int = None):
    """
    Generate daily sales report
    
    This task:
    1. Calculates daily sales totals
    2. Identifies top-selling products
    3. Generates report data
    """
    async def _generate_report():
        async with async_session_maker() as db:
            from app.models import Sale, SaleLine
            from datetime import datetime, timedelta
            
            # Get yesterday's sales
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_str = yesterday.strftime("%Y-%m-%d")
            
            statement = select(Sale).where(Sale.sale_date == yesterday_str)
            if shop_id:
                statement = statement.where(Sale.shop_id == shop_id)
            
            sales = await db.exec(statement)
            sales = sales.all()
            
            total_sales = sum(sale.final_amount for sale in sales)
            total_transactions = len(sales)
            
            # Get top-selling products
            statement = select(SaleLine).join(Sale).where(Sale.sale_date == yesterday_str)
            if shop_id:
                statement = statement.where(Sale.shop_id == shop_id)
            
            sale_lines = await db.exec(statement)
            sale_lines = sale_lines.all()
            
            product_sales = {}
            for line in sale_lines:
                if line.product_id not in product_sales:
                    product_sales[line.product_id] = {"quantity": 0, "revenue": 0}
                product_sales[line.product_id]["quantity"] += line.quantity
                product_sales[line.product_id]["revenue"] += line.total_price
            
            # Sort by revenue
            top_products = sorted(
                product_sales.items(),
                key=lambda x: x[1]["revenue"],
                reverse=True
            )[:10]
            
            return {
                "date": yesterday_str,
                "shop_id": shop_id,
                "total_sales": float(total_sales),
                "total_transactions": total_transactions,
                "top_products": [
                    {
                        "product_id": product_id,
                        "quantity_sold": float(data["quantity"]),
                        "revenue": float(data["revenue"])
                    }
                    for product_id, data in top_products
                ]
            }
    
    import asyncio
    return asyncio.run(_generate_report())


@celery_app.task
def cleanup_old_stock_movements(days_to_keep: int = 90):
    """
    Clean up old stock movement records to keep database size manageable
    
    This task removes stock movement records older than specified days,
    keeping only recent movements for reporting purposes.
    """
    async def _cleanup():
        async with async_session_maker() as db:
            from app.models import StockMovement
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_str = cutoff_date.strftime("%Y-%m-%d")
            
            # Delete old stock movements
            statement = select(StockMovement).where(
                StockMovement.created_at < cutoff_str
            )
            old_movements = await db.exec(statement)
            old_movements = old_movements.all()
            
            deleted_count = len(old_movements)
            
            # Actually delete the records
            for movement in old_movements:
                await db.delete(movement)
            
            await db.commit()
            
            return {
                "message": f"Cleaned up {deleted_count} old stock movement records",
                "cutoff_date": cutoff_str,
                "deleted_count": deleted_count
            }
    
    import asyncio
    return asyncio.run(_cleanup())
