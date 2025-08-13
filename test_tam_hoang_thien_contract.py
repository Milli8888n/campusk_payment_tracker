#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_tam_hoang_thien_contract():
    """Test tạo payment request cho Tâm Hoàng Thiện"""
    print("🚀 Test tạo payment request cho Tâm Hoàng Thiện")
    print("=" * 50)
    
    try:
        from src.main import app
        from src.contract_generator import ContractGenerator
        
        with app.app_context():
            # Khởi tạo contract generator
            generator = ContractGenerator()
            
            # Test với customer_id = 11 (Tâm Hoàng Thiện)
            result = generator.generate_contract(
                contract_type="payment_request",
                customer_id=11,  # Tâm Hoàng Thiện
                contract_id=18,  # Hợp đồng của Tâm Hoàng Thiện
                output_filename="test_tam_hoang_thien.docx"
            )
            
            print(f"📊 Kết quả:")
            print(f"   Success: {result.get('success')}")
            
            if result.get('success'):
                print(f"   File: {result.get('filename')}")
                print(f"   Path: {result.get('output_path')}")
                print("✅ Tạo thành công!")
            else:
                print(f"   Error: {result.get('error')}")
                print("❌ Tạo thất bại!")
                
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tam_hoang_thien_contract() 