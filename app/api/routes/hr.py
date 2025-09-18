"""
Human Resource Management routes
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.models import User, Shop, Sale, ProductionRun, UserRole
from app.schemas.auth import UserCreate, UserResponse
from app.api.routes.auth import get_current_user
from app.core.security import get_password_hash

router = APIRouter()


@router.get("/employees")
async def get_employees(
    shop_id: Optional[int] = Query(None),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    department: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of employees with filtering options
    
    Returns employee information including:
    - Basic details (name, email, phone, address)
    - Role and permissions
    - Shop assignment
    - Salary and employment details
    - Performance metrics
    """
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Shop manager can only see employees from their shop
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
        filters.append(User.shop_id == shop_id)
    if role:
        filters.append(User.role == role)
    if is_active is not None:
        filters.append(User.is_active == is_active)
    if department:
        filters.append(User.department == department)
    
    # Get employees with shop information
    query = select(User).options(selectinload(User.shop))
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    employees = result.scalars().all()
    
    # Get performance metrics for each employee
    employee_performance = []
    
    for employee in employees:
        # Sales performance (if employee has sales)
        sales_query = select(
            func.count(Sale.id).label("total_sales"),
            func.sum(Sale.final_amount).label("total_revenue")
        ).where(Sale.shop_id == employee.shop_id)
        
        sales_result = await db.execute(sales_query)
        sales_data = sales_result.first()
        
        # Production performance (if employee is involved in production)
        production_query = select(
            func.count(ProductionRun.id).label("total_production_runs"),
            func.sum(ProductionRun.planned_quantity).label("total_quantity")
        )
        
        production_result = await db.execute(production_query)
        production_data = production_result.first()
        
        employee_performance.append({
            "id": employee.id,
            "email": employee.email,
            "full_name": employee.full_name,
            "role": employee.role,
            "is_active": employee.is_active,
            "shop_id": employee.shop_id,
            "shop_name": employee.shop.name if employee.shop else None,
            "created_at": employee.created_at,
            "performance": {
                "total_sales": sales_data.total_sales or 0,
                "total_revenue": float(sales_data.total_revenue or 0),
                "total_production_runs": production_data.total_production_runs or 0,
                "total_production_quantity": float(production_data.total_quantity or 0)
            }
        })
    
    return {
        "total_employees": len(employee_performance),
        "employees": employee_performance
    }


@router.post("/employees", response_model=UserResponse)
async def create_employee(
    employee_data: UserCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new employee
    
    Only admins can create employees with any role.
    Shop managers can only create staff members for their shop.
    """
    if current_user.role == "admin":
        # Admin can create any role
        pass
    elif current_user.role == "shop_manager":
        # Shop manager can only create staff for their shop
        if employee_data.role != "staff":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Shop managers can only create staff members"
            )
        if employee_data.shop_id != current_user.shop_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Shop managers can only create employees for their own shop"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Check if user already exists
    from app.core.security import get_user_by_email
    existing_user = get_user_by_email(db, employee_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new employee
    hashed_password = get_password_hash(employee_data.password)
    db_employee = User(
        email=employee_data.email,
        hashed_password=hashed_password,
        full_name=employee_data.full_name,
        role=employee_data.role,
        shop_id=employee_data.shop_id
    )
    
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    
    return db_employee


@router.put("/employees/{employee_id}", response_model=UserResponse)
async def update_employee(
    employee_id: int,
    employee_data: dict,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update employee information
    
    Admins can update any employee.
    Shop managers can only update employees in their shop.
    """
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Get employee
    statement = select(User).where(User.id == employee_id)
    result = await db.execute(statement)
    employee = result.scalar_one_or_none()
    # employee is already a single object from scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check permissions
    if current_user.role == "shop_manager":
        if employee.shop_id != current_user.shop_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update employees in your shop"
            )
        # Shop managers can't change roles
        if "role" in employee_data:
            del employee_data["role"]
    
    # Update fields
    for field, value in employee_data.items():
        if hasattr(employee, field):
            setattr(employee, field, value)
    
    await db.commit()
    await db.refresh(employee)
    
    return employee


