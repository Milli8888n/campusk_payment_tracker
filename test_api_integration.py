#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import requests
from datetime import datetime

# Thêm đường dẫn để import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_api_integration():
    """Test tích hợp API như frontend sẽ gọi"""
    
    print("🚀 Test tích hợp API như Frontend")
    print("=" * 50)
    
    try:
        from src.main import app
        from src.models.user import db
        from src.models.customer import Customer, Contract
        
        print("✅ Đã import thành công các models")
        
        # Sử dụng application context
        with app.app_context():
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
            
            # Chuẩn bị request data như frontend sẽ gửi
            request_data = {
                "contract_type": "payment_request",
                "customer_id": customer.customer_id,
                "contract_id": contract.contract_id,
                "output_filename": f"api_test_payment_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            }
            
            print(f"\n📊 Request data:")
            print(json.dumps(request_data, indent=2, default=str))
            
            # Test API call như frontend sẽ làm
            print(f"\n🎯 Test API call:")
            
            # Sử dụng Flask test client thay vì requests
            with app.test_client() as client:
                response = client.post(
                    '/api/contracts/generate',
                    data=json.dumps(request_data),
                    content_type='application/json'
                )
                
                print(f"   Status Code: {response.status_code}")
                print(f"   Response Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    response_data = response.get_json()
                    print(f"✅ API call thành công!")
                    print(f"📄 Response: {json.dumps(response_data, indent=2, default=str)}")
                    
                    # Kiểm tra file đã được tạo
                    if 'data' in response_data and 'output_path' in response_data['data']:
                        output_path = response_data['data']['output_path']
                        if os.path.exists(output_path):
                            file_size = os.path.getsize(output_path)
                            print(f"📁 File size: {file_size:,} bytes")
                            
                            if file_size > 50000:  # File Word thường > 50KB
                                print(f"✅ File có kích thước hợp lý")
                                
                                # Kiểm tra xem file có chứa thông tin không
                                print(f"📄 File path: {output_path}")
                                print(f"✅ Payment request đã được tạo thành công qua API!")
                            else:
                                print(f"⚠️ File có thể bị lỗi (quá nhỏ)")
                        else:
                            print(f"❌ File không được tạo")
                    else:
                        print(f"❌ Response không chứa thông tin file")
                else:
                    print(f"❌ API call thất bại!")
                    try:
                        error_data = response.get_json()
                        print(f"   Error: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"   Error: {response.data.decode()}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_integration() 