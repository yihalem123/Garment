"""
Business Intelligence and KPI Tracking routes
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, text, case
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.models import (
    User, Sale, SaleLine, Purchase, PurchaseLine, ProductionRun, 
    StockItem, StockMovement, Shop, Product, RawMaterial,
    ItemType, MovementReason, SaleStatus, ProductionStatus
)
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/kpis")
async def get_key_performance_indicators(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    shop_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get Key Performance Indicators (KPIs) for business management
    
    Returns critical business metrics including:
    - Sales KPIs
    - Inventory KPIs
    - Production KPIs
    - Financial KPIs
    - Operational KPIs
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
    
    # Build base filters
    sales_filter = and_(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == SaleStatus.COMPLETED
    )
    
    if shop_id:
        sales_filter = and_(sales_filter, Sale.shop_id == shop_id)
    
    # Sales KPIs
    sales_kpis_query = select(
        func.count(Sale.id).label("total_transactions"),
        func.sum(Sale.final_amount).label("total_revenue"),
        func.avg(Sale.final_amount).label("avg_transaction_value"),
        func.max(Sale.final_amount).label("max_transaction_value"),
        func.min(Sale.final_amount).label("min_transaction_value")
    ).where(sales_filter)
    
    sales_kpis_result = await db.execute(sales_kpis_query)
    sales_kpis = sales_kpis_result.first()
    
    # Daily sales trend
    daily_sales_query = select(
        Sale.sale_date,
        func.count(Sale.id).label("daily_transactions"),
        func.sum(Sale.final_amount).label("daily_revenue")
    ).where(sales_filter)\
     .group_by(Sale.sale_date)\
     .order_by(Sale.sale_date)
    
    daily_sales_result = await db.execute(daily_sales_query)
    daily_sales = daily_sales_result.all()
    
    # Inventory KPIs
    inventory_kpis_query = select(
        func.count(StockItem.id).label("total_sku_count"),
        func.sum(StockItem.quantity).label("total_inventory_quantity"),
        func.sum(
            case(
                (StockItem.quantity <= StockItem.min_stock_level, 1),
                else_=0
            )
        ).label("low_stock_count")
    )
    
    if shop_id:
        inventory_kpis_query = inventory_kpis_query.where(StockItem.shop_id == shop_id)
    
    inventory_kpis_result = await db.execute(inventory_kpis_query)
    inventory_kpis = inventory_kpis_result.first()
    
    # Production KPIs
    production_kpis_query = select(
        func.count(ProductionRun.id).label("total_production_runs"),
        func.sum(ProductionRun.planned_quantity).label("total_planned_quantity"),
        func.sum(ProductionRun.actual_quantity).label("total_actual_quantity"),
        func.sum(ProductionRun.total_cost).label("total_production_cost"),
        func.avg(ProductionRun.total_cost).label("avg_production_cost")
    ).where(ProductionRun.status == ProductionStatus.COMPLETED)
    
    production_kpis_result = await db.execute(production_kpis_query)
    production_kpis = production_kpis_result.first()
    
    # Calculate efficiency metrics
    production_efficiency = 0
    if production_kpis.total_planned_quantity and production_kpis.total_planned_quantity > 0:
        production_efficiency = float(production_kpis.total_actual_quantity or 0) / float(production_kpis.total_planned_quantity) * 100
    
    # Financial KPIs
    purchase_cost_query = select(func.sum(Purchase.total_amount)).where(
        Purchase.purchase_date >= start_date
    )
    purchase_cost_result = await db.execute(purchase_cost_query)
    total_purchase_cost = purchase_cost_result.scalar_one_or_none() or 0
    
    # Calculate profit margins
    gross_profit = float(sales_kpis.total_revenue or 0) - float(total_purchase_cost)
    profit_margin = (gross_profit / float(sales_kpis.total_revenue or 1)) * 100 if sales_kpis.total_revenue else 0
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "sales_kpis": {
            "total_transactions": sales_kpis.total_transactions or 0,
            "total_revenue": float(sales_kpis.total_revenue or 0),
            "average_transaction_value": float(sales_kpis.avg_transaction_value or 0),
            "max_transaction_value": float(sales_kpis.max_transaction_value or 0),
            "min_transaction_value": float(sales_kpis.min_transaction_value or 0),
            "daily_sales_trend": [
                {
                    "date": str(daily_sale[0]),
                    "transactions": daily_sale[1],
                    "revenue": float(daily_sale[2])
                }
                for daily_sale in daily_sales
            ]
        },
        "inventory_kpis": {
            "total_sku_count": inventory_kpis.total_sku_count or 0,
            "total_inventory_quantity": float(inventory_kpis.total_inventory_quantity or 0),
            "low_stock_count": inventory_kpis.low_stock_count or 0,
            "stock_health_percentage": ((inventory_kpis.total_sku_count or 0) - (inventory_kpis.low_stock_count or 0)) / (inventory_kpis.total_sku_count or 1) * 100
        },
        "production_kpis": {
            "total_production_runs": production_kpis.total_production_runs or 0,
            "total_planned_quantity": float(production_kpis.total_planned_quantity or 0),
            "total_actual_quantity": float(production_kpis.total_actual_quantity or 0),
            "total_production_cost": float(production_kpis.total_production_cost or 0),
            "average_production_cost": float(production_kpis.avg_production_cost or 0),
            "production_efficiency_percentage": production_efficiency
        },
        "financial_kpis": {
            "total_revenue": float(sales_kpis.total_revenue or 0),
            "total_purchase_cost": float(total_purchase_cost),
            "gross_profit": gross_profit,
            "profit_margin_percentage": profit_margin,
            "total_production_cost": float(production_kpis.total_production_cost or 0)
        }
    }


@router.get("/trends")
async def get_business_trends(
    period: str = Query("monthly", description="daily, weekly, monthly"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    shop_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get business trends over time
    
    Returns trend data for:
    - Sales trends
    - Inventory trends
    - Production trends
    - Cost trends
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
        if period == "daily":
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        elif period == "weekly":
            start_date = (datetime.now() - timedelta(weeks=12)).strftime("%Y-%m-%d")
        else:  # monthly
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    # Build date grouping based on period (SQLite compatible)
    if period == "daily":
        date_group = func.date(Sale.sale_date)
    elif period == "weekly":
        # SQLite doesn't have week truncation, use year-week format
        date_group = func.strftime('%Y-%W', Sale.sale_date)
    else:  # monthly
        date_group = func.strftime('%Y-%m', Sale.sale_date)
    
    # Sales trends
    sales_trends_query = select(
        date_group.label("period"),
        func.count(Sale.id).label("transactions"),
        func.sum(Sale.final_amount).label("revenue"),
        func.avg(Sale.final_amount).label("avg_transaction_value")
    ).where(and_(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == SaleStatus.COMPLETED
    ))
    
    if shop_id:
        sales_trends_query = sales_trends_query.where(Sale.shop_id == shop_id)
    
    sales_trends_query = sales_trends_query.group_by(date_group).order_by(date_group)
    
    sales_trends_result = await db.execute(sales_trends_query)
    sales_trends = sales_trends_result.scalars().all()
    
    # Purchase trends
    purchase_trends_query = select(
        date_group.label("period"),
        func.count(Purchase.id).label("purchase_count"),
        func.sum(Purchase.total_amount).label("purchase_amount")
    ).where(and_(
        Purchase.purchase_date >= start_date,
        Purchase.purchase_date <= end_date
    )).group_by(date_group).order_by("period")
    
    purchase_trends_result = await db.execute(purchase_trends_query)
    purchase_trends = purchase_trends_result.scalars().all()
    
    # Production trends
    production_trends_query = select(
        date_group.label("period"),
        func.count(ProductionRun.id).label("production_runs"),
        func.sum(ProductionRun.planned_quantity).label("planned_quantity"),
        func.sum(ProductionRun.actual_quantity).label("actual_quantity"),
        func.sum(ProductionRun.total_cost).label("production_cost")
    ).where(and_(
        ProductionRun.end_date >= start_date,
        ProductionRun.end_date <= end_date,
        ProductionRun.status == ProductionStatus.COMPLETED
    )).group_by(date_group).order_by("period")
    
    production_trends_result = await db.execute(production_trends_query)
    production_trends = production_trends_result.scalars().all()
    
    return {
        "period": period,
        "date_range": {
            "start_date": start_date,
            "end_date": end_date
        },
        "sales_trends": [
            {
                "period": str(trend.period),
                "transactions": trend.transactions,
                "revenue": float(trend.revenue),
                "avg_transaction_value": float(trend.avg_transaction_value)
            }
            for trend in sales_trends
        ],
        "purchase_trends": [
            {
                "period": str(trend.period),
                "purchase_count": trend.purchase_count,
                "purchase_amount": float(trend.purchase_amount)
            }
            for trend in purchase_trends
        ],
        "production_trends": [
            {
                "period": str(trend.period),
                "production_runs": trend.production_runs,
                "planned_quantity": float(trend.planned_quantity),
                "actual_quantity": float(trend.actual_quantity),
                "production_cost": float(trend.production_cost),
                "efficiency": float(trend.actual_quantity or 0) / float(trend.planned_quantity or 1) * 100 if trend.planned_quantity else 0
            }
            for trend in production_trends
        ]
    }


@router.get("/comparative-analysis")
async def get_comparative_analysis(
    period: str = Query("monthly", description="daily, weekly, monthly"),
    comparison_periods: int = Query(3, description="Number of periods to compare"),
    shop_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get comparative analysis across different periods
    
    Returns comparison data for:
    - Period-over-period growth
    - Performance comparisons
    - Trend analysis
    """
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Calculate date ranges for comparison
    end_date = datetime.now()
    
    if period == "daily":
        period_delta = timedelta(days=1)
        start_date = end_date - timedelta(days=comparison_periods)
    elif period == "weekly":
        period_delta = timedelta(weeks=1)
        start_date = end_date - timedelta(weeks=comparison_periods)
    else:  # monthly
        period_delta = timedelta(days=30)
        start_date = end_date - timedelta(days=comparison_periods * 30)
    
    # Build comparison data
    comparison_data = []
    
    for i in range(comparison_periods):
        period_start = start_date + (period_delta * i)
        period_end = period_start + period_delta
        
        # Sales data for this period
        sales_filter = and_(
            Sale.sale_date >= period_start.strftime("%Y-%m-%d"),
            Sale.sale_date < period_end.strftime("%Y-%m-%d"),
            Sale.status == SaleStatus.COMPLETED
        )
        
        if shop_id:
            sales_filter = and_(sales_filter, Sale.shop_id == shop_id)
        
        sales_query = select(
            func.count(Sale.id).label("transactions"),
            func.sum(Sale.final_amount).label("revenue"),
            func.avg(Sale.final_amount).label("avg_transaction_value")
        ).where(sales_filter)
        
        sales_result = await db.execute(sales_query)
        sales_data = sales_result.scalar_one_or_none()
        
        # Purchase data for this period
        purchase_query = select(
            func.count(Purchase.id).label("purchase_count"),
            func.sum(Purchase.total_amount).label("purchase_amount")
        ).where(and_(
            Purchase.purchase_date >= period_start.strftime("%Y-%m-%d"),
            Purchase.purchase_date < period_end.strftime("%Y-%m-%d")
        ))
        
        purchase_result = await db.execute(purchase_query)
        purchase_data = purchase_result.scalar_one_or_none()
        
        comparison_data.append({
            "period": period_start.strftime("%Y-%m-%d"),
            "period_end": period_end.strftime("%Y-%m-%d"),
            "sales": {
                "transactions": sales_data.transactions or 0,
                "revenue": float(sales_data.revenue or 0),
                "avg_transaction_value": float(sales_data.avg_transaction_value or 0)
            },
            "purchases": {
                "purchase_count": purchase_data.purchase_count or 0,
                "purchase_amount": float(purchase_data.purchase_amount or 0)
            }
        })
    
    # Calculate growth rates
    growth_analysis = []
    for i in range(1, len(comparison_data)):
        current = comparison_data[i]
        previous = comparison_data[i-1]
        
        revenue_growth = 0
        if previous["sales"]["revenue"] > 0:
            revenue_growth = ((current["sales"]["revenue"] - previous["sales"]["revenue"]) / previous["sales"]["revenue"]) * 100
        
        transaction_growth = 0
        if previous["sales"]["transactions"] > 0:
            transaction_growth = ((current["sales"]["transactions"] - previous["sales"]["transactions"]) / previous["sales"]["transactions"]) * 100
        
        growth_analysis.append({
            "period": current["period"],
            "revenue_growth_percentage": revenue_growth,
            "transaction_growth_percentage": transaction_growth
        })
    
    return {
        "period": period,
        "comparison_periods": comparison_periods,
        "period_data": comparison_data,
        "growth_analysis": growth_analysis
    }


