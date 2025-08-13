#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_tam_hoang_thien():
    """Test dữ liệu khách hàng Tâm Hoàng Thiện"""
    print("🚀 Test dữ liệu khách hàng Tâm Hoàng Thiện")
    print("=" * 50)
    
    try:
        from src.main import app
        from src.models.customer import Customer, Contract
        
        with app.app_context():
            # Tìm khách hàng Tâm Hoàng Thiện
            customer = Customer.query.filter_by(customer_name='Tâm Hoàng Thiện').first()
            
            if customer:
                print(f"✅ Tìm thấy khách hàng: {customer.customer_name}")
                print(f"   ID: {customer.customer_id}")
                print(f"   Company: {customer.company_name}")
                print(f"   Email: {customer.email}")
                print(f"   Mobile: {customer.mobile}")
                
                # Kiểm tra hợp đồng
                contracts = Contract.query.filter_by(customer_id=customer.customer_id).all()
                print(f"   Số hợp đồng: {len(contracts)}")
                
                if contracts:
                    latest_contract = contracts[0]
                    print(f"   Hợp đồng gần nhất:")
                    print(f"     ID: {latest_contract.contract_id}")
                    print(f"     Giá trị: {latest_contract.contract_value}")
                    print(f"     Ngày bắt đầu: {latest_contract.contract_start_date}")
                else:
                    print("   ❌ Không có hợp đồng nào")
                    
            else:
                print("❌ Không tìm thấy khách hàng Tâm Hoàng Thiện")
                # Liệt kê tất cả khách hàng
                all_customers = Customer.query.all()
                print(f"   Tổng số khách hàng: {len(all_customers)}")
                for c in all_customers[:5]:  # Chỉ hiển thị 5 đầu
                    print(f"     - {c.customer_name} (ID: {c.customer_id})")
                    
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tam_hoang_thien() 