#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime, timedelta

# Thêm đường dẫn để import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_template_fields():
    """Debug các trường Jinja trong template"""
    
    print("🔍 Debug Template Fields")
    print("=" * 50)
    
    try:
        from docxtpl import DocxTemplate
        
        # Đường dẫn template
        template_path = "templates_jinja/6.1_payment_request_jinja.docx"
        
        if not os.path.exists(template_path):
            print(f"❌ Template không tồn tại: {template_path}")
            return
        
        print(f"✅ Template tồn tại: {template_path}")
        
        # Tạo dữ liệu test với tất cả các trường có thể có
        test_data = {
            # Thông tin khách hàng
            'customer_name': 'CÔNG TY TNHH ABC TEST',
            'address': '123 Đường ABC, Quận 1, TP.HCM',
            'tax_id': '0123456789',
            'representative': 'Nguyễn Văn Test',
            'position': 'Giám đốc',
            'mobile': '0901234567',
            
            # Thông tin dịch vụ chính
            'service_name': 'Tiền thuê văn phòng dịch vụ',
            'service_unit': 'Tháng',
            'service_quantity': '12',
            'service_unit_price': '5,000,000',
            'service_amount': '60,000,000',
            
            # Thông tin đặt cọc
            'deposit_service_name': 'Tiền đặt cọc Deposit',
            'deposit_unit': 'Tháng Month',
            'deposit_quantity': '2',
            'deposit_unit_price': '5,000,000',
            'deposit_amount': '10,000,000',
            
            # Thông tin thuế
            'vat_amount': '6,000,000',
            
            # Thông tin tổng hợp
            'total_rental_amount': '66,000,000',
            'total_amount': '66,000,000',
            'amount_in_words': 'sáu mươi sáu triệu đồng',
            
            # Thông tin thời gian
            'issue_date': '15/08/2025',
            'due_date': '15/09/2025',
            'payment_due_date': '15/09/2025',
            'contract_period': '12 tháng',
            'from_date': '01/01/2025',
            'to_date': '31/12/2025'
        }
        
        print("\n📊 Dữ liệu test:")
        for key, value in test_data.items():
            print(f"   {key}: {value}")
        
        # Thử render template
        print(f"\n🎯 Rendering template...")
        doc = DocxTemplate(template_path)
        
        # Kiểm tra các trường Jinja trong template
        print("\n🔍 Kiểm tra các trường Jinja trong template:")
        template_vars = doc.get_undeclared_template_variables()
        print(f"   Các biến Jinja được tìm thấy: {template_vars}")
        
        # Render template
        doc.render(test_data)
        
        # Lưu file test
        output_path = f"debug_template_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        doc.save(output_path)
        
        print(f"\n✅ File test đã được tạo: {output_path}")
        
        # Kiểm tra file size
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"📁 File size: {file_size:,} bytes")
        
        # So sánh với dữ liệu gốc
        print(f"\n📋 So sánh dữ liệu:")
        print(f"   - Template variables: {len(template_vars)}")
        print(f"   - Test data fields: {len(test_data)}")
        
        # Kiểm tra các trường thiếu
        missing_vars = set(template_vars) - set(test_data.keys())
        extra_vars = set(test_data.keys()) - set(template_vars)
        
        if missing_vars:
            print(f"   ⚠️ Các trường thiếu trong test_data: {missing_vars}")
        
        if extra_vars:
            print(f"   ℹ️ Các trường thừa trong test_data: {extra_vars}")
        
        if not missing_vars and not extra_vars:
            print(f"   ✅ Tất cả trường đều khớp!")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_template_fields() 