"""
Payroll Management routes
"""
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.models import Employee, PayrollRecord, PayrollSummary, PayrollStatus, Shop, User
from app.schemas.payroll import (
    PayrollRecordCreate, PayrollRecordUpdate, PayrollRecordResponse,
    PayrollSummaryResponse, PayrollProcessingRequest, PayrollPaymentRequest
)
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/records", response_model=List[PayrollRecordResponse])
async def get_payroll_records(
    employee_id: Optional[int] = Query(None),
    shop_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    period_start: Optional[str] = Query(None),
    period_end: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get payroll records with filtering options
    """
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Shop manager can only see payroll for their shop
    if current_user.role == "shop_manager":
        if current_user.shop_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Shop manager must be assigned to a shop"
            )
        shop_id = current_user.shop_id
    
    # Build filters
    filters = []
    if employee_id:
        filters.append(PayrollRecord.employee_id == employee_id)
    if shop_id:
        filters.append(Employee.shop_id == shop_id)
    if status:
        filters.append(PayrollRecord.status == status)
    if period_start:
        filters.append(PayrollRecord.payroll_period_start >= period_start)
    if period_end:
        filters.append(PayrollRecord.payroll_period_end <= period_end)
    
    # Get payroll records with employee information
    query = select(PayrollRecord).options(
        selectinload(PayrollRecord.employee).selectinload(Employee.shop)
    ).where(and_(*filters) if filters else True).order_by(desc(PayrollRecord.payroll_period_start))
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # Format response
    payroll_list = []
    for record in records:
        payroll_list.append(PayrollRecordResponse(
            id=record.id,
            employee_id=record.employee_id,
            employee_name=record.employee.full_name,
            payroll_period_start=record.payroll_period_start,
            payroll_period_end=record.payroll_period_end,
            base_salary=record.base_salary,
            hours_worked=record.hours_worked,
            overtime_hours=record.overtime_hours,
            hourly_rate=record.hourly_rate,
            overtime_rate=record.overtime_rate,
            regular_pay=record.regular_pay,
            overtime_pay=record.overtime_pay,
            commission_pay=record.commission_pay,
            bonus_pay=record.bonus_pay,
            tax_deduction=record.tax_deduction,
            insurance_deduction=record.insurance_deduction,
            other_deductions=record.other_deductions,
            gross_pay=record.gross_pay,
            total_deductions=record.total_deductions,
            net_pay=record.net_pay,
            payment_date=record.payment_date,
            payment_method=record.payment_method,
            payment_reference=record.payment_reference,
            status=record.status,
            notes=record.notes,
            created_at=record.created_at,
            updated_at=record.updated_at
        ))
    
    return payroll_list


@router.post("/process", response_model=PayrollSummaryResponse)
async def process_payroll(
    payroll_request: PayrollProcessingRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Process payroll for a specific period
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    
    # Get active employees for the period
    employee_filters = [Employee.is_active == True]
    if payroll_request.shop_id:
        employee_filters.append(Employee.shop_id == payroll_request.shop_id)
    
    employees_query = select(Employee).where(and_(*employee_filters))
    employees_result = await db.execute(employees_query)
    employees = employees_result.scalars().all()
    
    if not employees:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No employees found for the specified criteria"
        )
    
    # Create payroll records for each employee
    payroll_records = []
    total_gross_pay = Decimal('0')
    total_deductions = Decimal('0')
    total_net_pay = Decimal('0')
    
    for employee in employees:
        # Calculate pay based on employee type
        if employee.hourly_rate:
            # Hourly employee - calculate based on hours worked
            hours_worked = employee.work_hours_per_week * 4  # Assume 4 weeks per month
            regular_pay = employee.hourly_rate * hours_worked
            overtime_hours = max(0, hours_worked - 160)  # Overtime after 40 hours/week
            overtime_pay = overtime_hours * employee.hourly_rate * (employee.overtime_rate or Decimal('1.5'))
        else:
            # Salaried employee
            regular_pay = employee.base_salary
            overtime_pay = None
            hours_worked = None
            overtime_hours = None
        
        # Calculate deductions (simplified)
        tax_deduction = regular_pay * Decimal('0.15')  # 15% tax
        insurance_deduction = regular_pay * Decimal('0.05')  # 5% insurance
        total_deductions_emp = tax_deduction + insurance_deduction
        
        gross_pay = regular_pay + (overtime_pay or Decimal('0'))
        net_pay = gross_pay - total_deductions_emp
        
        # Create payroll record
        payroll_record = PayrollRecord(
            employee_id=employee.id,
            payroll_period_start=payroll_request.period_start,
            payroll_period_end=payroll_request.period_end,
            base_salary=employee.base_salary,
            hours_worked=hours_worked,
            overtime_hours=overtime_hours,
            hourly_rate=employee.hourly_rate,
            overtime_rate=employee.overtime_rate,
            regular_pay=regular_pay,
            overtime_pay=overtime_pay,
            commission_pay=None,
            bonus_pay=None,
            tax_deduction=tax_deduction,
            insurance_deduction=insurance_deduction,
            other_deductions=None,
            gross_pay=gross_pay,
            total_deductions=total_deductions_emp,
            net_pay=net_pay,
            status=PayrollStatus.PENDING
        )
        
        db.add(payroll_record)
        payroll_records.append(payroll_record)
        
        total_gross_pay += gross_pay
        total_deductions += total_deductions_emp
        total_net_pay += net_pay
    
    # Create payroll summary
    payroll_summary = PayrollSummary(
        period_start=payroll_request.period_start,
        period_end=payroll_request.period_end,
        shop_id=payroll_request.shop_id,
        total_employees=len(employees),
        total_gross_pay=total_gross_pay,
        total_deductions=total_deductions,
        total_net_pay=total_net_pay,
        is_processed=True,
        processed_at=datetime.utcnow(),
        processed_by=current_user.id
    )
    
    db.add(payroll_summary)
    await db.commit()
    
    # Get shop name
    shop_name = None
    if payroll_request.shop_id:
        shop_result = await db.execute(select(Shop).where(Shop.id == payroll_request.shop_id))
        shop = shop_result.scalar_one_or_none()
        if shop:
            shop_name = shop.name
    
    return PayrollSummaryResponse(
        id=payroll_summary.id,
        period_start=payroll_summary.period_start,
        period_end=payroll_summary.period_end,
        shop_id=payroll_summary.shop_id,
        shop_name=shop_name,
        total_employees=payroll_summary.total_employees,
        total_gross_pay=payroll_summary.total_gross_pay,
        total_deductions=payroll_summary.total_deductions,
        total_net_pay=payroll_summary.total_net_pay,
        is_processed=payroll_summary.is_processed,
        processed_at=payroll_summary.processed_at,
        processed_by=payroll_summary.processed_by,
        created_at=payroll_summary.created_at
    )


@router.post("/payment", response_model=dict)
async def process_payment(
    payment_request: PayrollPaymentRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Process payment for payroll records
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    
    # Get payroll records
    records_query = select(PayrollRecord).where(
        PayrollRecord.id.in_(payment_request.payroll_record_ids)
    )
    records_result = await db.execute(records_query)
    records = records_result.scalars().all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No payroll records found"
        )
    
    # Update records with payment information
    payment_date = payment_request.payment_date or datetime.utcnow()
    
    for record in records:
        record.payment_date = payment_date
        record.payment_method = payment_request.payment_method
        record.payment_reference = payment_request.payment_reference
        record.status = PayrollStatus.PAID
        record.notes = payment_request.notes
        record.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {
        "message": f"Payment processed for {len(records)} payroll records",
        "payment_date": payment_date,
        "payment_method": payment_request.payment_method,
        "total_amount": sum(float(record.net_pay) for record in records)
    }


@router.get("/summaries", response_model=List[PayrollSummaryResponse])
async def get_payroll_summaries(
    shop_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get payroll summaries
    """
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Shop manager can only see summaries for their shop
    if current_user.role == "shop_manager":
        if current_user.shop_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Shop manager must be assigned to a shop"
            )
        shop_id = current_user.shop_id
    
    # Build filters
    filters = []
    if shop_id:
        filters.append(PayrollSummary.shop_id == shop_id)
    if start_date:
        filters.append(PayrollSummary.period_start >= start_date)
    if end_date:
        filters.append(PayrollSummary.period_end <= end_date)
    
    # Get summaries
    query = select(PayrollSummary).where(and_(*filters) if filters else True).order_by(desc(PayrollSummary.period_start))
    result = await db.execute(query)
    summaries = result.scalars().all()
    
    # Get shop names
    shop_names = {}
    if summaries:
        shop_ids = [s.shop_id for s in summaries if s.shop_id]
        if shop_ids:
            shops_query = select(Shop).where(Shop.id.in_(shop_ids))
            shops_result = await db.execute(shops_query)
            shops = shops_result.scalars().all()
            shop_names = {shop.id: shop.name for shop in shops}
    
    # Format response
    summary_list = []
    for summary in summaries:
        summary_list.append(PayrollSummaryResponse(
            id=summary.id,
            period_start=summary.period_start,
            period_end=summary.period_end,
            shop_id=summary.shop_id,
            shop_name=shop_names.get(summary.shop_id) if summary.shop_id else None,
            total_employees=summary.total_employees,
            total_gross_pay=summary.total_gross_pay,
            total_deductions=summary.total_deductions,
            total_net_pay=summary.total_net_pay,
            is_processed=summary.is_processed,
            processed_at=summary.processed_at,
            processed_by=summary.processed_by,
            created_at=summary.created_at
        ))
    
    return summary_list


