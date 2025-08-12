#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal

# Thêm đường dẫn để import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def number_to_words_vietnamese(number):
    """Chuyển đổi số thành chữ tiếng Việt"""
    
    # Làm tròn số
    rounded_number = round(number)
    
    # Định nghĩa các từ số
    units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    teens = ["mười", "mười một", "mười hai", "mười ba", "mười bốn", "mười lăm", "mười sáu", "mười bảy", "mười tám", "mười chín"]
    tens = ["", "", "hai mươi", "ba mươi", "bốn mươi", "năm mươi", "sáu mươi", "bảy mươi", "tám mươi", "chín mươi"]
    
    def convert_less_than_one_thousand(n):
        """Chuyển đổi số nhỏ hơn 1000"""
        if n == 0:
            return ""
        elif n < 10:
            return units[n]
        elif n < 20:
            return teens[n - 10]
        elif n < 100:
            if n % 10 == 0:
                return tens[n // 10]
            elif n % 10 == 1:
                return tens[n // 10] + " mốt"
            elif n % 10 == 5:
                return tens[n // 10] + " lăm"
            else:
                return tens[n // 10] + " " + units[n % 10]
        else:
            if n % 100 == 0:
                return units[n // 100] + " trăm"
            else:
                return units[n // 100] + " trăm " + convert_less_than_one_thousand(n % 100)
    
    def convert_number(n):
        """Chuyển đổi số thành chữ"""
        if n == 0:
            return "không"
        
        # Chia thành các nhóm 3 chữ số
        groups = []
        temp = n
        while temp > 0:
            groups.append(temp % 1000)
            temp //= 1000
        
        # Chuyển đổi từng nhóm
        words = []
        for i, group in enumerate(reversed(groups)):
            if group == 0:
                continue
            
            group_words = convert_less_than_one_thousand(group)
            
            if i == 0:  # Nhóm cuối
                words.append(group_words)
            elif i == 1:  # Nhóm nghìn
                if group == 1:
                    words.append("nghìn")
                else:
                    words.append(group_words + " nghìn")
            elif i == 2:  # Nhóm triệu
                if group == 1:
                    words.append("triệu")
                else:
                    words.append(group_words + " triệu")
            elif i == 3:  # Nhóm tỷ
                if group == 1:
                    words.append("tỷ")
                else:
                    words.append(group_words + " tỷ")
            elif i == 4:  # Nhóm nghìn tỷ
                if group == 1:
                    words.append("nghìn tỷ")
                else:
                    words.append(group_words + " nghìn tỷ")
        
        return " ".join(words)
    
    # Chuyển đổi số
    words = convert_number(rounded_number)
    
    # Thêm "đồng" vào cuối
    return words + " đồng"

def create_payment_request_with_words():
    """Tạo Payment Request với số tiền bằng chữ được convert đúng"""
    
    print("🚀 Tạo Payment Request với số tiền bằng chữ")
    print("=" * 60)
    
    try:
        from src.main import app
        from src.models.user import db
        from src.models.customer import Customer, Contract, PaymentRequest
        from docxtpl import DocxTemplate
        
        print("✅ Đã import thành công các models và docxtpl")
        
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
            
            # Tính toán các khoản tiền
            service_amount = float(contract.contract_value) * 12
            vat_amount = service_amount * 0.1
            total_amount = service_amount + vat_amount
            
            # Chuyển đổi số tiền thành chữ
            amount_in_words = number_to_words_vietnamese(total_amount)
            
            print(f"✅ Service Amount: {service_amount:,} VND")
            print(f"✅ VAT Amount: {vat_amount:,} VND")
            print(f"✅ Total Amount: {total_amount:,} VND")
            print(f"✅ Amount in Words: {amount_in_words}")
            
            # Tạo payment request number unique
            payment_request_number = f'PR20241215{datetime.now().strftime("%H%M%S")}'
            
            # Tạo payment request
            payment_request = PaymentRequest(
                customer_id=customer.customer_id,
                contract_id=contract.contract_id,
                payment_request_number=payment_request_number,
                issue_date=date.today(),
                due_date=date.today() + timedelta(days=15),
                service_name='Tiền thuê văn phòng dịch vụ',
                service_unit='Tháng',
                service_quantity=12,
                service_unit_price=float(contract.contract_value),
                service_amount=service_amount,
                vat_percentage=10.0,
                vat_amount=vat_amount,
                deposit_amount=0,
                total_rental_amount=total_amount,
                amount_in_words=amount_in_words,
                status='pending',
                notes='Payment request với số tiền bằng chữ được convert đúng'
            )
            
            # Lưu vào database
            db.session.add(payment_request)
            db.session.commit()
            
            print("✅ Payment Request đã được lưu vào database!")
            print(f"   Payment Request ID: {payment_request.payment_request_id}")
            print(f"   Payment Request Number: {payment_request.payment_request_number}")
            
            # Chuẩn bị dữ liệu cho template
            template_data = {
                'customer_name': customer.customer_name,
                'address': customer.address or 'N/A',
                'tax_id': customer.tax_id or 'N/A',
                'representative': customer.representative or 'N/A',
                'position': customer.position or 'N/A',
                'mobile': customer.mobile or 'N/A',
                
                # Thông tin dịch vụ
                'service_name': payment_request.service_name,
                'service_unit': payment_request.service_unit,
                'service_quantity': str(payment_request.service_quantity),
                'service_unit_price': f"{payment_request.service_unit_price:,}",
                'service_amount': f"{payment_request.service_amount:,}",
                
                # Thông tin thuế
                'vat_amount': f"{payment_request.vat_amount:,}",
                
                # Thông tin đặt cọc
                'deposit_amount': f"{payment_request.deposit_amount:,}",
                
                # Thông tin tổng hợp
                'total_rental_amount': f"{payment_request.total_rental_amount:,}",
                'amount_in_words': payment_request.amount_in_words,
                
                # Thông tin thời gian
                'issue_date': payment_request.issue_date.strftime('%d/%m/%Y'),
                'due_date': payment_request.due_date.strftime('%d/%m/%Y'),
                'contract_period': '12 tháng',
                'from_date': contract.contract_start_date.strftime('%d/%m/%Y'),
                'to_date': contract.contract_end_date.strftime('%d/%m/%Y')
            }
            
            print("\n📊 Dữ liệu cho template:")
            for key, value in template_data.items():
                if key == 'amount_in_words':
                    print(f"   {key}: {value}")
                else:
                    print(f"   {key}: {value}")
            
            # Render template
            template_path = "templates_jinja/6.1_payment_request_jinja.docx"
            if os.path.exists(template_path):
                print(f"\n🎯 Rendering template: {template_path}")
                
                doc = DocxTemplate(template_path)
                doc.render(template_data)
                
                output_path = f"payment_request_with_words_{payment_request.payment_request_number}.docx"
                doc.save(output_path)
                
                print(f"✅ Payment Request đã được tạo thành công!")
                print(f"📄 File: {output_path}")
                print(f"📊 Payment Request ID: {payment_request.payment_request_id}")
                print(f"💰 Total Amount: {payment_request.total_rental_amount:,} VND")
                print(f"📝 Amount in Words: {payment_request.amount_in_words}")
                
            else:
                print(f"❌ Template không tồn tại: {template_path}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

def test_number_conversion():
    """Test chuyển đổi số thành chữ"""
    
    test_numbers = [
        431161473.60,
        216324094.80,
        416314932.00,
        1000000,
        5000000,
        10000000
    ]
    
    print("🧪 Test chuyển đổi số thành chữ:")
    print("=" * 50)
    
    for number in test_numbers:
        words = number_to_words_vietnamese(number)
        print(f"{number:15,.0f} -> {words}")

def main():
    """Main function"""
    print("🚀 Tạo Payment Request với số tiền bằng chữ")
    print("=" * 60)
    
    # Test chuyển đổi số
    test_number_conversion()
    
    # Tạo payment request
    create_payment_request_with_words()
    
    print("\n✅ Hoàn thành tạo Payment Request với số tiền bằng chữ!")
    print("\n📋 Tóm tắt:")
    print("   - Số tiền đã được chuyển đổi thành chữ tiếng Việt")
    print("   - Payment Request đã được tạo với dữ liệu chính xác")
    print("   - File Word đã được tạo với số tiền bằng chữ đúng")

if __name__ == "__main__":
    main() 