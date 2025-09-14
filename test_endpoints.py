#!/usr/bin/env python3
"""
Simple endpoint testing script for Garment Business Management System
Tests individual endpoints with sample data
"""

import asyncio
import httpx
import json
from datetime import datetime
from decimal import Decimal

BASE_URL = "http://localhost:8000"

async def test_endpoint(method: str, endpoint: str, data: dict = None, description: str = ""):
    """Test a single endpoint"""
    print(f"\n🧪 Testing: {description}")
    print(f"   {method} {endpoint}")
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                response = await client.post(f"{BASE_URL}{endpoint}", json=data)
            elif method == "PUT":
                response = await client.put(f"{BASE_URL}{endpoint}", json=data)
            elif method == "DELETE":
                response = await client.delete(f"{BASE_URL}{endpoint}")
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code < 400:
                print("   ✅ Success")
                if response.content:
                    result = response.json()
                    if isinstance(result, list):
                        print(f"   📊 Returned {len(result)} items")
                    elif isinstance(result, dict):
                        print(f"   📋 Response keys: {list(result.keys())}")
            else:
                print(f"   ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

async def login_and_get_token():
    """Login and get access token"""
    print("🔐 Logging in...")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/auth/login", data={
            "username": "admin@garment.com",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            print("✅ Login successful")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None

async def test_with_auth(token: str):
    """Test endpoints that require authentication"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient(headers=headers) as client:
        # Test get current user
        response = await client.get(f"{BASE_URL}/users/me")
        print(f"\n👤 Current User: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   Name: {user_data.get('full_name')}")
            print(f"   Role: {user_data.get('role')}")

async def main():
    """Main test function"""
    print("🚀 Garment Business Management System - Endpoint Tests")
    print("=" * 60)
    
    # Test public endpoints first
    await test_endpoint("GET", "/docs", description="API Documentation")
    await test_endpoint("GET", "/openapi.json", description="OpenAPI Specification")
    
    # Test authentication
    token = await login_and_get_token()
    if token:
        await test_with_auth(token)
    
    # Test basic endpoints
    await test_endpoint("GET", "/products/", description="Get all products")
    await test_endpoint("GET", "/raw-materials/", description="Get all raw materials")
    await test_endpoint("GET", "/shops/", description="Get all shops")
    await test_endpoint("GET", "/inventory/stocks", description="Get stock items")
    await test_endpoint("GET", "/inventory/stock-movements", description="Get stock movements")
    
    # Test analytics endpoints
    await test_endpoint("GET", "/analytics/dashboard", description="Dashboard analytics")
    await test_endpoint("GET", "/analytics/profit-loss?start_date=2024-01-01&end_date=2024-12-31", description="Profit/Loss analytics")
    
    # Test business intelligence
    await test_endpoint("GET", "/business-intelligence/kpis", description="Business KPIs")
    await test_endpoint("GET", "/business-intelligence/business-health", description="Business health")
    
    # Test finance endpoints
    await test_endpoint("GET", "/finance/profit-loss-statement?start_date=2024-01-01&end_date=2024-12-31", description="P&L Statement")
    
    print("\n" + "=" * 60)
    print("🎉 Endpoint testing completed!")
    print(f"\n🌐 Visit {BASE_URL}/docs for interactive API documentation")

if __name__ == "__main__":
    asyncio.run(main())