@router.get("/statistics/overview")
async def get_payroll_statistics(
    shop_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get payroll statistics overview
    """
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Shop manager can only see statistics for their shop
    if current_user.role == "shop_manager":
        if current_user.shop_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Shop manager must be assigned to a shop"
            )
        shop_id = current_user.shop_id
    
    # Build filters
    filters = []
    if shop_id:
        filters.append(Employee.shop_id == shop_id)
    
    # Get current month statistics
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_end = datetime.now()
    
    current_month_query = select(
        func.sum(PayrollRecord.net_pay).label("total_paid"),
        func.count(PayrollRecord.id).label("records_count"),
        func.avg(PayrollRecord.net_pay).label("avg_pay")
    ).join(Employee).where(
        and_(
            PayrollRecord.payment_date >= current_month_start,
            PayrollRecord.payment_date <= current_month_end,
            PayrollRecord.status == PayrollStatus.PAID,
            *filters
        )
    )
    
    current_month_result = await db.execute(current_month_query)
    current_month_stats = current_month_result.first()
    
    # Get pending payments
    pending_query = select(
        func.sum(PayrollRecord.net_pay).label("total_pending"),
        func.count(PayrollRecord.id).label("pending_count")
    ).join(Employee).where(
        and_(
            PayrollRecord.status == PayrollStatus.PENDING,
            *filters
        )
    )
    
    pending_result = await db.execute(pending_query)
    pending_stats = pending_result.first()
    
    return {
        "current_month": {
            "total_paid": float(current_month_stats.total_paid or 0),
            "records_count": current_month_stats.records_count or 0,
            "average_pay": float(current_month_stats.avg_pay or 0)
        },
        "pending_payments": {
            "total_pending": float(pending_stats.total_pending or 0),
            "pending_count": pending_stats.pending_count or 0
        }
    }
