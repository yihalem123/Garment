#!/usr/bin/env python3
"""
Simple test script to verify the setup
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from app.core.config import settings
from app.models import Base


async def test_database_connection():
    """Test database connection"""
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        print("✅ Database connection successful")
        await engine.dispose()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_imports():
    """Test that all modules can be imported"""
    try:
        from app.main import app
        from app.models import User, Shop, Product, RawMaterial
        from app.schemas import UserCreate, ProductCreate
        from app.core.security import get_password_hash
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("Testing Garment Business Management System setup...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Connection Test", test_database_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        result = await test_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("Test Results:")
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    if all(results):
        print("\n🎉 All tests passed! The system is ready to use.")
        print("\nTo start the application:")
        print("  python run.py")
        print("\nTo run with Docker:")
        print("  docker-compose up -d")
        return 0
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
