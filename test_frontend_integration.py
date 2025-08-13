#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime, timedelta

# Thêm đường dẫn để import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_frontend_integration():
    """Test tích hợp frontend-backend cho payment request"""
    
    print("🚀 Test tích hợp Frontend-Backend cho Payment Request")
    print("=" * 60)
    
    try:
        from src.main import app
        from src.models.user import db
        from src.models.customer import Customer, Contract
        from src.contract_generator import ContractGenerator
        
        print("✅ Đã import thành công các models và ContractGenerator")
        
        # Sử dụng application context
        with app.app_context():
            # Khởi tạo contract generator
            contract_generator = ContractGenerator()
            
            # Lấy customer có contract
            customers_with_contracts = db.session.query(Customer).join(Contract).all()
            
            if not customers_with_contracts:
                print("❌ Không tìm thấy customer nào có contract")
                return
            
            # Lấy customer đầu tiên có contract
            customer = customers_with_contracts[0]
            contract = customer.contracts[0]
            
            print(f"✅ Sử dụng customer: {customer.customer_name}")
            print(f"✅ Contract value: {contract.contract_value:,} VND")
            
            # Lấy dữ liệu customer và contract như frontend sẽ làm
            customer_data = contract_generator.get_customer_data(customer.customer_id)
            contract_data = contract_generator.get_contract_data(contract.contract_id)
            
            print(f"\n📊 Customer data từ database:")
            print(f"   customer_name: {customer_data.get('customer_name')}")
            print(f"   company_name: {customer_data.get('company_name')}")
            print(f"   tax_id: {customer_data.get('tax_id')}")
            print(f"   mobile: {customer_data.get('mobile')}")
            
            print(f"\n📊 Contract data từ database:")
            print(f"   contract_value: {contract_data.get('contract_value')}")
            print(f"   contract_start_date: {contract_data.get('contract_start_date')}")
            print(f"   contract_end_date: {contract_data.get('contract_end_date')}")
            
            # Chuẩn bị dữ liệu cho template như frontend sẽ làm
            template_data = contract_generator.prepare_payment_request_data(customer_data, contract_data)
            
            print(f"\n📊 Template data được chuẩn bị:")
            print("=" * 50)
            for key, value in template_data.items():
                print(f"   {key}: {value}")
            
            # Kiểm tra xem có đủ 11 trường không
            expected_fields = {
                'customer_name', 'address', 'service_name', 'service_unit',
                'service_quantity', 'service_unit_price', 'service_amount',
                'vat_amount', 'deposit_amount', 'total_rental_amount', 'amount_in_words'
            }
            
            actual_fields = set(template_data.keys())
            
            print(f"\n🔍 Kiểm tra các trường:")
            print(f"   - Expected fields: {len(expected_fields)}")
            print(f"   - Actual fields: {len(actual_fields)}")
            
            missing_fields = expected_fields - actual_fields
            extra_fields = actual_fields - expected_fields
            
            if missing_fields:
                print(f"   ⚠️ Thiếu trường: {missing_fields}")
            else:
                print(f"   ✅ Không thiếu trường nào")
            
            if extra_fields:
                print(f"   ℹ️ Trường thừa: {extra_fields}")
            else:
                print(f"   ✅ Không có trường thừa")
            
            # Test tạo contract như frontend sẽ làm
            print(f"\n🎯 Test tạo payment request như frontend:")
            
            result = contract_generator.generate_contract(
                contract_type="payment_request",
                customer_id=customer.customer_id,
                contract_id=contract.contract_id,
                output_filename=f"frontend_test_payment_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            )
            
            if result['success']:
                print(f"✅ Tạo payment request thành công!")
                if 'output_filename' in result:
                    print(f"📄 File: {result['output_filename']}")
                if 'output_path' in result:
                    print(f"📁 Full path: {result['output_path']}")
                
                # Kiểm tra file đã tạo
                output_path = result.get('output_path')
                if output_path and os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"📁 File size: {file_size:,} bytes")
                    
                    if file_size > 50000:  # File Word thường > 50KB
                        print(f"✅ File có kích thước hợp lý")
                    else:
                        print(f"⚠️ File có thể bị lỗi (quá nhỏ)")
                else:
                    print(f"❌ File không được tạo hoặc không tìm thấy")
            else:
                print(f"❌ Lỗi tạo payment request: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_frontend_integration() 