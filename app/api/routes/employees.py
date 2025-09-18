"""
Employee Management routes
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.models import Employee, Shop, User, EmploymentStatus
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[EmployeeListResponse])
async def get_employees(
    shop_id: Optional[int] = Query(None),
    department: Optional[str] = Query(None),
    employment_status: Optional[str] = Query(None),
    position: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of employees with filtering options
    
    Returns employee information including:
    - Basic details (name, email, position, department)
    - Salary information
    - Shop assignment
    - Employment status
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
    filters = [Employee.is_active == True]
    if shop_id:
        filters.append(Employee.shop_id == shop_id)
    if department:
        filters.append(Employee.department == department)
    if employment_status:
        filters.append(Employee.employment_status == employment_status)
    if position:
        filters.append(Employee.position.ilike(f"%{position}%"))
    if search:
        search_filter = or_(
            Employee.first_name.ilike(f"%{search}%"),
            Employee.last_name.ilike(f"%{search}%"),
            Employee.employee_id.ilike(f"%{search}%"),
            Employee.email.ilike(f"%{search}%")
        )
        filters.append(search_filter)
    
    # Get employees with shop and manager information
    query = select(Employee).options(
        selectinload(Employee.shop),
        selectinload(Employee.manager)
    ).where(and_(*filters)).order_by(Employee.last_name, Employee.first_name)
    
    result = await db.execute(query)
    employees = result.scalars().all()
    
    # Format response
    employee_list = []
    for emp in employees:
        employee_list.append(EmployeeListResponse(
            id=emp.id,
            employee_id=emp.employee_id,
            full_name=emp.full_name,
            email=emp.email,
            position=emp.position,
            department=emp.department,
            employment_status=emp.employment_status,
            base_salary=emp.base_salary,
            shop_name=emp.shop.name if emp.shop else None,
            manager_name=emp.manager.full_name if emp.manager else None,
            hire_date=emp.hire_date
        ))
    
    return employee_list


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed employee information
    """
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Get employee with relationships
    query = select(Employee).options(
        selectinload(Employee.shop),
        selectinload(Employee.manager)
    ).where(Employee.id == employee_id)
    
    result = await db.execute(query)
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Shop manager can only see employees from their shop
    if current_user.role == "shop_manager":
        if current_user.shop_id != employee.shop_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Can only view employees from your shop."
            )
    
    return employee


@router.post("/", response_model=EmployeeResponse)
async def create_employee(
    employee_data: EmployeeCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new employee
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    
    # Check if employee ID already exists
    existing_employee = await db.execute(
        select(Employee).where(Employee.employee_id == employee_data.employee_id)
    )
    if existing_employee.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already exists"
        )
    
    # Check if email already exists
    existing_email = await db.execute(
        select(Employee).where(Employee.email == employee_data.email)
    )
    if existing_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create employee
    employee = Employee(
        employee_id=employee_data.employee_id,
        first_name=employee_data.first_name,
        last_name=employee_data.last_name,
        email=employee_data.email,
        phone=employee_data.phone,
        address=employee_data.address,
        position=employee_data.position,
        department=employee_data.department,
        base_salary=employee_data.base_salary,
        hourly_rate=employee_data.hourly_rate,
        overtime_rate=employee_data.overtime_rate,
        commission_rate=employee_data.commission_rate,
        work_hours_per_week=employee_data.work_hours_per_week,
        shop_id=employee_data.shop_id,
        manager_id=employee_data.manager_id,
        hire_date=employee_data.hire_date,
        employment_status=EmploymentStatus.ACTIVE
    )
    
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Update employee information
    """
    if current_user.role not in ["admin", "shop_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin or shop manager role required."
        )
    
    # Get employee
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Shop manager can only update employees from their shop
    if current_user.role == "shop_manager":
        if current_user.shop_id != employee.shop_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Can only update employees from your shop."
            )
    
    # Update fields
    update_data = employee_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)
    
    employee.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(employee)
    
    return employee


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete employee (soft delete)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin role required."
        )
    
    # Get employee
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Soft delete
    employee.is_active = False
    employee.employment_status = EmploymentStatus.TERMINATED
    employee.termination_date = datetime.utcnow()
    employee.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Employee deleted successfully"}


@router.get("/statistics/summary")
async def get_employee_statistics(
    shop_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Get employee statistics
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
    filters = [Employee.is_active == True]
    if shop_id:
        filters.append(Employee.shop_id == shop_id)
    
    # Total employees
    total_query = select(func.count(Employee.id)).where(and_(*filters))
    total_result = await db.execute(total_query)
    total_employees = total_result.scalar()
    
    # By department
    dept_query = select(
        Employee.department,
        func.count(Employee.id).label("count")
    ).where(and_(*filters)).group_by(Employee.department)
    dept_result = await db.execute(dept_query)
    dept_stats = dept_result.all()
    
    # By employment status
    status_query = select(
        Employee.employment_status,
        func.count(Employee.id).label("count")
    ).where(and_(*filters)).group_by(Employee.employment_status)
    status_result = await db.execute(status_query)
    status_stats = status_result.all()
    
    # Salary statistics
    salary_query = select(
        func.sum(Employee.base_salary).label("total_salary"),
        func.avg(Employee.base_salary).label("avg_salary"),
        func.min(Employee.base_salary).label("min_salary"),
        func.max(Employee.base_salary).label("max_salary")
    ).where(and_(*filters))
    salary_result = await db.execute(salary_query)
    salary_stats = salary_result.first()
    
    return {
        "total_employees": total_employees,
        "by_department": [
            {"department": dept.department, "count": dept.count}
            for dept in dept_stats
        ],
        "by_status": [
            {"status": status.employment_status, "count": status.count}
            for status in status_stats
        ],
        "salary_statistics": {
            "total_monthly_salary": float(salary_stats.total_salary or 0),
            "average_salary": float(salary_stats.avg_salary or 0),
            "min_salary": float(salary_stats.min_salary or 0),
            "max_salary": float(salary_stats.max_salary or 0)
        }
    }
