#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_number_to_words():
    """Debug hàm number_to_words với số lớn"""
    print("🚀 Debug hàm number_to_words")
    print("=" * 50)
    
    try:
        from src.contract_generator import ContractGenerator
        
        # Khởi tạo generator
        generator = ContractGenerator()
        
        # Test với số nhỏ trước
        print("📊 Test số nhỏ:")
        test_numbers = [1000, 10000, 100000, 1000000]
        for num in test_numbers:
            try:
                result = generator.number_to_words(num)
                print(f"   {num:,} → {result}")
            except Exception as e:
                print(f"   ❌ {num:,} → Lỗi: {e}")
        
        # Test với số của Tâm Hoàng Thiện
        print("\n📊 Test số của Tâm Hoàng Thiện:")
        tam_contract_value = 12313132132213132.00
        print(f"   Số gốc: {tam_contract_value}")
        
        try:
            result = generator.number_to_words(tam_contract_value)
            print(f"   ✅ Kết quả: {result}")
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
            import traceback
            traceback.print_exc()
            
        # Test với Decimal
        print("\n📊 Test với Decimal:")
        try:
            decimal_value = Decimal(str(tam_contract_value))
            print(f"   Decimal: {decimal_value}")
            result = generator.number_to_words(float(decimal_value))
            print(f"   ✅ Kết quả: {result}")
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_number_to_words() 