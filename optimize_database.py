import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.customer import db

def optimize_database():
    """Add indexes to improve database performance"""
    print("🔧 OPTIMIZING DATABASE PERFORMANCE")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Add indexes for frequently queried columns
            indexes_to_create = [
                # Customer table indexes
                "CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(customer_name)",
                "CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)",
                "CREATE INDEX IF NOT EXISTS idx_customers_mobile ON customers(mobile)",
                "CREATE INDEX IF NOT EXISTS idx_customers_company ON customers(company_name)",
                
                # Contract table indexes
                "CREATE INDEX IF NOT EXISTS idx_contracts_customer_id ON contracts(customer_id)",
                "CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status)",
                "CREATE INDEX IF NOT EXISTS idx_contracts_type ON contracts(contract_type)",
                "CREATE INDEX IF NOT EXISTS idx_contracts_dates ON contracts(contract_start_date, contract_end_date)",
                
                # Room table indexes
                "CREATE INDEX IF NOT EXISTS idx_rooms_branch_id ON rooms(branch_id)",
                "CREATE INDEX IF NOT EXISTS idx_rooms_available ON rooms(is_available)",
                "CREATE INDEX IF NOT EXISTS idx_rooms_number ON rooms(room_number)",
                
                # Room booking indexes
                "CREATE INDEX IF NOT EXISTS idx_room_bookings_room_id ON room_bookings(room_id)",
                "CREATE INDEX IF NOT EXISTS idx_room_bookings_customer_id ON room_bookings(customer_id)",
                "CREATE INDEX IF NOT EXISTS idx_room_bookings_dates ON room_bookings(rental_start_date, rental_end_date)",
                "CREATE INDEX IF NOT EXISTS idx_room_bookings_status ON room_bookings(status)",
                
                # Alert indexes
                "CREATE INDEX IF NOT EXISTS idx_alerts_contract_id ON alerts(contract_id)",
                "CREATE INDEX IF NOT EXISTS idx_alerts_date ON alerts(alert_date)",
                "CREATE INDEX IF NOT EXISTS idx_alerts_sent ON alerts(is_sent)",
                
                # Room alert indexes
                "CREATE INDEX IF NOT EXISTS idx_room_alerts_booking_id ON room_alerts(booking_id)",
                "CREATE INDEX IF NOT EXISTS idx_room_alerts_date ON room_alerts(alert_date)",
                "CREATE INDEX IF NOT EXISTS idx_room_alerts_sent ON room_alerts(is_sent)",
            ]
            
            created_count = 0
            for index_sql in indexes_to_create:
                try:
                    db.session.execute(db.text(index_sql))
                    created_count += 1
                    index_name = index_sql.split('idx_')[1].split(' ')[0]
                    print(f"✅ Created index: idx_{index_name}")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"❌ Failed to create index: {str(e)[:50]}")
            
            db.session.commit()
            print(f"\n📊 Database optimization completed!")
            print(f"   ✅ {created_count}/{len(indexes_to_create)} indexes processed")
            
            # Analyze tables for query planner
            analyze_queries = [
                "ANALYZE customers",
                "ANALYZE contracts", 
                "ANALYZE rooms",
                "ANALYZE room_bookings",
                "ANALYZE alerts",
                "ANALYZE room_alerts"
            ]
            
            for query in analyze_queries:
                try:
                    db.session.execute(db.text(query))
                    table_name = query.split()[1]
                    print(f"📈 Analyzed table: {table_name}")
                except Exception as e:
                    print(f"⚠️ Failed to analyze: {str(e)[:30]}")
            
            db.session.commit()
            print("\n🎯 Database is now optimized for better performance!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Database optimization failed: {e}")

def check_database_size():
    """Check database size and table statistics"""
    print("\n📊 DATABASE STATISTICS")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Get table sizes
            tables = ['customers', 'contracts', 'rooms', 'room_bookings', 'branches', 'alerts', 'room_alerts']
            
            for table in tables:
                try:
                    count_result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                    count = count_result[0] if count_result else 0
                    print(f"📋 {table:15}: {count:6} records")
                except Exception as e:
                    print(f"❌ {table:15}: Error getting count")
            
            # Check database file size
            db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
            if os.path.exists(db_path):
                file_size = os.path.getsize(db_path) / 1024  # KB
                print(f"\n💾 Database file size: {file_size:.2f} KB")
            
        except Exception as e:
            print(f"❌ Error checking database stats: {e}")

if __name__ == "__main__":
    check_database_size()
    optimize_database() 