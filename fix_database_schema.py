import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.customer import db
from sqlalchemy import inspect, text

def fix_database_schema():
    """Fix database schema by adding missing fields"""
    print("🔧 FIXING DATABASE SCHEMA")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Kiểm tra cấu trúc bảng customers hiện tại
            inspector = inspect(db.engine)
            customer_columns = [col['name'] for col in inspector.get_columns('customers')]
            
            print(f"📋 Current customers table columns: {', '.join(customer_columns)}")
            
            # Danh sách các trường cần kiểm tra và thêm
            required_fields = {
                'company_name': 'VARCHAR(255)',
                'tax_id': 'VARCHAR(50)',
                'nationality': 'VARCHAR(100)',
                'business_type': 'VARCHAR(255)',
                'enterprise_type': 'VARCHAR(255)',
                'id_card': 'VARCHAR(50)',
                'zalo': 'VARCHAR(50)',
                'whatsapp': 'VARCHAR(50)',
                'kakao': 'VARCHAR(50)',
                'notes': 'TEXT'
            }
            
            missing_fields = []
            
            # Kiểm tra từng trường
            for field_name, field_type in required_fields.items():
                if field_name not in customer_columns:
                    missing_fields.append((field_name, field_type))
                    print(f"❌ Missing field: {field_name} ({field_type})")
                else:
                    print(f"✅ Field exists: {field_name}")
            
            if not missing_fields:
                print("\n🎉 All required fields are present in the customers table!")
                return
            
            print(f"\n🔧 Adding {len(missing_fields)} missing fields...")
            
            # Thêm các trường bị thiếu
            for field_name, field_type in missing_fields:
                try:
                    sql = f"ALTER TABLE customers ADD COLUMN {field_name} {field_type}"
                    print(f"Executing: {sql}")
                    
                    with db.engine.connect() as conn:
                        conn.execute(text(sql))
                        conn.commit()
                    
                    print(f"✅ Successfully added field: {field_name}")
                    
                except Exception as e:
                    print(f"❌ Error adding field {field_name}: {e}")
            
            # Kiểm tra lại cấu trúc sau khi sửa
            print("\n📋 Updated customers table structure:")
            updated_columns = [col['name'] for col in inspector.get_columns('customers')]
            for col in updated_columns:
                print(f"  - {col}")
            
            print("\n🎉 Database schema fix completed!")
            
        except Exception as e:
            print(f"❌ Error fixing database schema: {e}")

def check_table_structure():
    """Check the current structure of all tables"""
    print("\n🔍 CHECKING ALL TABLE STRUCTURES")
    print("=" * 50)
    
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            for table_name in tables:
                print(f"\n📋 Table: {table_name}")
                print("-" * 30)
                
                columns = inspector.get_columns(table_name)
                for col in columns:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    default = f" DEFAULT {col['default']}" if col['default'] is not None else ""
                    print(f"  - {col['name']}: {col['type']} {nullable}{default}")
                
                # Kiểm tra indexes
                indexes = inspector.get_indexes(table_name)
                if indexes:
                    print("  Indexes:")
                    for idx in indexes:
                        print(f"    - {idx['name']}: {', '.join(idx['column_names'])}")
                
        except Exception as e:
            print(f"❌ Error checking table structure: {e}")

def create_missing_indexes():
    """Create missing indexes for better performance"""
    print("\n🚀 CREATING MISSING INDEXES")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Danh sách indexes cần tạo
            indexes_to_create = [
                "CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(customer_name)",
                "CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)",
                "CREATE INDEX IF NOT EXISTS idx_customers_mobile ON customers(mobile)",
                "CREATE INDEX IF NOT EXISTS idx_customers_company ON customers(company_name)",
                "CREATE INDEX IF NOT EXISTS idx_customers_tax_id ON customers(tax_id)"
            ]
            
            for sql in indexes_to_create:
                try:
                    print(f"Creating index: {sql}")
                    with db.engine.connect() as conn:
                        conn.execute(text(sql))
                        conn.commit()
                    print(f"✅ Index created successfully")
                except Exception as e:
                    print(f"❌ Error creating index: {e}")
                    
        except Exception as e:
            print(f"❌ Error creating indexes: {e}")

if __name__ == "__main__":
    print("Database Schema Fix Tool")
    print("=" * 50)
    
    # Sửa schema
    fix_database_schema()
    
    # Kiểm tra cấu trúc bảng
    check_table_structure()
    
    # Tạo indexes
    create_missing_indexes()
    
    print("\n" + "=" * 50)
    print("Database schema fix tool completed!")
    print("=" * 50) 