@router.delete("/employees/{employee_id}")
async def deactivate_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate an employee (soft delete)
    
    Admins can deactivate any employee.
    Shop managers can only deactivate employees in their shop.
    """
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Get employee
    statement = select(User).where(User.id == employee_id)
    result = await db.execute(statement)
    employee = result.scalar_one_or_none()
    # employee is already a single object from scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check permissions
    if current_user.role == "shop_manager":
        if employee.shop_id != current_user.shop_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only deactivate employees in your shop"
            )
    
    # Prevent deactivating self
    if employee.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    # Deactivate employee
    employee.is_active = False
    await db.commit()
    
    return {"message": "Employee deactivated successfully"}


@router.get("/performance")
async def get_employee_performance(
    employee_id: Optional[int] = Query(None),
    shop_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get employee performance metrics
    
    Returns detailed performance data including:
    - Sales performance
    - Production metrics
    - Activity levels
    - Comparative analysis
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
    filters = []
    if employee_id:
        # Get employee's shop
        employee_query = select(User).where(User.id == employee_id)
        result = await db.execute(employee_query)
        employee = result.scalar_one_or_none()
        # employee is already a single object from scalar_one_or_none()
        if employee and employee.shop_id:
            filters.append(Sale.shop_id == employee.shop_id)
    elif shop_id:
        filters.append(Sale.shop_id == shop_id)
    
    # Add date filters
    filters.extend([
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ])
    
    # Sales performance by shop
    sales_query = select(
        Sale.shop_id,
        func.count(Sale.id).label("total_sales"),
        func.sum(Sale.final_amount).label("total_revenue"),
        func.avg(Sale.final_amount).label("avg_sale_amount")
    ).where(and_(*filters))\
     .group_by(Sale.shop_id)
    
    sales_result = await db.execute(sales_query)
    sales_data = sales_result.scalars().all()
    
    # Get shop information
    shops_query = select(Shop)
    result = await db.execute(shops_query)
    shops = result.scalars().all()
    shop_dict = {shop.id: shop.name for shop in shops}
    
    # Production performance
    production_query = select(
        func.count(ProductionRun.id).label("total_runs"),
        func.sum(ProductionRun.planned_quantity).label("total_planned"),
        func.sum(ProductionRun.actual_quantity).label("total_actual"),
        func.sum(ProductionRun.total_cost).label("total_cost")
    ).where(and_(
        ProductionRun.end_date >= start_date,
        ProductionRun.end_date <= end_date,
        ProductionRun.status == "completed"
    ))
    
    production_result = await db.execute(production_query)
    production_data = production_result.first()
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "sales_performance": [
            {
                "shop_id": data.shop_id,
                "shop_name": shop_dict.get(data.shop_id, f"Shop {data.shop_id}"),
                "total_sales": data.total_sales,
                "total_revenue": float(data.total_revenue),
                "average_sale_amount": float(data.avg_sale_amount)
            }
            for data in sales_data
        ],
        "production_performance": {
            "total_runs": production_data.total_runs or 0,
            "total_planned_quantity": float(production_data.total_planned or 0),
            "total_actual_quantity": float(production_data.total_actual or 0),
            "total_cost": float(production_data.total_cost or 0),
            "efficiency": float(production_data.total_actual or 0) / float(production_data.total_planned or 1) * 100 if production_data.total_planned else 0
        }
    }


@router.get("/workforce-summary")
async def get_workforce_summary(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get workforce summary and statistics
    
    Returns:
    - Total employees by role
    - Active vs inactive employees
    - Shop-wise distribution
    - Recent hires
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    
    # Total employees by role
    role_query = select(
        User.role,
        func.count(User.id).label("count")
    ).group_by(User.role)
    
    role_result = await db.execute(role_query)
    role_distribution = role_result.all()
    
    # Active vs inactive
    status_query = select(
        User.is_active,
        func.count(User.id).label("count")
    ).group_by(User.is_active)
    
    status_result = await db.execute(status_query)
    status_distribution = status_result.all()
    
    # Shop-wise distribution
    shop_query = select(
        User.shop_id,
        func.count(User.id).label("count")
    ).group_by(User.shop_id)
    
    shop_result = await db.execute(shop_query)
    shop_distribution = shop_result.all()
    
    # Get shop names
    shops_query = select(Shop)
    result = await db.execute(shops_query)
    shops = result.scalars().all()
    shop_dict = {shop.id: shop.name for shop in shops}
    
    # Recent hires (last 30 days)
    recent_hires_query = select(User).where(
        User.created_at >= datetime.now() - timedelta(days=30)
    ).order_by(desc(User.created_at)).limit(10)
    
    result = await db.execute(recent_hires_query)
    recent_hires = result.scalars().all()
    
    return {
        "role_distribution": [
            {
                "role": role.role,
                "count": role.count
            }
            for role in role_distribution
        ],
        "status_distribution": [
            {
                "status": "active" if status.is_active else "inactive",
                "count": status.count
            }
            for status in status_distribution
        ],
        "shop_distribution": [
            {
                "shop_id": shop.shop_id,
                "shop_name": shop_dict.get(shop.shop_id, f"Shop {shop.shop_id}"),
                "count": shop.count
            }
            for shop in shop_distribution
        ],
        "recent_hires": [
            {
                "id": hire.id,
                "full_name": hire.full_name,
                "email": hire.email,
                "role": hire.role,
                "shop_id": hire.shop_id,
                "shop_name": shop_dict.get(hire.shop_id),
                "created_at": hire.created_at
            }
            for hire in recent_hires
        ]
    }


@router.get("/monthly-costs")
async def get_monthly_costs(
    shop_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get monthly costs including employee salaries
    
    Returns:
    - Total monthly salary costs
    - Breakdown by department
    - Breakdown by shop
    - Individual employee costs
    """
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Shop manager can only see costs for their shop
    if current_user.role == "shop_manager":
        if current_user.shop_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Shop manager must be assigned to a shop"
            )
        shop_id = current_user.shop_id
    
    # Build filters
    filters = [User.is_active == True]
    if shop_id:
        filters.append(User.shop_id == shop_id)
    
    # Get all active employees with salary information
    query = select(User).options(selectinload(User.shop)).where(and_(*filters))
    result = await db.execute(query)
    employees = result.scalars().all()
    
    # Calculate total monthly salary costs
    total_monthly_salary = sum(
        float(emp.salary) if emp.salary else 0 
        for emp in employees
    )
    
    # Breakdown by department
    dept_costs = {}
    for emp in employees:
        if emp.department:
            dept = emp.department
            if dept not in dept_costs:
                dept_costs[dept] = 0
            dept_costs[dept] += float(emp.salary) if emp.salary else 0
    
    # Breakdown by shop
    shop_costs = {}
    for emp in employees:
        if emp.shop:
            shop_name = emp.shop.name
            if shop_name not in shop_costs:
                shop_costs[shop_name] = 0
            shop_costs[shop_name] += float(emp.salary) if emp.salary else 0
    
    # Individual employee costs
    employee_costs = []
    for emp in employees:
        if emp.salary:
            employee_costs.append({
                "id": emp.id,
                "full_name": emp.full_name,
                "position": emp.position,
                "department": emp.department,
                "shop_name": emp.shop.name if emp.shop else "Unassigned",
                "monthly_salary": float(emp.salary),
                "role": emp.role
            })
    
    # Sort by salary (highest first)
    employee_costs.sort(key=lambda x: x["monthly_salary"], reverse=True)
    
    return {
        "total_monthly_salary": total_monthly_salary,
        "employee_count": len(employees),
        "breakdown_by_department": [
            {"department": dept, "total_cost": cost}
            for dept, cost in dept_costs.items()
        ],
        "breakdown_by_shop": [
            {"shop_name": shop, "total_cost": cost}
            for shop, cost in shop_costs.items()
        ],
        "employee_costs": employee_costs,
        "average_salary": total_monthly_salary / len(employees) if employees else 0,
        "highest_paid": employee_costs[0] if employee_costs else None,
        "lowest_paid": employee_costs[-1] if employee_costs else None
    }
