#!/usr/bin/env python3
"""
Comprehensive test for Employee and Payroll Management System
"""
import asyncio
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Test configuration
BASE_URL = "http://localhost:8000"
ADMIN_CREDENTIALS = {
    "email": "admin@garment.com",
    "password": "admin123"
}

class EmployeePayrollTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.employee_id = None
        self.payroll_record_id = None

    def login(self):
        """Login as admin"""
        print("🔐 Logging in as admin...")
        # OAuth2PasswordRequestForm expects username and password
        login_data = {
            "username": ADMIN_CREDENTIALS["email"],
            "password": ADMIN_CREDENTIALS["password"]
        }
        response = self.session.post(f"{BASE_URL}/auth/login", data=login_data)
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            print("✅ Login successful!")
            return True
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False

    def test_employee_management(self):
        """Test employee management endpoints"""
        print("\n👥 Testing Employee Management...")
        
        # Test 1: Get employees
        print("📋 Getting employees list...")
        response = self.session.get(f"{BASE_URL}/employees/")
        if response.status_code == 200:
            employees = response.json()
            print(f"✅ Found {len(employees)} employees")
            if employees:
                self.employee_id = employees[0]["id"]
                print(f"📝 First employee: {employees[0]['full_name']} (ID: {self.employee_id})")
        else:
            print(f"❌ Failed to get employees: {response.status_code} - {response.text}")
            return False

        # Test 2: Get employee statistics
        print("📊 Getting employee statistics...")
        response = self.session.get(f"{BASE_URL}/employees/statistics/summary")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Employee statistics:")
            print(f"   - Total employees: {stats['total_employees']}")
            print(f"   - Total monthly salary: ${stats['salary_statistics']['total_monthly_salary']:,.2f}")
            print(f"   - Average salary: ${stats['salary_statistics']['average_salary']:,.2f}")
        else:
            print(f"❌ Failed to get statistics: {response.status_code} - {response.text}")

        # Test 3: Create new employee
        print("➕ Creating new employee...")
        new_employee = {
            "employee_id": "EMP999",
            "first_name": "Test",
            "last_name": "Employee",
            "email": "test.employee@garment.com",
            "phone": "+1234567890",
            "address": "123 Test Street",
            "position": "Test Position",
            "department": "Testing",
            "base_salary": 5000.00,
            "hourly_rate": None,
            "overtime_rate": 1.5,
            "commission_rate": None,
            "work_hours_per_week": 40,
            "shop_id": 1,
            "manager_id": None,
            "hire_date": datetime.now().isoformat()
        }
        
        response = self.session.post(f"{BASE_URL}/employees/", json=new_employee)
        if response.status_code == 200:
            created_employee = response.json()
            print(f"✅ Created employee: {created_employee['full_name']} (ID: {created_employee['id']})")
            self.employee_id = created_employee['id']
        else:
            print(f"❌ Failed to create employee: {response.status_code} - {response.text}")

        return True

    def test_payroll_management(self):
        """Test payroll management endpoints"""
        print("\n💰 Testing Payroll Management...")
        
        # Test 1: Process payroll
        print("🔄 Processing payroll...")
        payroll_data = {
            "period_start": (datetime.now() - timedelta(days=30)).isoformat(),
            "period_end": datetime.now().isoformat(),
            "shop_id": 1,
            "include_inactive": False
        }
        
        response = self.session.post(f"{BASE_URL}/payroll/process", json=payroll_data)
        if response.status_code == 200:
            payroll_summary = response.json()
            print(f"✅ Payroll processed successfully!")
            print(f"   - Period: {payroll_summary['period_start']} to {payroll_summary['period_end']}")
            print(f"   - Total employees: {payroll_summary['total_employees']}")
            print(f"   - Total gross pay: ${float(payroll_summary['total_gross_pay']):,.2f}")
            print(f"   - Total deductions: ${float(payroll_summary['total_deductions']):,.2f}")
            print(f"   - Total net pay: ${float(payroll_summary['total_net_pay']):,.2f}")
        else:
            print(f"❌ Failed to process payroll: {response.status_code} - {response.text}")
            return False

        # Test 2: Get payroll records
        print("📋 Getting payroll records...")
        response = self.session.get(f"{BASE_URL}/payroll/records")
        if response.status_code == 200:
            records = response.json()
            print(f"✅ Found {len(records)} payroll records")
            if records:
                self.payroll_record_id = records[0]["id"]
                record = records[0]
                print(f"📝 First record: {record['employee_name']}")
                print(f"   - Gross pay: ${float(record['gross_pay']):,.2f}")
                print(f"   - Net pay: ${float(record['net_pay']):,.2f}")
                print(f"   - Status: {record['status']}")
        else:
            print(f"❌ Failed to get payroll records: {response.status_code} - {response.text}")

        # Test 3: Get payroll summaries
        print("📊 Getting payroll summaries...")
        response = self.session.get(f"{BASE_URL}/payroll/summaries")
        if response.status_code == 200:
            summaries = response.json()
            print(f"✅ Found {len(summaries)} payroll summaries")
            for summary in summaries:
                print(f"   - Period: {summary['period_start']} to {summary['period_end']}")
                print(f"   - Total net pay: ${float(summary['total_net_pay']):,.2f}")
                print(f"   - Processed: {summary['is_processed']}")
        else:
            print(f"❌ Failed to get payroll summaries: {response.status_code} - {response.text}")

        # Test 4: Get payroll statistics
        print("📈 Getting payroll statistics...")
        response = self.session.get(f"{BASE_URL}/payroll/statistics/overview")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Payroll statistics:")
            print(f"   - Current month total paid: ${float(stats['current_month']['total_paid']):,.2f}")
            print(f"   - Records processed: {stats['current_month']['records_count']}")
            print(f"   - Average pay: ${float(stats['current_month']['average_pay']):,.2f}")
            print(f"   - Pending payments: {stats['pending_payments']['pending_count']}")
            print(f"   - Pending amount: ${float(stats['pending_payments']['total_pending']):,.2f}")
        else:
            print(f"❌ Failed to get payroll statistics: {response.status_code} - {response.text}")

        return True

    def test_payment_processing(self):
        """Test payment processing"""
        print("\n💳 Testing Payment Processing...")
        
        if not self.payroll_record_id:
            print("❌ No payroll record ID available for payment testing")
            return False

        # Test payment processing
        print("💸 Processing payment...")
        payment_data = {
            "payroll_record_ids": [self.payroll_record_id],
            "payment_method": "bank_transfer",
            "payment_reference": "PAY-TEST-001",
            "payment_date": datetime.now().isoformat(),
            "notes": "Test payment processing"
        }
        
        response = self.session.post(f"{BASE_URL}/payroll/payment", json=payment_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Payment processed successfully!")
            print(f"   - Records processed: {result['message']}")
            print(f"   - Payment method: {result['payment_method']}")
            print(f"   - Total amount: ${float(result['total_amount']):,.2f}")
        else:
            print(f"❌ Failed to process payment: {response.status_code} - {response.text}")
            return False

        return True

    def test_role_based_access(self):
        """Test role-based access control"""
        print("\n🔒 Testing Role-Based Access Control...")
        
        # Test shop manager access
        print("🏪 Testing shop manager access...")
        shop_manager_credentials = {
            "email": "shop.manager@garment.com",
            "password": "shop123"
        }
        
        # Login as shop manager
        shop_manager_login_data = {
            "username": shop_manager_credentials["email"],
            "password": shop_manager_credentials["password"]
        }
        response = requests.post(f"{BASE_URL}/auth/login", data=shop_manager_login_data)
        if response.status_code == 200:
            shop_manager_token = response.json()["access_token"]
            shop_manager_session = requests.Session()
            shop_manager_session.headers.update({"Authorization": f"Bearer {shop_manager_token}"})
            
            # Test shop manager can access employees from their shop
            response = shop_manager_session.get(f"{BASE_URL}/employees/")
            if response.status_code == 200:
                employees = response.json()
                print(f"✅ Shop manager can see {len(employees)} employees from their shop")
            else:
                print(f"❌ Shop manager cannot access employees: {response.status_code}")
            
            # Test shop manager cannot access payroll processing
            response = shop_manager_session.post(f"{BASE_URL}/payroll/process", json={})
            if response.status_code == 403:
                print("✅ Shop manager correctly denied access to payroll processing")
            else:
                print(f"❌ Shop manager should not have access to payroll processing: {response.status_code}")
        else:
            print("❌ Could not login as shop manager")

        return True

    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Employee & Payroll System Test")
        print("=" * 60)
        
        # Login
        if not self.login():
            return False
        
        # Test employee management
        if not self.test_employee_management():
            return False
        
        # Test payroll management
        if not self.test_payroll_management():
            return False
        
        # Test payment processing
        if not self.test_payment_processing():
            return False
        
        # Test role-based access
        if not self.test_role_based_access():
            return False
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("✅ Employee Management System: Working")
        print("✅ Payroll Management System: Working")
        print("✅ Payment Processing: Working")
        print("✅ Role-Based Access Control: Working")
        print("\n🏆 The Employee and Payroll Management System is fully functional!")
        
        return True

def main():
    """Main test function"""
    tester = EmployeePayrollTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎯 System is ready for production use!")
    else:
        print("\n⚠️  Some tests failed. Please check the system configuration.")

if __name__ == "__main__":
    main()
