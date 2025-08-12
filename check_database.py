import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.customer import Customer, Contract, WebBooking, Alert, db
from src.models.room import Branch, Room, RoomBooking, RoomAlert, WebRoomBooking
from sqlalchemy import inspect, text
from datetime import datetime

def check_database():
    with app.app_context():
        print("=" * 60)
        print("           DATABASE COMPREHENSIVE CHECK")
        print("=" * 60)
        
        # Kiểm tra database file
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path) / 1024  # KB
            print(f"Database file: {db_path}")
            print(f"Database size: {file_size:.2f} KB")
            print(f"Last modified: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
        else:
            print(f"Database file not found: {db_path}")
        
        print("\n" + "=" * 60)
        print("           TABLE STRUCTURE & DATA")
        print("=" * 60)
        
        # Lấy danh sách tất cả các bảng
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("❌ No tables found in database!")
            return
            
        print(f"📊 Found {len(tables)} tables: {', '.join(tables)}")
        print()
        
        # Kiểm tra từng bảng
        check_customer_data()
        check_contract_data()
        check_booking_data()
        check_alert_data()
        check_room_data()
        check_branch_data()
        check_room_booking_data()
        check_room_alert_data()
        check_web_room_booking_data()
        
        # Kiểm tra quan hệ giữa các bảng
        print("=" * 60)
        print("           RELATIONSHIP CHECK")
        print("=" * 60)
        check_relationships()
        
        # Kiểm tra API endpoints
        print("=" * 60)
        print("           API ENDPOINTS TEST")
        print("=" * 60)
        test_api_endpoints()
        
        # Thống kê tổng quan
        print("=" * 60)
        print("           SUMMARY STATISTICS")
        print("=" * 60)
        show_summary_stats()

def check_customer_data():
    print("👥 CUSTOMERS TABLE")
    print("-" * 40)
    
    try:
        customer_count = Customer.query.count()
        print(f"Total customers: {customer_count}")
        
        if customer_count > 0:
            customers = Customer.query.limit(5).all()
            print("\nSample customers:")
            for i, customer in enumerate(customers, 1):
                print(f"  {i}. {customer.customer_name} (ID: {customer.customer_id})")
                print(f"     📧 {customer.email or 'No email'}")
                print(f"     📱 {customer.mobile or 'No mobile'}")
                print(f"     🏢 {customer.company_name or 'No company'}")
                print(f"     🆔 {customer.tax_id or 'No tax ID'}")
                print(f"     🌍 {customer.nationality or 'No nationality'}")
                print(f"     💼 {customer.business_type or 'No business type'}")
            
            # Kiểm tra dữ liệu thiếu
            missing_email = Customer.query.filter(Customer.email.is_(None)).count()
            missing_mobile = Customer.query.filter(Customer.mobile.is_(None)).count()
            missing_company = Customer.query.filter(Customer.company_name.is_(None)).count()
            missing_tax_id = Customer.query.filter(Customer.tax_id.is_(None)).count()
            
            print(f"\nData quality:")
            print(f"  📧 Missing email: {missing_email}/{customer_count}")
            print(f"  📱 Missing mobile: {missing_mobile}/{customer_count}")
            print(f"  🏢 Missing company: {missing_company}/{customer_count}")
            print(f"  🆔 Missing tax ID: {missing_tax_id}/{customer_count}")
        else:
            print("⚠️  No customers found!")
    except Exception as e:
        print(f"❌ Error checking customers: {e}")
    print()

def check_contract_data():
    print("📋 CONTRACTS TABLE")
    print("-" * 40)
    
    try:
        contract_count = Contract.query.count()
        print(f"Total contracts: {contract_count}")
        
        if contract_count > 0:
            contracts = Contract.query.limit(5).all()
            print("\nSample contracts:")
            for i, contract in enumerate(contracts, 1):
                customer = Customer.query.get(contract.customer_id)
                customer_name = customer.customer_name if customer else "Unknown"
                
                print(f"  {i}. Contract #{contract.contract_id}")
                print(f"     👤 Customer: {customer_name} (ID: {contract.customer_id})")
                print(f"     📝 Type: {contract.contract_type}")
                print(f"     💰 Value: {contract.contract_value:,} VND")
                print(f"     📊 Status: {contract.status}")
                print(f"     📅 Start: {contract.contract_start_date}")
                print(f"     📅 End: {contract.contract_end_date}")
                
            # Thống kê theo status
            statuses = db.session.query(Contract.status, db.func.count(Contract.contract_id)).group_by(Contract.status).all()
            print(f"\nContract status breakdown:")
            for status, count in statuses:
                print(f"  📊 {status}: {count}")
                
            # Thống kê theo type
            types = db.session.query(Contract.contract_type, db.func.count(Contract.contract_id)).group_by(Contract.contract_type).all()
            print(f"\nContract type breakdown:")
            for contract_type, count in types:
                print(f"  📋 {contract_type}: {count}")
        else:
            print("⚠️  No contracts found!")
    except Exception as e:
        print(f"❌ Error checking contracts: {e}")
    print()

def check_booking_data():
    print("📝 WEB_BOOKINGS TABLE")
    print("-" * 40)
    
    try:
        booking_count = WebBooking.query.count()
        print(f"Total web bookings: {booking_count}")
        
        if booking_count > 0:
            bookings = WebBooking.query.limit(3).all()
            print("\nSample bookings:")
            for i, booking in enumerate(bookings, 1):
                print(f"  {i}. Booking #{booking.booking_id}")
                print(f"     👤 Customer: {booking.customer_name}")
                print(f"     📧 Email: {booking.email}")
                print(f"     📱 Phone: {booking.phone}")
                print(f"     🏢 Service: {booking.service_type}")
                print(f"     📅 Created: {booking.created_at}")
        else:
            print("⚠️  No web bookings found!")
    except Exception as e:
        print(f"❌ Error checking web bookings: {e}")
    print()

def check_alert_data():
    print("🚨 ALERTS TABLE")
    print("-" * 40)
    
    try:
        alert_count = Alert.query.count()
        print(f"Total alerts: {alert_count}")
        
        if alert_count > 0:
            alerts = Alert.query.limit(5).all()
            print("\nRecent alerts:")
            for i, alert in enumerate(alerts, 1):
                contract = Contract.query.get(alert.contract_id) if alert.contract_id else None
                customer_name = "Unknown"
                if contract:
                    customer = Customer.query.get(contract.customer_id)
                    customer_name = customer.customer_name if customer else "Unknown"
                
                print(f"  {i}. Alert #{alert.alert_id}")
                print(f"     📋 Contract ID: {alert.contract_id}")
                print(f"     👤 Customer: {customer_name}")
                print(f"     📅 Alert Date: {alert.alert_date}")
                print(f"     📝 Type: {alert.alert_type}")
                print(f"     📧 Is Sent: {'Yes' if alert.is_sent else 'No'}")
                print(f"     📅 Created: {alert.created_at}")
                
            # Thống kê theo type
            alert_types = db.session.query(Alert.alert_type, db.func.count(Alert.alert_id)).group_by(Alert.alert_type).all()
            print(f"\nAlert type breakdown:")
            for alert_type, count in alert_types:
                print(f"  📝 {alert_type}: {count}")
                
            # Thống kê gửi chưa gửi
            sent_count = Alert.query.filter(Alert.is_sent == True).count()
            unsent_count = alert_count - sent_count
            print(f"\nAlert status breakdown:")
            print(f"  ✅ Sent: {sent_count}")
            print(f"  ⏳ Pending: {unsent_count}")
        else:
            print("⚠️  No alerts found!")
    except Exception as e:
        print(f"❌ Error checking alerts: {e}")
    print()
        
def check_room_data():
    print("🏠 ROOMS TABLE")
    print("-" * 40)
    
    try:
        room_count = Room.query.count()
        print(f"Total rooms: {room_count}")
        
        if room_count > 0:
            rooms = Room.query.limit(5).all()
            print("\nSample rooms:")
            for i, room in enumerate(rooms, 1):
                branch = Branch.query.get(room.branch_id) if room.branch_id else None
                branch_name = branch.branch_name if branch else "No branch"
                
                print(f"  {i}. Room #{room.room_number}")
                print(f"     🏢 Branch: {branch_name}")
                print(f"     📝 Type: {getattr(room, 'room_type', 'No type')}")
                print(f"     📊 Available: {'Yes' if room.is_available else 'No'}")
                print(f"     💰 Rental Price: {room.rental_price:,} VND")
                print(f"     📏 Area: {room.area} m²")
                print(f"     👥 Capacity: {room.capacity}")
                print(f"     🧭 Orientation: {room.orientation or 'No orientation'}")
                
            # Thống kê theo availability
            available_count = Room.query.filter(Room.is_available == True).count()
            occupied_count = room_count - available_count
            
            print(f"\nRoom availability breakdown:")
            print(f"  ✅ Available: {available_count}")
            print(f"  🔒 Occupied: {occupied_count}")
        else:
            print("⚠️  No rooms found!")
    except Exception as e:
        print(f"❌ Error checking rooms: {e}")
    print()

def check_branch_data():
    print("🏢 BRANCHES TABLE")
    print("-" * 40)
    
    try:
        branch_count = Branch.query.count()
        print(f"Total branches: {branch_count}")
        
        if branch_count > 0:
            branches = Branch.query.all()
            print("\nAll branches:")
            for i, branch in enumerate(branches, 1):
                room_count = Room.query.filter_by(branch_id=branch.branch_id).count()
                print(f"  {i}. {branch.branch_name}")
                print(f"     📍 Address: {branch.address or 'No address'}")
                print(f"     📝 Description: {branch.description or 'No description'}")
                print(f"     🏠 Rooms: {room_count}")
                print(f"     📅 Created: {branch.created_at}")
        else:
            print("⚠️  No branches found!")
    except Exception as e:
        print(f"❌ Error checking branches: {e}")
    print()

def check_room_booking_data():
    print("📅 ROOM_BOOKINGS TABLE")
    print("-" * 40)
    
    try:
        booking_count = RoomBooking.query.count()
        print(f"Total room bookings: {booking_count}")
        
        if booking_count > 0:
            bookings = RoomBooking.query.limit(3).all()
            print("\nSample room bookings:")
            for i, booking in enumerate(bookings, 1):
                room = Room.query.get(booking.room_id) if booking.room_id else None
                room_number = room.room_number if room else "Unknown"
                
                print(f"  {i}. Booking #{booking.booking_id}")
                print(f"     🏠 Room: {room_number}")
                
                customer = Customer.query.get(booking.customer_id) if booking.customer_id else None
                customer_name = customer.customer_name if customer else "Unknown"
                print(f"     👤 Customer: {customer_name}")
                print(f"     📅 From: {booking.rental_start_date}")
                print(f"     📅 To: {booking.rental_end_date}")
                print(f"     📊 Status: {booking.status}")
                if booking.monthly_rent:
                    print(f"     💰 Monthly Rent: {booking.monthly_rent:,} VND")
                else:
                    print(f"     💰 Monthly Rent: Not set")
        else:
            print("⚠️  No room bookings found!")
    except Exception as e:
        print(f"❌ Error checking room bookings: {e}")
    print()

def check_room_alert_data():
    print("🚨 ROOM_ALERTS TABLE")
    print("-" * 40)
    
    try:
        alert_count = RoomAlert.query.count()
        print(f"Total room alerts: {alert_count}")
        
        if alert_count > 0:
            alerts = RoomAlert.query.limit(5).all()
            print("\nRecent room alerts:")
            for i, alert in enumerate(alerts, 1):
                booking = RoomBooking.query.get(alert.booking_id) if alert.booking_id else None
                room_info = "Unknown"
                customer_info = "Unknown"
                
                if booking:
                    room = Room.query.get(booking.room_id) if booking.room_id else None
                    room_info = f"Room {room.room_number}" if room else "Unknown Room"
                    
                    customer = Customer.query.get(booking.customer_id) if booking.customer_id else None
                    customer_info = customer.customer_name if customer else "Unknown Customer"
                
                print(f"  {i}. Alert #{alert.alert_id}")
                print(f"     📋 Booking ID: {alert.booking_id}")
                print(f"     🏠 Room: {room_info}")
                print(f"     👤 Customer: {customer_info}")
                print(f"     📅 Alert Date: {alert.alert_date}")
                print(f"     📝 Type: {alert.alert_type}")
                print(f"     📧 Is Sent: {'Yes' if alert.is_sent else 'No'}")
                print(f"     📅 Created: {alert.created_at}")
                
            # Thống kê theo type
            alert_types = db.session.query(RoomAlert.alert_type, db.func.count(RoomAlert.alert_id)).group_by(RoomAlert.alert_type).all()
            print(f"\nRoom alert type breakdown:")
            for alert_type, count in alert_types:
                print(f"  📝 {alert_type}: {count}")
                
            # Thống kê gửi chưa gửi
            sent_count = RoomAlert.query.filter(RoomAlert.is_sent == True).count()
            unsent_count = alert_count - sent_count
            print(f"\nRoom alert status breakdown:")
            print(f"  ✅ Sent: {sent_count}")
            print(f"  ⏳ Pending: {unsent_count}")
        else:
            print("⚠️  No room alerts found!")
    except Exception as e:
        print(f"❌ Error checking room alerts: {e}")
    print()

def check_web_room_booking_data():
    print("🌐 WEB_ROOM_BOOKINGS TABLE")
    print("-" * 40)
    
    try:
        booking_count = WebRoomBooking.query.count()
        print(f"Total web room bookings: {booking_count}")
        
        if booking_count > 0:
            bookings = WebRoomBooking.query.limit(5).all()
            print("\nSample web room bookings:")
            for i, booking in enumerate(bookings, 1):
                branch = Branch.query.get(booking.branch_id) if booking.branch_id else None
                branch_name = branch.branch_name if branch else "Unknown Branch"
                
                room = Room.query.get(booking.room_id) if booking.room_id else None
                room_info = f"Room {room.room_number}" if room else "No specific room"
                
                print(f"  {i}. Booking #{booking.web_booking_id}")
                print(f"     👤 Customer: {booking.customer_name}")
                print(f"     📧 Email: {booking.customer_email}")
                print(f"     📱 Phone: {booking.customer_phone or 'No phone'}")
                print(f"     🏢 Branch: {branch_name}")
                print(f"     🏠 Room: {room_info}")
                print(f"     📅 Preferred Start: {booking.preferred_start_date}")
                print(f"     📅 Preferred End: {booking.preferred_end_date or 'Not specified'}")
                print(f"     📊 Status: {booking.status}")
                print(f"     📅 Booking Date: {booking.booking_date}")
                print(f"     💬 Message: {booking.message or 'No message'}")
                
            # Thống kê theo status
            statuses = db.session.query(WebRoomBooking.status, db.func.count(WebRoomBooking.web_booking_id)).group_by(WebRoomBooking.status).all()
            print(f"\nWeb booking status breakdown:")
            for status, count in statuses:
                print(f"  📊 {status}: {count}")
        else:
            print("⚠️  No web room bookings found!")
    except Exception as e:
        print(f"❌ Error checking web room bookings: {e}")
    print()

def check_relationships():
    print("🔗 Checking data relationships...")
    
    try:
        # Customers without contracts
        customers_without_contracts = db.session.query(Customer).outerjoin(Contract).filter(Contract.customer_id.is_(None)).count()
        print(f"👤 Customers without contracts: {customers_without_contracts}")
        
        # Contracts without customers
        contracts_without_customers = db.session.query(Contract).outerjoin(Customer).filter(Customer.customer_id.is_(None)).count()
        print(f"📋 Orphaned contracts: {contracts_without_customers}")
        
        # Rooms without branches
        rooms_without_branches = db.session.query(Room).outerjoin(Branch).filter(Branch.branch_id.is_(None)).count()
        print(f"🏠 Rooms without branches: {rooms_without_branches}")
        
        # Room bookings without rooms
        bookings_without_rooms = db.session.query(RoomBooking).outerjoin(Room).filter(Room.room_id.is_(None)).count()
        print(f"📅 Bookings without rooms: {bookings_without_rooms}")
    except Exception as e:
        print(f"❌ Error checking relationships: {e}")
    
    print()

def test_api_endpoints():
    print("🔌 Testing API endpoints...")
    
    try:
        # Test customer endpoint
        from src.routes.customer import get_customers
        with app.test_request_context('/api/customers'):
            response = get_customers()
            print(f"✅ GET /api/customers: {response[1]} status")
            
        # Test contract templates endpoint
        from src.routes.contracts import get_available_templates
        with app.test_request_context('/api/contracts/templates'):
            response = get_available_templates()
            print(f"✅ GET /api/contracts/templates: {response[1]} status")
            
        # Test room endpoint  
        from src.routes.room import get_rooms
        with app.test_request_context('/api/rooms'):
            response = get_rooms()
            print(f"✅ GET /api/rooms: {response[1]} status")
            
    except Exception as e:
        print(f"❌ API test error: {e}")
    
    print()

def show_summary_stats():
    print("📊 Database Summary:")
    try:
        print(f"👥 Total Customers: {Customer.query.count()}")
        print(f"📋 Total Contracts: {Contract.query.count()}")
        print(f"📝 Total Web Bookings: {WebBooking.query.count()}")
        print(f"🚨 Total Alerts: {Alert.query.count()}")
        print(f"🏢 Total Branches: {Branch.query.count()}")
        print(f"🏠 Total Rooms: {Room.query.count()}")
        print(f"📅 Total Room Bookings: {RoomBooking.query.count()}")
        print(f"🚨 Total Room Alerts: {RoomAlert.query.count()}")
        print(f"🌐 Total Web Room Bookings: {WebRoomBooking.query.count()}")
        
        # Tính tổng doanh thu từ contracts
        total_revenue = db.session.query(db.func.sum(Contract.contract_value)).scalar() or 0
        print(f"💰 Total Contract Value: {total_revenue:,} VND")
        
        # Tính tổng doanh thu từ room bookings
        total_room_revenue = db.session.query(db.func.sum(RoomBooking.monthly_rent)).scalar() or 0
        print(f"🏠 Total Room Revenue: {total_room_revenue:,} VND")
    except Exception as e:
        print(f"❌ Error getting summary stats: {e}")
    
    print("\n" + "=" * 60)
    print("           DATABASE CHECK COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    check_database() 