#!/usr/bin/env python3
"""
Script to create an admin user if it doesn't exist
"""
import asyncio
from sqlalchemy import select

from app.db.session import async_session_maker
from app.core.security import get_password_hash, get_user_by_email_async
from app.models import User, UserRole


async def create_admin_user():
    """Create admin user if it doesn't exist"""
    async with async_session_maker() as db:
        # Check if admin user exists
        admin_email = "admin@garment.com"
        existing_user = await get_user_by_email_async(db, admin_email)
        
        if existing_user:
            print(f"✅ Admin user already exists: {admin_email}")
            print(f"   Full Name: {existing_user.full_name}")
            print(f"   Role: {existing_user.role}")
            return existing_user
        
        # Create admin user
        print(f"🔧 Creating admin user: {admin_email}")
        admin_user = User(
            email=admin_email,
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            shop_id=None
        )
        
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {admin_email}")
        print(f"   Password: admin123")
        print(f"   Full Name: {admin_user.full_name}")
        print(f"   Role: {admin_user.role}")
        
        return admin_user


if __name__ == "__main__":
    asyncio.run(create_admin_user())