@router.get("/business-health")
async def get_business_health_score(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get overall business health score and recommendations
    
    Returns:
    - Business health score (0-100)
    - Key metrics status
    - Recommendations for improvement
    """
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Calculate various health metrics
    health_metrics = {}
    recommendations = []
    
    # Inventory Health (30% weight)
    low_stock_query = select(func.count(StockItem.id)).where(
        StockItem.quantity <= StockItem.min_stock_level
    )
    total_stock_query = select(func.count(StockItem.id))
    
    low_stock_result = await db.execute(low_stock_query)
    total_stock_result = await db.execute(total_stock_query)
    
    low_stock_count = low_stock_result.scalar_one_or_none() or 0
    total_stock_count = total_stock_result.scalar_one_or_none() or 1
    
    inventory_health = ((total_stock_count - low_stock_count) / total_stock_count) * 100
    health_metrics["inventory_health"] = inventory_health
    
    if inventory_health < 80:
        recommendations.append("Consider reordering low stock items to maintain optimal inventory levels")
    
    # Sales Health (25% weight)
    recent_sales_query = select(func.count(Sale.id)).where(
        and_(
            Sale.sale_date >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            Sale.status == SaleStatus.COMPLETED
        )
    )
    recent_sales_result = await db.execute(recent_sales_query)
    recent_sales_count = recent_sales_result.scalar_one_or_none() or 0
    
    # Assume healthy if more than 5 sales per week
    sales_health = min(100, (recent_sales_count / 5) * 100)
    health_metrics["sales_health"] = sales_health
    
    if sales_health < 60:
        recommendations.append("Sales activity is low. Consider promotional activities or marketing campaigns")
    
    # Production Health (20% weight)
    production_efficiency_query = select(
        func.sum(ProductionRun.actual_quantity).label("actual"),
        func.sum(ProductionRun.planned_quantity).label("planned")
    ).where(ProductionRun.status == ProductionStatus.COMPLETED)
    
    production_result = await db.execute(production_efficiency_query)
    production_data = production_result.first()
    
    production_efficiency = 0
    if production_data and production_data.planned and production_data.planned > 0:
        production_efficiency = float((production_data.actual / production_data.planned) * 100)
    
    health_metrics["production_health"] = production_efficiency
    
    if production_efficiency < 90:
        recommendations.append("Production efficiency is below target. Review production processes and resource allocation")
    
    # Financial Health (25% weight)
    # Calculate profit margin for last 30 days
    revenue_query = select(func.sum(Sale.final_amount)).where(
        and_(
            Sale.sale_date >= (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            Sale.status == SaleStatus.COMPLETED
        )
    )
    cost_query = select(func.sum(Purchase.total_amount)).where(
        Purchase.purchase_date >= (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    )
    
    revenue_result = await db.execute(revenue_query)
    cost_result = await db.execute(cost_query)
    
    revenue = revenue_result.scalar_one_or_none() or 0
    costs = cost_result.scalar_one_or_none() or 0
    
    profit_margin = 0
    if revenue > 0:
        profit_margin = ((revenue - costs) / revenue) * 100
    
    # Assume healthy if profit margin > 20%
    financial_health = min(100, (profit_margin / 20) * 100)
    health_metrics["financial_health"] = financial_health
    
    if financial_health < 60:
        recommendations.append("Profit margins are low. Review pricing strategy and cost management")
    
    # Calculate overall health score
    overall_health = (
        inventory_health * 0.30 +
        sales_health * 0.25 +
        production_efficiency * 0.20 +
        financial_health * 0.25
    )
    
    # Determine health status
    if overall_health >= 80:
        health_status = "Excellent"
    elif overall_health >= 60:
        health_status = "Good"
    elif overall_health >= 40:
        health_status = "Fair"
    else:
        health_status = "Needs Attention"
    
    return {
        "overall_health_score": overall_health,
        "health_status": health_status,
        "health_metrics": health_metrics,
        "recommendations": recommendations,
        "last_updated": datetime.now().isoformat()
    }
