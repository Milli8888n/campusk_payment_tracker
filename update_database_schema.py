#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

# Thêm đường dẫn để import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def update_database_schema():
    """Cập nhật database schema để thêm bảng payment_requests"""
    
    print("🚀 Cập nhật Database Schema")
    print("=" * 50)
    
    try:
        from src.main import app
        from src.models.user import db
        from src.models.customer import PaymentRequest
        
        print("✅ Đã import thành công các models")
        
        # Sử dụng application context
        with app.app_context():
            # Tạo tất cả các bảng
            db.create_all()
            
            print("✅ Đã tạo thành công tất cả các bảng trong database")
            print("✅ Bảng payment_requests đã được thêm vào database")
            
            # Kiểm tra xem bảng đã được tạo chưa
            try:
                # Thử query bảng payment_requests
                result = db.session.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payment_requests'")
                if result.fetchone():
                    print("✅ Bảng payment_requests đã tồn tại trong database")
                else:
                    print("❌ Bảng payment_requests chưa được tạo")
            except Exception as e:
                print(f"⚠️ Không thể kiểm tra bảng: {e}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_database_schema() 