import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.customer import Customer, Contract, db
from datetime import datetime, date, timedelta
import random

def create_sample_data():
    with app.app_context():
        # Xóa dữ liệu cũ
        Contract.query.delete()
        Customer.query.delete()
        db.session.commit()
        
        print("Creating sample customers...")
        
        # Tạo khách hàng mẫu
        customers_data = [
            {
                "customer_name": "Nguyễn Văn A",
                "email": "nguyenvana@email.com",
                "mobile": "0901234567",
                "company_name": "Công ty TNHH ABC",
                "tax_id": "0123456789",
                "nationality": "Việt Nam",
                "business_type": "Công nghệ",
                "enterprise_type": "TNHH",
                "notes": "Khách hàng VIP"
            },
            {
                "customer_name": "Trần Thị B",
                "email": "tranthib@email.com",
                "mobile": "0912345678",
                "nationality": "Việt Nam",
                "notes": "Khách hàng cá nhân"
            },
            {
                "customer_name": "Lê Văn C",
                "email": "levanc@email.com",
                "mobile": "0923456789",
                "company_name": "Công ty Cổ phần XYZ",
                "tax_id": "0987654321",
                "nationality": "Việt Nam",
                "business_type": "Thương mại",
                "enterprise_type": "Cổ phần",
                "zalo": "levanc123",
                "whatsapp": "+84923456789"
            },
            {
                "customer_name": "Phạm Thị D",
                "email": "phamthid@email.com",
                "mobile": "0934567890",
                "nationality": "Việt Nam",
                "kakao": "phamthid_kr"
            },
            {
                "customer_name": "Hoàng Văn E",
                "email": "hoangvane@email.com",
                "mobile": "0945678901",
                "company_name": "Công ty TNHH DEF",
                "tax_id": "0111222333",
                "nationality": "Việt Nam",
                "business_type": "Dịch vụ",
                "enterprise_type": "TNHH",
                "notes": "Khách hàng mới"
            },
            {
                "customer_name": "Customer 1",
                "email": "customer1@test.com",
                "mobile": "0956789012",
                "nationality": "Việt Nam"
            },
            {
                "customer_name": "Customer 2",
                "email": "customer2@test.com",
                "mobile": "0967890123",
                "company_name": "Company 1 LLC",
                "tax_id": "0444555666",
                "nationality": "Việt Nam",
                "business_type": "Sản xuất",
                "enterprise_type": "TNHH"
            },
            {
                "customer_name": "Test Customer",
                "email": "test@customer.com",
                "mobile": "0978901234",
                "nationality": "Việt Nam",
                "notes": "Khách hàng test"
            },
            {
                "customer_name": "Customer 3",
                "email": "customer3@test.com",
                "mobile": "0989012345",
                "nationality": "Việt Nam"
            },
            {
                "customer_name": "Customer 4",
                "email": "customer4@test.com",
                "mobile": "0990123456",
                "company_name": "Company 2 LLC",
                "tax_id": "0777888999",
                "nationality": "Việt Nam",
                "business_type": "Thương mại điện tử",
                "enterprise_type": "TNHH"
            }
        ]
        
        customers = []
        for customer_data in customers_data:
            customer = Customer(**customer_data)
            db.session.add(customer)
            customers.append(customer)
        
        db.session.commit()
        print(f"Created {len(customers)} customers")
        
        # Tạo hợp đồng mẫu
        contract_types = ["VP ảo", "Phòng họp", "Chỗ ngồi cố định", "Chỗ ngồi không cố định", "Văn phòng riêng"]
        statuses = ["Khách hỏi", "Khách xem", "Khách book", "Khách đã thanh toán"]
        
        print("Creating sample contracts...")
        
        for i, customer in enumerate(customers):
            # Mỗi khách hàng có 1-3 hợp đồng
            num_contracts = random.randint(1, 3)
            
            for j in range(num_contracts):
                contract_type = random.choice(contract_types)
                contract_value = random.randint(5000000, 50000000)
                amount_paid = random.randint(0, contract_value)
                
                # Tạo ngày hợp đồng
                start_date = date.today() - timedelta(days=random.randint(30, 365))
                end_date = start_date + timedelta(days=random.randint(90, 730))
                
                # Chọn trạng thái dựa trên số tiền đã thanh toán
                if amount_paid == 0:
                    status = "Khách hỏi"
                elif amount_paid < contract_value * 0.3:
                    status = "Khách xem"
                elif amount_paid < contract_value:
                    status = "Khách book"
                else:
                    status = "Khách đã thanh toán"
                
                contract = Contract(
                    customer_id=customer.customer_id,
                    contract_type=contract_type,
                    contract_value=contract_value,
                    contract_start_date=start_date,
                    contract_end_date=end_date,
                    amount_paid=amount_paid,
                    last_payment_date=start_date + timedelta(days=random.randint(0, 30)) if amount_paid > 0 else None,
                    status=status,
                    additional_services="Dịch vụ internet, điện nước, bảo vệ"
                )
                
                db.session.add(contract)
        
        db.session.commit()
        print("Sample data creation completed!")
        
        # In thống kê
        total_customers = Customer.query.count()
        total_contracts = Contract.query.count()
        active_contracts = Contract.query.filter(Contract.status.in_(['Khách book', 'Khách đã thanh toán'])).count()
        
        print(f"\nStatistics:")
        print(f"Total customers: {total_customers}")
        print(f"Total contracts: {total_contracts}")
        print(f"Active contracts: {active_contracts}")

if __name__ == "__main__":
    create_sample_data() 