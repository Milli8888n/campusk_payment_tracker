#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal

# Thêm đường dẫn để import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_multiple_payment_requests():
    """Tạo nhiều payment request với dữ liệu khác nhau"""
    
    print("🚀 Tạo nhiều Payment Request với dữ liệu khác nhau")
    print("=" * 60)
    
    try:
        from src.main import app
        from src.models.user import db
        from src.models.customer import Customer, Contract, PaymentRequest
        from docxtpl import DocxTemplate
        
        print("✅ Đã import thành công các models và docxtpl")
        
        # Sử dụng application context
        with app.app_context():
            # Lấy tất cả customers có contract
            customers_with_contracts = db.session.query(Customer).join(Contract).all()
            
            if not customers_with_contracts:
                print("❌ Không tìm thấy customer nào có contract")
                return
            
            print(f"✅ Tìm thấy {len(customers_with_contracts)} customers có contract")
            
            # Tạo payment request cho từng customer
            for i, customer in enumerate(customers_with_contracts[:3]):  # Chỉ tạo 3 payment request
                contract = customer.contracts[0]
                
                # Tạo payment request number unique
                payment_request_number = f'PR20241215{str(i+1).zfill(3)}'
                
                print(f"\n📋 Tạo Payment Request {i+1}:")
                print(f"   Customer: {customer.customer_name}")
                print(f"   Contract Value: {contract.contract_value:,} VND")
                
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
                    service_amount=float(contract.contract_value) * 12,
                    vat_percentage=10.0,
                    vat_amount=float(contract.contract_value) * 12 * 0.1,
                    deposit_amount=0,
                    total_rental_amount=float(contract.contract_value) * 12 * 1.1,
                    amount_in_words='Số tiền bằng chữ',
                    status='pending',
                    notes=f'Payment request {i+1} được tạo tự động từ hệ thống'
                )
                
                # Lưu vào database
                db.session.add(payment_request)
                db.session.commit()
                
                print(f"   ✅ Payment Request ID: {payment_request.payment_request_id}")
                print(f"   ✅ Payment Request Number: {payment_request.payment_request_number}")
                print(f"   ✅ Total Amount: {payment_request.total_rental_amount:,} VND")
                
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
                
                # Render template
                template_path = "templates_jinja/6.1_payment_request_jinja.docx"
                if os.path.exists(template_path):
                    doc = DocxTemplate(template_path)
                    doc.render(template_data)
                    
                    output_path = f"payment_request_{payment_request.payment_request_number}.docx"
                    doc.save(output_path)
                    
                    print(f"   📄 File: {output_path}")
                    
                else:
                    print(f"   ❌ Template không tồn tại: {template_path}")
            
            print(f"\n✅ Đã tạo thành công {len(customers_with_contracts[:3])} Payment Requests!")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

def list_existing_payment_requests():
    """Liệt kê các payment request đã có"""
    
    print("\n📋 Liệt kê các Payment Request đã có:")
    print("=" * 50)
    
    try:
        from src.main import app
        from src.models.customer import PaymentRequest, Customer, Contract
        
        with app.app_context():
            payment_requests = PaymentRequest.query.all()
            
            if not payment_requests:
                print("❌ Chưa có Payment Request nào")
                return
            
            print(f"✅ Tìm thấy {len(payment_requests)} Payment Requests:")
            
            for pr in payment_requests:
                customer = Customer.query.get(pr.customer_id)
                contract = Contract.query.get(pr.contract_id) if pr.contract_id else None
                
                print(f"\n📄 Payment Request ID: {pr.payment_request_id}")
                print(f"   Number: {pr.payment_request_number}")
                print(f"   Customer: {customer.customer_name if customer else 'N/A'}")
                print(f"   Contract Value: {contract.contract_value:,} VND" if contract else "   Contract: N/A")
                print(f"   Total Amount: {pr.total_rental_amount:,} VND")
                print(f"   Status: {pr.status}")
                print(f"   Issue Date: {pr.issue_date}")
                print(f"   Due Date: {pr.due_date}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")

def main():
    """Main function"""
    print("🚀 Tạo nhiều Payment Request với dữ liệu khác nhau")
    print("=" * 60)
    
    # Liệt kê payment requests hiện có
    list_existing_payment_requests()
    
    # Tạo nhiều payment request
    create_multiple_payment_requests()
    
    print("\n✅ Hoàn thành tạo nhiều Payment Request!")
    print("\n📋 Tóm tắt:")
    print("   - Đã tạo nhiều Payment Request với dữ liệu khác nhau")
    print("   - Mỗi Payment Request có số unique")
    print("   - File Word đã được tạo cho từng Payment Request")
    print("   - Tất cả đã được lưu vào database")

if __name__ == "__main__":
    main() 