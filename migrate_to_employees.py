#!/usr/bin/env python3
"""
Migration script to create Employee records from existing User salary data
"""
import asyncio
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_maker
from app.models import User, Employee, Shop, EmploymentStatus

async def migrate_to_employees():
    """Migrate existing user salary data to Employee model"""
    async with async_session_maker() as db:
        from sqlalchemy import select
        
        # Get all users with salary information
        users_query = select(User).where(User.salary.isnot(None))
        users_result = await db.execute(users_query)
        users = users_result.scalars().all()
        
        if not users:
            print("No users with salary information found.")
            return
        
        print(f"Found {len(users)} users with salary information. Migrating to Employee model...")
        
        migrated_count = 0
        for user in users:
            # Check if employee already exists
            existing_employee = await db.execute(
                select(Employee).where(Employee.email == user.email)
            )
            if existing_employee.scalar_one_or_none():
                print(f"Employee with email {user.email} already exists, skipping...")
                continue
            
            # Generate employee ID
            employee_id = f"EMP{user.id:03d}"
            
            # Create employee record
            employee = Employee(
                employee_id=employee_id,
                first_name=user.full_name.split()[0] if user.full_name else "Unknown",
                last_name=" ".join(user.full_name.split()[1:]) if user.full_name and len(user.full_name.split()) > 1 else "Employee",
                email=user.email,
                phone=getattr(user, 'phone', None),
                address=getattr(user, 'address', None),
                position=getattr(user, 'position', 'Staff'),
                department=getattr(user, 'department', 'General'),
                base_salary=user.salary,
                hourly_rate=None,
                overtime_rate=Decimal('1.5'),
                commission_rate=None,
                work_hours_per_week=40,
                shop_id=user.shop_id,
                manager_id=None,
                hire_date=getattr(user, 'hire_date', user.created_at),
                employment_status=EmploymentStatus.ACTIVE,
                is_active=user.is_active
            )
            
            db.add(employee)
            migrated_count += 1
            
            print(f"✅ Migrated: {user.full_name} -> {employee_id}")
        
        await db.commit()
        print(f"\n🎉 Successfully migrated {migrated_count} employees!")
        print(f"📊 Total employees in system: {migrated_count}")

if __name__ == "__main__":
    asyncio.run(migrate_to_employees())
