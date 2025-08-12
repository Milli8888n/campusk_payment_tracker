import sys
import os
import requests
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.customer import Customer, Contract, db
from src.models.room import Branch, Room, RoomBooking

def check_data_flow():
    print("=" * 80)
    print("         DATA FLOW CHECK: DATABASE → BACKEND → FRONTEND")
    print("=" * 80)
    
    # Check if backend server is running
    backend_url = "http://localhost:5000"
    frontend_url = "http://localhost:5173"  # Vite default port
    
    print("\n🔍 STEP 1: BACKEND SERVER STATUS")
    print("-" * 50)
    check_backend_server(backend_url)
    
    print("\n🔍 STEP 2: DATABASE → BACKEND API")
    print("-" * 50)
    check_database_to_api_flow(backend_url)
    
    print("\n🔍 STEP 3: API ENDPOINTS TESTING")
    print("-" * 50)
    test_all_api_endpoints(backend_url)
    
    print("\n🔍 STEP 4: CORS & FRONTEND CONNECTIVITY")
    print("-" * 50)
    check_cors_and_frontend(backend_url, frontend_url)
    
    print("\n🔍 STEP 5: DATA CONSISTENCY CHECK")
    print("-" * 50)
    check_data_consistency()
    
    print("\n🔍 STEP 6: PERFORMANCE & RESPONSE TIME")
    print("-" * 50)
    check_api_performance(backend_url)
    
    print("\n" + "=" * 80)
    print("                    FLOW CHECK COMPLETED")
    print("=" * 80)

