"""
Business Analytics and Reporting routes
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.models import (
    User, Sale, SaleLine, Purchase, PurchaseLine, ProductionRun, 
    StockItem, StockMovement, Shop, Product, RawMaterial,
    ItemType, MovementReason, SaleStatus, ProductionStatus
)
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/dashboard")
async def get_business_dashboard(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    shop_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive business dashboard data
    
    Returns key business metrics including:
    - Sales performance
    - Inventory status
    - Production metrics
    - Financial overview
    - Top products
    - Low stock alerts
    """
    # Check if user is admin or shop manager
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Set default date range if not provided
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Build date filter
    date_filter = and_(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    )
    
    if shop_id:
        date_filter = and_(date_filter, Sale.shop_id == shop_id)
    
    # Sales Performance
    sales_query = select(
        func.count(Sale.id).label("total_sales"),
        func.sum(Sale.final_amount).label("total_revenue"),
        func.avg(Sale.final_amount).label("avg_sale_amount")
    ).where(and_(date_filter, Sale.status == SaleStatus.COMPLETED))
    
    sales_result = await db.execute(sales_query)
    sales_stats = sales_result.first()
    
    
    # Top Selling Products
    top_products_query = select(
        Product.name,
        Product.sku,
        func.sum(SaleLine.quantity).label("total_quantity"),
        func.sum(SaleLine.total_price).label("total_revenue")
    ).join(SaleLine, Product.id == SaleLine.product_id)\
     .join(Sale, SaleLine.sale_id == Sale.id)\
     .where(and_(date_filter, Sale.status == SaleStatus.COMPLETED))\
     .group_by(Product.id, Product.name, Product.sku)\
     .order_by(desc("total_revenue"))\
     .limit(10)
    
    top_products = await db.execute(top_products_query)
    top_products_list = top_products.all()
    
    # Inventory Status
    inventory_query = select(
        func.count(StockItem.id).label("total_items"),
        func.sum(StockItem.quantity).label("total_quantity"),
        func.sum(StockItem.quantity * StockItem.min_stock_level).label("total_value")
    )
    
    if shop_id:
        inventory_query = inventory_query.where(StockItem.shop_id == shop_id)
    
    inventory_result = await db.execute(inventory_query)
    inventory_stats = inventory_result.first()
    
    # Low Stock Items
    low_stock_query = select(StockItem).where(
        StockItem.quantity <= StockItem.min_stock_level
    )
    
    if shop_id:
        low_stock_query = low_stock_query.where(StockItem.shop_id == shop_id)
    
    low_stock_items = await db.execute(low_stock_query)
    low_stock_list = low_stock_items.scalars().all()
    
    # Production Status
    production_query = select(
        func.count(ProductionRun.id).label("total_runs"),
        func.sum(ProductionRun.planned_quantity).label("total_planned"),
        func.sum(ProductionRun.actual_quantity).label("total_actual"),
        func.sum(ProductionRun.total_cost).label("total_cost")
    ).where(ProductionRun.status == ProductionStatus.COMPLETED)
    
    production_result = await db.execute(production_query)
    production_stats = production_result.first()
    
    # Recent Activities
    recent_sales_query = select(Sale).where(date_filter)\
        .order_by(desc(Sale.created_at)).limit(5)
    recent_sales = await db.execute(recent_sales_query)
    recent_sales_list = recent_sales.scalars().all()
    
    # Monthly Employee Costs
    employee_costs_query = select(
        func.sum(User.salary).label("total_monthly_salary"),
        func.count(User.id).label("employee_count")
    ).where(User.is_active == True)
    
    if shop_id:
        employee_costs_query = employee_costs_query.where(User.shop_id == shop_id)
    
    employee_costs_result = await db.execute(employee_costs_query)
    employee_costs_stats = employee_costs_result.first()
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "sales_performance": {
            "total_sales": sales_stats.total_sales or 0,
            "total_revenue": float(sales_stats.total_revenue or 0),
            "average_sale_amount": float(sales_stats.avg_sale_amount or 0)
        },
        "inventory_status": {
            "total_items": inventory_stats.total_items or 0,
            "total_quantity": float(inventory_stats.total_quantity or 0),
            "low_stock_items": len(low_stock_list)
        },
        "production_metrics": {
            "total_runs": production_stats.total_runs or 0,
            "total_planned_quantity": float(production_stats.total_planned or 0),
            "total_actual_quantity": float(production_stats.total_actual or 0),
            "total_production_cost": float(production_stats.total_cost or 0)
        },
        "top_products": [
            {
                "name": product.name,
                "sku": product.sku,
                "total_quantity": float(product.total_quantity),
                "total_revenue": float(product.total_revenue)
            }
            for product in top_products_list
        ],
        "low_stock_alerts": [
            {
                "id": item.id,
                "item_type": item.item_type,
                "product_id": item.product_id,
                "raw_material_id": item.raw_material_id,
                "current_quantity": float(item.quantity),
                "min_stock_level": float(item.min_stock_level),
                "shop_id": item.shop_id
            }
            for item in low_stock_list
        ],
        "recent_activities": [
            {
                "id": sale.id,
                "sale_number": sale.sale_number,
                "customer_name": sale.customer_name,
                "final_amount": float(sale.final_amount),
                "sale_date": sale.sale_date,
                "shop_id": sale.shop_id
            }
            for sale in recent_sales_list
        ],
        "monthly_costs": {
            "total_employee_salary": float(employee_costs_stats.total_monthly_salary or 0),
            "employee_count": employee_costs_stats.employee_count or 0,
            "average_salary": float(employee_costs_stats.total_monthly_salary or 0) / max(employee_costs_stats.employee_count or 1, 1)
        }
    }


