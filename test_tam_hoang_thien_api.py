#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_tam_hoang_thien_api():
    """Test API integration cho Tâm Hoàng Thiện"""
    print("🚀 Test API integration cho Tâm Hoàng Thiện")
    print("=" * 50)
    
    try:
        from src.main import app
        
        with app.test_client() as client:
            # Test data
            request_data = {
                "contract_type": "payment_request",
                "customer_id": 11,  # Tâm Hoàng Thiện
                "contract_id": 18,  # Hợp đồng của Tâm Hoàng Thiện
                "output_filename": f"api_tam_hoang_thien_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            }
            
            print(f"📊 Request data:")
            print(json.dumps(request_data, indent=2, ensure_ascii=False))
            
            # Gọi API
            print(f"\n🎯 Test API call:")
            response = client.post('/api/contracts/generate', 
                                json=request_data,
                                headers={'Content-Type': 'application/json'})
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ API call thành công!")
                response_data = response.get_json()
                print(f"📄 Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Kiểm tra file được tạo
                if response_data.get('data', {}).get('success'):
                    output_path = response_data['data']['output_path']
                    if os.path.exists(output_path):
                        file_size = os.path.getsize(output_path)
                        print(f"📁 File size: {file_size:,} bytes")
                        print(f"✅ File đã được tạo thành công!")
                    else:
                        print("❌ File không tồn tại")
                else:
                    print("❌ API trả về success=False")
            else:
                print("❌ API call thất bại!")
                print(f"   Response: {response.get_data(as_text=True)}")
                
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tam_hoang_thien_api() 