def check_backend_server(backend_url):
    """Kiểm tra backend server có đang chạy không"""
    try:
        response = requests.get(f"{backend_url}/api/test", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend server is RUNNING")
            print(f"   📡 URL: {backend_url}")
            print(f"   📅 Server time: {data.get('timestamp', 'Unknown')}")
            print(f"   💬 Message: {data.get('message', 'No message')}")
            return True
        else:
            print(f"⚠️  Backend server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Backend server is NOT RUNNING at {backend_url}")
        print("   🚀 Start server with: python src/main.py")
        return False
    except Exception as e:
        print(f"❌ Backend server check failed: {e}")
        return False

def check_database_to_api_flow(backend_url):
    """Kiểm tra luồng dữ liệu từ Database → API"""
    print("🔄 Testing Database → API data flow...")
    
    with app.app_context():
        # Get data directly from database
        db_customer_count = Customer.query.count()
        db_contract_count = Contract.query.count()
        db_branch_count = Branch.query.count()
        db_room_count = Room.query.count()
        
        print(f"📊 Database counts:")
        print(f"   👥 Customers: {db_customer_count}")
        print(f"   📋 Contracts: {db_contract_count}")
        print(f"   🏢 Branches: {db_branch_count}")
        print(f"   🏠 Rooms: {db_room_count}")
    
    # Get data from API
    api_counts = {}
    
    try:
        # Test customers API
        response = requests.get(f"{backend_url}/api/customers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            api_counts['customers'] = len(data.get('customers', []))
            print(f"\n✅ /api/customers working")
        else:
            print(f"\n❌ /api/customers failed: {response.status_code}")
            
        # Test rooms API  
        response = requests.get(f"{backend_url}/api/rooms", timeout=10)
        if response.status_code == 200:
            data = response.json()
            api_counts['rooms'] = len(data.get('rooms', []))
            print(f"✅ /api/rooms working")
        else:
            print(f"❌ /api/rooms failed: {response.status_code}")
            
        # Test branches API
        response = requests.get(f"{backend_url}/api/branches", timeout=10)
        if response.status_code == 200:
            data = response.json()
            api_counts['branches'] = len(data.get('branches', []))
            print(f"✅ /api/branches working")
        else:
            print(f"❌ /api/branches failed: {response.status_code}")
            
        # Test templates API
        response = requests.get(f"{backend_url}/api/contracts/templates", timeout=10)
        if response.status_code == 200:
            data = response.json()
            api_counts['templates'] = data.get('total', 0)
            print(f"✅ /api/contracts/templates working")
        else:
            print(f"❌ /api/contracts/templates failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ API testing failed: {e}")
        return
    
    # Compare database vs API counts
    print(f"\n📊 Database vs API comparison:")
    if 'customers' in api_counts:
        match = "✅" if db_customer_count == api_counts['customers'] else "❌"
        print(f"   👥 Customers: DB={db_customer_count}, API={api_counts['customers']} {match}")
    
    if 'rooms' in api_counts:
        match = "✅" if db_room_count == api_counts['rooms'] else "❌"
        print(f"   🏠 Rooms: DB={db_room_count}, API={api_counts['rooms']} {match}")
        
    if 'branches' in api_counts:
        match = "✅" if db_branch_count == api_counts['branches'] else "❌"
        print(f"   🏢 Branches: DB={db_branch_count}, API={api_counts['branches']} {match}")

def test_all_api_endpoints(backend_url):
    """Test tất cả API endpoints"""
    endpoints = [
        ("GET", "/api/test", "Test endpoint"),
        ("GET", "/api/customers", "Customer list"),
        ("GET", "/api/rooms", "Room list"), 
        ("GET", "/api/branches", "Branch list"),
        ("GET", "/api/room-bookings", "Room bookings"),
        ("GET", "/api/contracts/templates", "Contract templates"),
        ("GET", "/api/contracts/list", "Generated contracts"),
        ("GET", "/api/dashboard/stats", "Dashboard stats"),
        ("GET", "/api/alerts/upcoming", "Upcoming alerts"),
        ("GET", "/api/room-dashboard/stats", "Room dashboard stats"),
        ("GET", "/api/room-alerts/upcoming", "Room alerts"),
    ]
    
    working_endpoints = 0
    total_endpoints = len(endpoints)
    
    for method, endpoint, description in endpoints:
        try:
            response = requests.get(f"{backend_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - {description}")
                working_endpoints += 1
            elif response.status_code == 404:
                print(f"⚠️  {endpoint} - {description} (Not Found)")
            else:
                print(f"❌ {endpoint} - {description} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {endpoint} - {description} (Error: {str(e)[:50]})")
    
    print(f"\n📊 API Endpoints Summary: {working_endpoints}/{total_endpoints} working")
    success_rate = (working_endpoints / total_endpoints) * 100
    print(f"   📈 Success Rate: {success_rate:.1f}%")

def check_cors_and_frontend(backend_url, frontend_url):
    """Kiểm tra CORS và kết nối frontend"""
    print("🌐 Checking CORS configuration...")
    
    # Test CORS headers
    try:
        response = requests.options(f"{backend_url}/api/customers", timeout=5)
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        if cors_headers['Access-Control-Allow-Origin']:
            print(f"✅ CORS is configured")
            for header, value in cors_headers.items():
                if value:
                    print(f"   {header}: {value}")
        else:
            print(f"⚠️  CORS headers not found in OPTIONS response")
            
    except Exception as e:
        print(f"❌ CORS check failed: {e}")
    
    # Test if frontend is running
    print(f"\n🖥️  Checking frontend server at {frontend_url}...")
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Frontend server is RUNNING")
            print(f"   📡 URL: {frontend_url}")
        else:
            print(f"⚠️  Frontend responded with status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Frontend server is NOT RUNNING at {frontend_url}")
        print("   🚀 Start frontend with: npm run dev")
    except Exception as e:
        print(f"❌ Frontend check failed: {e}")

def check_data_consistency():
    """Kiểm tra tính nhất quán của dữ liệu"""
    print("🔍 Checking data consistency...")
    
    with app.app_context():
        issues = []
        
        # Check for orphaned contracts
        orphaned_contracts = db.session.query(Contract).outerjoin(Customer).filter(Customer.customer_id.is_(None)).count()
        if orphaned_contracts > 0:
            issues.append(f"❌ {orphaned_contracts} contracts without customers")
        else:
            print("✅ All contracts have valid customers")
        
        # Check for customers without contracts
        customers_no_contracts = db.session.query(Customer).outerjoin(Contract).filter(Contract.customer_id.is_(None)).count()
        if customers_no_contracts > 0:
            print(f"⚠️  {customers_no_contracts} customers without contracts")
        else:
            print("✅ All customers have contracts")
            
        # Check for rooms without branches
        rooms_no_branches = db.session.query(Room).outerjoin(Branch).filter(Branch.branch_id.is_(None)).count()
        if rooms_no_branches > 0:
            issues.append(f"❌ {rooms_no_branches} rooms without branches")
        else:
            print("✅ All rooms have valid branches")
            
        # Check for bookings without rooms
        bookings_no_rooms = db.session.query(RoomBooking).outerjoin(Room).filter(Room.room_id.is_(None)).count()
        if bookings_no_rooms > 0:
            issues.append(f"❌ {bookings_no_rooms} bookings without rooms")
        else:
            print("✅ All bookings have valid rooms")
        
        if issues:
            print(f"\n⚠️  Data consistency issues found:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n✅ Data consistency check passed!")

def check_api_performance(backend_url):
    """Kiểm tra hiệu suất API"""
    print("⏱️  Testing API performance...")
    
    endpoints_to_test = [
        "/api/customers",
        "/api/rooms", 
        "/api/contracts/templates"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            start_time = time.time()
            response = requests.get(f"{backend_url}{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                data_size = len(response.content)
                if response_time < 100:
                    status = "🚀 Fast"
                elif response_time < 500:
                    status = "✅ Good"
                elif response_time < 1000:
                    status = "⚠️  Slow"
                else:
                    status = "❌ Very Slow"
                    
                print(f"{status} {endpoint}: {response_time:.0f}ms ({data_size} bytes)")
            else:
                print(f"❌ {endpoint}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"❌ {endpoint}: Error ({str(e)[:30]})")

def test_crud_operations(backend_url):
    """Test CRUD operations"""
    print("\n🔄 Testing CRUD operations...")
    
    # This would test CREATE, READ, UPDATE, DELETE operations
    # For safety, we'll only test READ operations
    
    try:
        # Test pagination
        response = requests.get(f"{backend_url}/api/customers?page=1&per_page=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            customers = data.get('customers', [])
            if customers:
                print(f"✅ Pagination working: Got {len(customers)} customers")
                
                # Test individual customer fetch
                if customers:
                    customer_id = customers[0]['customer_id']
                    response = requests.get(f"{backend_url}/api/customers/{customer_id}", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ Individual customer fetch working (ID: {customer_id})")
                    else:
                        print(f"❌ Individual customer fetch failed")
            else:
                print(f"⚠️  No customers returned from API")
        else:
            print(f"❌ Customer pagination failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ CRUD testing failed: {e}")

def test_contract_generation_flow(backend_url):
    """Test contract generation flow"""
    print("\n📄 Testing contract generation flow...")
    
    try:
        # Get available templates
        response = requests.get(f"{backend_url}/api/contracts/templates", timeout=5)
        if response.status_code == 200:
            templates_data = response.json()
            templates = templates_data.get('templates', [])
            available_templates = [t for t in templates if t.get('available', False)]
            
            print(f"✅ Templates API working: {len(available_templates)}/{len(templates)} available")
            
            if available_templates:
                # Get customers for testing
                response = requests.get(f"{backend_url}/api/customers?per_page=1", timeout=5)
                if response.status_code == 200:
                    customers_data = response.json()
                    customers = customers_data.get('customers', [])
                    
                    if customers:
                        print(f"✅ Ready for contract generation:")
                        print(f"   📄 Available templates: {len(available_templates)}")
                        print(f"   👥 Available customers: {len(customers)}")
                        print(f"   🎯 Can generate contracts: YES")
                    else:
                        print(f"⚠️  No customers available for contract generation")
                else:
                    print(f"❌ Cannot fetch customers for contract generation")
            else:
                print(f"⚠️  No available templates for contract generation")
        else:
            print(f"❌ Templates API failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Contract generation flow test failed: {e}")

if __name__ == "__main__":
    check_data_flow()
    
    # Additional tests
    backend_url = "http://localhost:5000"
    test_crud_operations(backend_url)
    test_contract_generation_flow(backend_url) 