@router.get("/profit-loss")
async def get_profit_loss_analysis(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    shop_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive profit and loss analysis
    
    Calculates:
    - Total revenue from sales
    - Cost of goods sold (COGS)
    - Production costs
    - Purchase costs
    - Gross profit and margins
    """
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Set default date range
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Revenue from Sales
    sales_filter = and_(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == SaleStatus.COMPLETED
    )
    
    if shop_id:
        sales_filter = and_(sales_filter, Sale.shop_id == shop_id)
    
    revenue_query = select(func.sum(Sale.final_amount)).where(sales_filter)
    revenue_result = await db.execute(revenue_query)
    total_revenue = revenue_result.scalar_one_or_none() or 0
    
    # Cost of Goods Sold (COGS) - based on product cost prices
    cogs_query = select(
        func.sum(SaleLine.quantity * Product.cost_price)
    ).join(Product, SaleLine.product_id == Product.id)\
     .join(Sale, SaleLine.sale_id == Sale.id)\
     .where(sales_filter)
    
    cogs_result = await db.execute(cogs_query)
    total_cogs = cogs_result.scalar_one_or_none() or 0
    
    # Production Costs
    production_filter = and_(
        ProductionRun.end_date >= start_date,
        ProductionRun.end_date <= end_date,
        ProductionRun.status == ProductionStatus.COMPLETED
    )
    
    production_cost_query = select(func.sum(ProductionRun.total_cost)).where(production_filter)
    production_cost_result = await db.execute(production_cost_query)
    total_production_cost = production_cost_result.scalar_one_or_none() or 0
    
    # Purchase Costs
    purchase_filter = and_(
        Purchase.purchase_date >= start_date,
        Purchase.purchase_date <= end_date
    )
    
    purchase_cost_query = select(func.sum(Purchase.total_amount)).where(purchase_filter)
    purchase_cost_result = await db.execute(purchase_cost_query)
    total_purchase_cost = purchase_cost_result.scalar_one_or_none() or 0
    
    # Calculate profits and margins
    gross_profit = total_revenue - total_cogs
    gross_profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    net_profit = gross_profit - total_production_cost
    net_profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "revenue": {
            "total_revenue": float(total_revenue),
            "sales_count": 0  # Could be calculated separately
        },
        "costs": {
            "cost_of_goods_sold": float(total_cogs),
            "production_costs": float(total_production_cost),
            "purchase_costs": float(total_purchase_cost),
            "total_costs": float(total_cogs + total_production_cost + total_purchase_cost)
        },
        "profitability": {
            "gross_profit": float(gross_profit),
            "gross_profit_margin": float(gross_profit_margin),
            "net_profit": float(net_profit),
            "net_profit_margin": float(net_profit_margin)
        }
    }


@router.get("/inventory-report")
async def get_inventory_report(
    shop_id: Optional[int] = Query(None),
    item_type: Optional[str] = Query(None),
    low_stock_only: bool = Query(False),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive inventory report
    
    Returns detailed inventory information including:
    - Stock levels by shop and item type
    - Value calculations
    - Movement history
    - Low stock alerts
    """
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Build filters
    filters = []
    if shop_id:
        filters.append(StockItem.shop_id == shop_id)
    if item_type:
        filters.append(StockItem.item_type == item_type)
    if low_stock_only:
        filters.append(StockItem.quantity <= StockItem.min_stock_level)
    
    # Get inventory items with related data
    query = select(StockItem).options(
        selectinload(StockItem.product),
        selectinload(StockItem.raw_material),
        selectinload(StockItem.shop)
    )
    
    if filters:
        query = query.where(and_(*filters))
    
    inventory_items = await db.execute(query)
    items_list = inventory_items.scalars().all()
    
    # Calculate total values
    total_items = len(items_list)
    total_quantity = sum(float(item.quantity) for item in items_list)
    low_stock_count = sum(1 for item in items_list if item.quantity <= item.min_stock_level)
    
    # Group by shop and item type
    shop_summary = {}
    item_type_summary = {}
    
    for item in items_list:
        # Shop summary
        if item.shop_id not in shop_summary:
            shop_summary[item.shop_id] = {
                "shop_name": item.shop.name if item.shop else f"Shop {item.shop_id}",
                "total_items": 0,
                "total_quantity": 0,
                "low_stock_items": 0
            }
        
        shop_summary[item.shop_id]["total_items"] += 1
        shop_summary[item.shop_id]["total_quantity"] += float(item.quantity)
        if item.quantity <= item.min_stock_level:
            shop_summary[item.shop_id]["low_stock_items"] += 1
        
        # Item type summary
        if item.item_type not in item_type_summary:
            item_type_summary[item.item_type] = {
                "total_items": 0,
                "total_quantity": 0,
                "low_stock_items": 0
            }
        
        item_type_summary[item.item_type]["total_items"] += 1
        item_type_summary[item.item_type]["total_quantity"] += float(item.quantity)
        if item.quantity <= item.min_stock_level:
            item_type_summary[item.item_type]["low_stock_items"] += 1
    
    return {
        "summary": {
            "total_items": total_items,
            "total_quantity": total_quantity,
            "low_stock_items": low_stock_count
        },
        "shop_summary": shop_summary,
        "item_type_summary": item_type_summary,
        "inventory_items": [
            {
                "id": item.id,
                "shop_id": item.shop_id,
                "shop_name": item.shop.name if item.shop else None,
                "item_type": item.item_type,
                "product_id": item.product_id,
                "product_name": item.product.name if item.product else None,
                "raw_material_id": item.raw_material_id,
                "raw_material_name": item.raw_material.name if item.raw_material else None,
                "quantity": float(item.quantity),
                "reserved_quantity": float(item.reserved_quantity),
                "available_quantity": float(item.quantity - item.reserved_quantity),
                "min_stock_level": float(item.min_stock_level),
                "is_low_stock": item.quantity <= item.min_stock_level
            }
            for item in items_list
        ]
    }


@router.get("/financial-summary")
async def get_financial_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive financial summary
    
    Returns:
    - Revenue breakdown
    - Cost analysis
    - Cash flow indicators
    - Financial ratios
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    
    # Set default date range
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Revenue by payment method
    revenue_by_payment_query = select(
        func.sum(Payment.amount).label("total_amount"),
        Payment.payment_method
    ).join(Sale, Payment.sale_id == Sale.id)\
     .where(and_(
         Sale.sale_date >= start_date,
         Sale.sale_date <= end_date,
         Sale.status == SaleStatus.COMPLETED
     ))\
     .group_by(Payment.payment_method)
    
    revenue_by_payment = await db.execute(revenue_by_payment_query)
    payment_breakdown = revenue_by_payment.scalars().all()
    
    # Total revenue
    total_revenue_query = select(func.sum(Sale.final_amount)).where(and_(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == SaleStatus.COMPLETED
    ))
    total_revenue_result = await db.execute(total_revenue_query)
    total_revenue = total_revenue_result.scalar_one_or_none() or 0
    
    # Total costs
    total_costs_query = select(
        func.sum(Purchase.total_amount).label("purchase_costs"),
        func.sum(ProductionRun.total_cost).label("production_costs")
    ).where(and_(
        or_(
            Purchase.purchase_date >= start_date,
            ProductionRun.end_date >= start_date
        )
    ))
    
    costs_result = await db.execute(total_costs_query)
    costs_data = costs_result.scalar_one_or_none()
    
    total_costs = (costs_data.purchase_costs or 0) + (costs_data.production_costs or 0)
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "revenue": {
            "total_revenue": float(total_revenue),
            "by_payment_method": [
                {
                    "payment_method": payment.payment_method,
                    "amount": float(payment.total_amount)
                }
                for payment in payment_breakdown
            ]
        },
        "costs": {
            "purchase_costs": float(costs_data.purchase_costs or 0),
            "production_costs": float(costs_data.production_costs or 0),
            "total_costs": float(total_costs)
        },
        "profitability": {
            "gross_profit": float(total_revenue - total_costs),
            "profit_margin": float((total_revenue - total_costs) / total_revenue * 100) if total_revenue > 0 else 0
        }
    }
