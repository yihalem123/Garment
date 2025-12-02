"""
Financial Reporting and Analysis routes
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, case
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.models import (
    User, Sale, SaleLine, Purchase, PurchaseLine, ProductionRun, 
    Payment, StockItem, Shop, Product, RawMaterial,
    ItemType, MovementReason, SaleStatus, ProductionStatus, PaymentMethod,
    PayrollRecord, PayrollStatus
)
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/profit-loss-statement")
async def get_profit_loss_statement(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    shop_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive Profit & Loss Statement
    
    Returns detailed financial breakdown including:
    - Revenue breakdown
    - Cost of Goods Sold (COGS)
    - Operating expenses
    - Gross profit and margins
    - Net profit calculations
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
    
    # Build filters
    sales_filter = and_(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == SaleStatus.COMPLETED
    )
    
    if shop_id:
        sales_filter = and_(sales_filter, Sale.shop_id == shop_id)
    
    # REVENUE SECTION
    # Total revenue
    total_revenue_query = select(func.sum(Sale.final_amount)).where(sales_filter)
    total_revenue_result = await db.execute(total_revenue_query)
    total_revenue = total_revenue_result.scalar_one_or_none() or 0
    
    # Revenue by payment method
    revenue_by_payment_query = select(
        Payment.payment_method,
        func.sum(Payment.amount).label("amount")
    ).join(Sale, Payment.sale_id == Sale.id)\
     .where(sales_filter)\
     .group_by(Payment.payment_method)
    
    revenue_by_payment_result = await db.execute(revenue_by_payment_query)
    revenue_by_payment = revenue_by_payment_result.all()
    
    # Revenue by shop
    revenue_by_shop_query = select(
        Sale.shop_id,
        func.sum(Sale.final_amount).label("revenue")
    ).where(sales_filter)\
     .group_by(Sale.shop_id)
    
    revenue_by_shop_result = await db.execute(revenue_by_shop_query)
    revenue_by_shop = revenue_by_shop_result.all()
    
    # Get shop names
    shops_query = select(Shop)
    shops = await db.execute(shops_query)
    shops_list = shops.scalars().all()
    shop_dict = {shop.id: shop.name for shop in shops_list}
    
    # COST OF GOODS SOLD (COGS)
    # Calculate COGS based on product cost prices
    cogs_query = select(
        func.sum(SaleLine.quantity * Product.cost_price).label("total_cogs")
    ).join(Product, SaleLine.product_id == Product.id)\
     .join(Sale, SaleLine.sale_id == Sale.id)\
     .where(sales_filter)
    
    cogs_result = await db.execute(cogs_query)
    total_cogs = cogs_result.scalar_one_or_none() or 0
    
    # OPERATING EXPENSES
    # Raw material purchases
    purchase_filter = and_(
        Purchase.purchase_date >= start_date,
        Purchase.purchase_date <= end_date
    )
    
    purchase_costs_query = select(func.sum(Purchase.total_amount)).where(purchase_filter)
    purchase_costs_result = await db.execute(purchase_costs_query)
    total_purchase_costs = purchase_costs_result.scalar_one_or_none() or 0
    
    # Production costs
    production_filter = and_(
        ProductionRun.end_date >= start_date,
        ProductionRun.end_date <= end_date,
        ProductionRun.status == ProductionStatus.COMPLETED
    )
    
    production_costs_query = select(
        func.sum(ProductionRun.labor_cost).label("labor_cost"),
        func.sum(ProductionRun.overhead_cost).label("overhead_cost")
    ).where(production_filter)
    
    production_costs_result = await db.execute(production_costs_query)
    production_costs = production_costs_result.first()
    
    total_labor_cost = production_costs.labor_cost or 0
    total_overhead_cost = production_costs.overhead_cost or 0
    
    # Get salary costs from payroll records
    salary_costs_query = select(
        func.sum(PayrollRecord.net_pay)
    ).where(
        and_(
            PayrollRecord.payment_date >= start_date,
            PayrollRecord.payment_date <= end_date,
            PayrollRecord.status == PayrollStatus.PAID
        )
    )
    salary_costs_result = await db.execute(salary_costs_query)
    total_salary_costs = salary_costs_result.scalar_one_or_none() or 0
    
    # Calculate profits
    gross_profit = total_revenue - total_cogs
    gross_profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    total_operating_expenses = total_purchase_costs + total_labor_cost + total_overhead_cost + total_salary_costs
    net_profit = gross_profit - total_operating_expenses
    net_profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
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
                    "amount": float(payment.amount)
                }
                for payment in revenue_by_payment
            ],
            "by_shop": [
                {
                    "shop_id": shop[0],
                    "shop_name": shop_dict.get(shop[0], f"Shop {shop[0]}"),
                    "revenue": float(shop[1])
                }
                for shop in revenue_by_shop
            ]
        },
        "cost_of_goods_sold": {
            "total_cogs": float(total_cogs),
            "gross_profit": float(gross_profit),
            "gross_profit_margin": float(gross_profit_margin)
        },
        "operating_expenses": {
            "raw_material_purchases": float(total_purchase_costs),
            "labor_costs": float(total_labor_cost),
            "overhead_costs": float(total_overhead_cost),
            "salary_costs": float(total_salary_costs),
            "total_operating_expenses": float(total_operating_expenses)
        },
        "net_profit": {
            "net_profit": float(net_profit),
            "net_profit_margin": float(net_profit_margin)
        }
    }


@router.get("/cash-flow-statement")
async def get_cash_flow_statement(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    shop_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get Cash Flow Statement
    
    Returns cash flow analysis including:
    - Operating cash flow
    - Investing cash flow
    - Financing cash flow
    - Net cash flow
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
    
    # OPERATING CASH FLOW
    # Cash from sales
    sales_filter = and_(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == SaleStatus.COMPLETED
    )
    
    if shop_id:
        sales_filter = and_(sales_filter, Sale.shop_id == shop_id)
    
    cash_sales_query = select(func.sum(Payment.amount)).join(Sale, Payment.sale_id == Sale.id)\
        .where(and_(sales_filter, Payment.payment_method == PaymentMethod.CASH))
    
    cash_sales_result = await db.execute(cash_sales_query)
    cash_from_sales = cash_sales_result.scalar_one_or_none() or 0
    
    # Bank transfer sales
    bank_transfer_sales_query = select(func.sum(Payment.amount)).join(Sale, Payment.sale_id == Sale.id)\
        .where(and_(sales_filter, Payment.payment_method == PaymentMethod.BANK_TRANSFER))
    
    bank_transfer_sales_result = await db.execute(bank_transfer_sales_query)
    bank_transfer_from_sales = bank_transfer_sales_result.scalar_one_or_none() or 0
    
    # Cash paid for purchases
    purchase_filter = and_(
        Purchase.purchase_date >= start_date,
        Purchase.purchase_date <= end_date
    )
    
    cash_paid_for_purchases_query = select(func.sum(Purchase.total_amount)).where(purchase_filter)
    cash_paid_for_purchases_result = await db.execute(cash_paid_for_purchases_query)
    cash_paid_for_purchases = cash_paid_for_purchases_result.scalar_one_or_none() or 0
    
    # Cash paid for production
    production_filter = and_(
        ProductionRun.end_date >= start_date,
        ProductionRun.end_date <= end_date,
        ProductionRun.status == ProductionStatus.COMPLETED
    )
    
    production_cash_query = select(
        func.sum(ProductionRun.labor_cost + ProductionRun.overhead_cost)
    ).where(production_filter)
    
    production_cash_result = await db.execute(production_cash_query)
    cash_paid_for_production = production_cash_result.scalar_one_or_none() or 0
    
    # Calculate operating cash flow
    operating_cash_flow = cash_from_sales + bank_transfer_from_sales - cash_paid_for_purchases - cash_paid_for_production
    
    # INVESTING CASH FLOW
    # For garment business, this might include equipment purchases, etc.
    # For now, we'll set this to 0 as we don't have equipment tracking
    investing_cash_flow = 0
    
    # FINANCING CASH FLOW
    # This would include loans, investments, etc.
    # For now, we'll set this to 0
    financing_cash_flow = 0
    
    # Net cash flow
    net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "operating_cash_flow": {
            "cash_from_sales": float(cash_from_sales),
            "bank_transfer_from_sales": float(bank_transfer_from_sales),
            "cash_paid_for_purchases": float(cash_paid_for_purchases),
            "cash_paid_for_production": float(cash_paid_for_production),
            "net_operating_cash_flow": float(operating_cash_flow)
        },
        "investing_cash_flow": {
            "net_investing_cash_flow": float(investing_cash_flow)
        },
        "financing_cash_flow": {
            "net_financing_cash_flow": float(financing_cash_flow)
        },
        "net_cash_flow": float(net_cash_flow)
    }


@router.get("/balance-sheet")
async def get_balance_sheet(
    as_of_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get Balance Sheet
    
    Returns balance sheet including:
    - Assets (Current and Fixed)
    - Liabilities
    - Equity
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    
    # Set default date
    if not as_of_date:
        as_of_date = datetime.now().strftime("%Y-%m-%d")
    
    # CURRENT ASSETS
    # Inventory value
    inventory_query = select(
        func.sum(
            case(
                (StockItem.item_type == ItemType.PRODUCT, StockItem.quantity * Product.cost_price),
                (StockItem.item_type == ItemType.RAW_MATERIAL, StockItem.quantity * RawMaterial.unit_price),
                else_=0
            )
        ).label("inventory_value")
    ).outerjoin(Product, StockItem.product_id == Product.id)\
     .outerjoin(RawMaterial, StockItem.raw_material_id == RawMaterial.id)
    
    inventory_result = await db.execute(inventory_query)
    inventory_value = inventory_result.scalar_one_or_none() or 0
    
    # Cash and bank balances (simplified - based on recent payments)
    cash_balance_query = select(func.sum(Payment.amount)).where(
        and_(
            Payment.payment_method == PaymentMethod.CASH,
            Payment.payment_date >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        )
    )
    
    bank_balance_query = select(func.sum(Payment.amount)).where(
        and_(
            Payment.payment_method == PaymentMethod.BANK_TRANSFER,
            Payment.payment_date >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        )
    )
    
    cash_balance_result = await db.execute(cash_balance_query)
    bank_balance_result = await db.execute(bank_balance_query)
    
    cash_balance = cash_balance_result.scalar_one_or_none() or 0
    bank_balance = bank_balance_result.scalar_one_or_none() or 0
    
    # Accounts receivable (simplified - based on recent sales without payments)
    # This is a simplified calculation
    accounts_receivable = 0  # Would need more complex logic for actual receivables
    
    total_current_assets = inventory_value + cash_balance + bank_balance + accounts_receivable
    
    # FIXED ASSETS
    # For garment business, this might include equipment, machinery, etc.
    # For now, we'll set this to 0
    total_fixed_assets = 0
    
    total_assets = total_current_assets + total_fixed_assets
    
    # LIABILITIES
    # Accounts payable (simplified - based on recent purchases)
    # This is a simplified calculation
    accounts_payable = 0  # Would need more complex logic for actual payables
    
    total_liabilities = accounts_payable
    
    # EQUITY
    # Owner's equity = Assets - Liabilities
    owners_equity = total_assets - total_liabilities
    
    return {
        "as_of_date": as_of_date,
        "assets": {
            "current_assets": {
                "inventory": float(inventory_value),
                "cash": float(cash_balance),
                "bank_balance": float(bank_balance),
                "accounts_receivable": float(accounts_receivable),
                "total_current_assets": float(total_current_assets)
            },
            "fixed_assets": {
                "total_fixed_assets": float(total_fixed_assets)
            },
            "total_assets": float(total_assets)
        },
        "liabilities": {
            "accounts_payable": float(accounts_payable),
            "total_liabilities": float(total_liabilities)
        },
        "equity": {
            "owners_equity": float(owners_equity)
        },
        "balance_check": {
            "assets": float(total_assets),
            "liabilities_plus_equity": float(total_liabilities + owners_equity),
            "balanced": abs(total_assets - (total_liabilities + owners_equity)) < 0.01
        }
    }


@router.get("/financial-ratios")
async def get_financial_ratios(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get Financial Ratios Analysis
    
    Returns key financial ratios including:
    - Profitability ratios
    - Liquidity ratios
    - Efficiency ratios
    - Growth ratios
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
    
    # Get financial data
    sales_filter = and_(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == SaleStatus.COMPLETED
    )
    
    # Revenue and costs
    revenue_query = select(func.sum(Sale.final_amount)).where(sales_filter)
    revenue_result = await db.execute(revenue_query)
    revenue = revenue_result.scalar_one_or_none() or 0
    
    # COGS
    cogs_query = select(
        func.sum(SaleLine.quantity * Product.cost_price)
    ).join(Product, SaleLine.product_id == Product.id)\
     .join(Sale, SaleLine.sale_id == Sale.id)\
     .where(sales_filter)
    
    cogs_result = await db.execute(cogs_query)
    cogs = cogs_result.scalar_one_or_none() or 0
    
    # Operating expenses
    purchase_costs_query = select(func.sum(Purchase.total_amount)).where(
        Purchase.purchase_date >= start_date
    )
    purchase_costs_result = await db.execute(purchase_costs_query)
    purchase_costs = purchase_costs_result.scalar_one_or_none() or 0
    
    production_costs_query = select(
        func.sum(ProductionRun.labor_cost + ProductionRun.overhead_cost)
    ).where(and_(
        ProductionRun.end_date >= start_date,
        ProductionRun.status == ProductionStatus.COMPLETED
    ))
    production_costs_result = await db.execute(production_costs_query)
    production_costs = production_costs_result.scalar_one_or_none() or 0
    
    total_operating_expenses = purchase_costs + production_costs
    
    # Calculate ratios
    gross_profit = revenue - cogs
    net_profit = gross_profit - total_operating_expenses
    
    # Profitability Ratios
    gross_profit_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
    net_profit_margin = (net_profit / revenue * 100) if revenue > 0 else 0
    operating_margin = ((gross_profit - total_operating_expenses) / revenue * 100) if revenue > 0 else 0
    
    # Efficiency Ratios
    # Inventory turnover (simplified)
    avg_inventory_query = select(func.avg(StockItem.quantity)).where(
        StockItem.item_type == ItemType.PRODUCT
    )
    avg_inventory_result = await db.execute(avg_inventory_query)
    avg_inventory = avg_inventory_result.scalar_one_or_none() or 1
    
    inventory_turnover = float(cogs) / float(avg_inventory) if avg_inventory > 0 else 0
    
    # Sales per transaction
    transaction_count_query = select(func.count(Sale.id)).where(sales_filter)
    transaction_count_result = await db.execute(transaction_count_query)
    transaction_count = transaction_count_result.scalar_one_or_none() or 1
    
    sales_per_transaction = revenue / transaction_count
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "profitability_ratios": {
            "gross_profit_margin": float(gross_profit_margin),
            "net_profit_margin": float(net_profit_margin),
            "operating_margin": float(operating_margin)
        },
        "efficiency_ratios": {
            "inventory_turnover": float(inventory_turnover),
            "sales_per_transaction": float(sales_per_transaction)
        },
        "financial_data": {
            "revenue": float(revenue),
            "cost_of_goods_sold": float(cogs),
            "gross_profit": float(gross_profit),
            "operating_expenses": float(total_operating_expenses),
            "net_profit": float(net_profit),
            "transaction_count": transaction_count
        }
    }
