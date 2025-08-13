#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal

# Thêm đường dẫn để import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def number_to_words_vietnamese(number):
    """Chuyển số thành chữ tiếng Việt"""
    units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    teens = ["mười", "mười một", "mười hai", "mười ba", "mười bốn", "mười lăm", "mười sáu", "mười bảy", "mười tám", "mười chín"]
    tens = ["", "", "hai mươi", "ba mươi", "bốn mươi", "năm mươi", "sáu mươi", "bảy mươi", "tám mươi", "chín mươi"]
    
    def convert_less_than_one_thousand(n):
        if n == 0:
            return ""
        
        if n < 10:
            return units[n]
        elif n < 20:
            return teens[n - 10]
        elif n < 100:
            if n % 10 == 0:
                return tens[n // 10]
            else:
                return tens[n // 10] + " " + units[n % 10]
        else:
            if n % 100 == 0:
                return units[n // 100] + " trăm"
            else:
                return units[n // 100] + " trăm " + convert_less_than_one_thousand(n % 100)
    
    if number == 0:
        return "không đồng"
    
    # Xử lý phần nguyên
    integer_part = int(number)
    decimal_part = int((number - integer_part) * 100)
    
    if integer_part == 0:
        result = "không"
    else:
        result = ""
        
        # Xử lý hàng tỷ
        billions = integer_part // 1000000000
        if billions > 0:
            result += convert_less_than_one_thousand(billions) + " tỷ "
            integer_part %= 1000000000
        
        # Xử lý hàng triệu
        millions = integer_part // 1000000
        if millions > 0:
            result += convert_less_than_one_thousand(millions) + " triệu "
            integer_part %= 1000000
        
        # Xử lý hàng nghìn
        thousands = integer_part // 1000
        if thousands > 0:
            result += convert_less_than_one_thousand(thousands) + " nghìn "
            integer_part %= 1000
        
        # Xử lý phần còn lại
        if integer_part > 0:
            result += convert_less_than_one_thousand(integer_part)
    
    # Xử lý phần thập phân
    if decimal_part > 0:
        result += " phẩy " + convert_less_than_one_thousand(decimal_part)
    
    # Thêm "đồng" vào cuối
    result += " đồng"
    
    return result.strip()

def test_payment_request_complete():
    """Test tạo Payment Request với đầy đủ các trường Jinja"""
    
    print("🚀 Test tạo Payment Request với đầy đủ các trường Jinja")
    print("=" * 70)
    
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
            deposit_amount = float(contract.contract_value) * 2
            total_amount = service_amount + vat_amount
            
            # Chuyển đổi số tiền thành chữ
            amount_in_words = number_to_words_vietnamese(total_amount)
            
            print(f"✅ Service Amount: {service_amount:,} VND")
            print(f"✅ VAT Amount: {vat_amount:,} VND")
            print(f"✅ Deposit Amount: {deposit_amount:,} VND")
            print(f"✅ Total Amount: {total_amount:,} VND")
            print(f"✅ Amount in Words: {amount_in_words}")
            
            # Tạo payment request number unique
            payment_request_number = f'PR20241215{datetime.now().strftime("%H%M%S")}'
            
            # Tạo payment request
            payment_request = PaymentRequest(
                payment_request_number=payment_request_number,
                customer_id=customer.customer_id,
                contract_id=contract.contract_id,
                issue_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=30),
                service_name='Tiền thuê văn phòng dịch vụ',
                service_unit='Tháng',
                service_quantity=12,
                service_unit_price=float(contract.contract_value),
                service_amount=service_amount,
                vat_percentage=10.0,
                vat_amount=vat_amount,
                deposit_amount=deposit_amount,
                total_rental_amount=total_amount,
                amount_in_words=amount_in_words,
                status='pending',
                notes='Payment request với đầy đủ các trường Jinja'
            )
            
            # Lưu vào database
            db.session.add(payment_request)
            db.session.commit()
            
            print("✅ Payment Request đã được lưu vào database!")
            print(f"   Payment Request ID: {payment_request.payment_request_id}")
            print(f"   Payment Request Number: {payment_request.payment_request_number}")
            
            # Chuẩn bị dữ liệu cho template với đầy đủ các trường
            template_data = {
                # Thông tin khách hàng
                'customer_name': customer.customer_name,
                'address': customer.company_name or 'N/A',  # Sử dụng company_name thay cho address
                'tax_id': customer.tax_id or 'N/A',
                'representative': customer.customer_name or 'N/A',  # Sử dụng customer_name thay cho representative
                'position': 'Đại diện',  # Giá trị mặc định
                'mobile': customer.mobile or 'N/A',
                
                # Thông tin dịch vụ chính
                'service_name': payment_request.service_name,
                'service_unit': payment_request.service_unit,
                'service_quantity': str(payment_request.service_quantity),
                'service_unit_price': f"{payment_request.service_unit_price:,}",
                'service_amount': f"{payment_request.service_amount:,}",
                
                # Thông tin đặt cọc
                'deposit_service_name': 'Tiền đặt cọc Deposit',
                'deposit_unit': 'Tháng Month',
                'deposit_quantity': '2',
                'deposit_unit_price': f"{payment_request.service_unit_price:,}",
                'deposit_amount': f"{payment_request.deposit_amount:,}",
                
                # Thông tin thuế
                'vat_amount': f"{payment_request.vat_amount:,}",
                
                # Thông tin tổng hợp
                'total_rental_amount': f"{payment_request.total_rental_amount:,}",
                'total_amount': f"{payment_request.total_rental_amount:,}",
                'amount_in_words': payment_request.amount_in_words,
                
                # Thông tin thời gian
                'issue_date': payment_request.issue_date.strftime('%d/%m/%Y'),
                'due_date': payment_request.due_date.strftime('%d/%m/%Y'),
                'payment_due_date': payment_request.due_date.strftime('%d/%m/%Y'),
                'contract_period': '12 tháng',
                'from_date': contract.contract_start_date.strftime('%d/%m/%Y'),
                'to_date': contract.contract_end_date.strftime('%d/%m/%Y')
            }
            
            print("\n📊 Dữ liệu đầy đủ cho template:")
            print("=" * 50)
            for key, value in template_data.items():
                print(f"   {key}: {value}")
            
            # Render template
            template_path = "templates_jinja/6.1_payment_request_jinja.docx"
            if os.path.exists(template_path):
                print(f"\n🎯 Rendering template: {template_path}")
                
                doc = DocxTemplate(template_path)
                doc.render(template_data)
                
                output_path = f"payment_request_complete_{payment_request.payment_request_number}.docx"
                doc.save(output_path)
                
                print(f"✅ Payment Request đã được tạo thành công!")
                print(f"📄 File: {output_path}")
                print(f"📊 Payment Request ID: {payment_request.payment_request_id}")
                print(f"💰 Total Amount: {payment_request.total_rental_amount:,} VND")
                print(f"📝 Amount in Words: {payment_request.amount_in_words}")
                
                # Kiểm tra file đã tạo
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"📁 File size: {file_size:,} bytes")
                else:
                    print("❌ File không được tạo thành công")
                
            else:
                print(f"❌ Template không tồn tại: {template_path}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_payment_request_complete() 