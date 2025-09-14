#!/usr/bin/env python3
"""
Create database tables
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db.session import async_session_maker
from app.models import *
from sqlmodel import SQLModel
from app.db.session import engine

async def create_tables():
    """Create all database tables"""
    print("🔧 Creating database tables...")
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    print("✅ Database tables created successfully!")

async def main():
    """Main function"""
    print("🚀 Creating Garment Business Management System Database Tables")
    print("=" * 70)
    
    try:
        await create_tables()
        print("\n🎉 Database setup completed successfully!")
        print("\n📋 You can now:")
        print("   - Run populate_sample_data.py to add sample data")
        print("   - Start the application with python run.py")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
