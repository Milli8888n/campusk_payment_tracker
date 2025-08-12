#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal

# Thêm đường dẫn để import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_all_remaining_contracts():
    """Tạo tất cả các hợp đồng còn lại từ các template Jinja"""
    
    print("🚀 Tạo tất cả các hợp đồng còn lại")
    print("=" * 60)
    
    try:
        from src.main import app
        from src.models.user import db
        from src.models.customer import Customer, Contract
        from docxtpl import DocxTemplate
        
        print("✅ Đã import thành công các models và docxtpl")
        
        # Định nghĩa các loại hợp đồng và template tương ứng
        contract_types = {
            "virtual_office": {
                "template": "1.1_virtual_office_jinja.docx",
                "description": "Virtual Office Contract",
                "output_prefix": "virtual_office"
            },
            "private_office": {
                "template": "2.1_private_office_jinja.docx",
                "description": "Private Office Contract",
                "output_prefix": "private_office"
            },
            "hot_desk": {
                "template": "4.1_hot_desk_jinja.docx",
                "description": "Hot Desk Contract",
                "output_prefix": "hot_desk"
            },
            "event_space": {
                "template": "3.1_event_contract_jinja.docx",
                "description": "Event Space Contract",
                "output_prefix": "event_space"
            },
            "event_space_bbtl": {
                "template": "3.2_event_contract_bbtl_jinja.docx",
                "description": "Event Space BBTL Contract",
                "output_prefix": "event_space_bbtl"
            },
            "renewal_vo": {
                "template": "1.3_renewal_vo_jinja.docx",
                "description": "Virtual Office Renewal Contract",
                "output_prefix": "renewal_vo"
            },
            "liquidation_vo": {
                "template": "1.2_liquidation_vo_jinja.docx",
                "description": "Virtual Office Liquidation Contract",
                "output_prefix": "liquidation_vo"
            },
            "name_change_po": {
                "template": "2.2_name_change_po_jinja.docx",
                "description": "Private Office Name Change Contract",
                "output_prefix": "name_change_po"
            },
            "liquidation_po": {
                "template": "2.4_liquidation_po_jinja.docx",
                "description": "Private Office Liquidation Contract",
                "output_prefix": "liquidation_po"
            }
        }
        
        # Sử dụng application context
        with app.app_context():
            # Lấy tất cả customers có contract
            customers_with_contracts = db.session.query(Customer).join(Contract).all()
            
            if not customers_with_contracts:
                print("❌ Không tìm thấy customer nào có contract")
                return
            
            print(f"✅ Tìm thấy {len(customers_with_contracts)} customers có contract")
            
            # Tạo thư mục generated_contracts nếu chưa có
            output_dir = "generated_contracts"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"✅ Đã tạo thư mục: {output_dir}")
            
            total_contracts_created = 0
            
            # Tạo hợp đồng cho từng loại
            for contract_type, config in contract_types.items():
                template_path = f"templates_jinja/{config['template']}"
                
                if not os.path.exists(template_path):
                    print(f"❌ Template không tồn tại: {template_path}")
                    continue
                
                print(f"\n📄 Tạo hợp đồng: {config['description']}")
                print(f"   Template: {config['template']}")
                
                contracts_created = 0
                
                # Tạo hợp đồng cho từng customer
                for i, customer in enumerate(customers_with_contracts[:3]):  # Chỉ tạo cho 3 customer đầu
                    contract = customer.contracts[0]
                    
                    # Chuẩn bị dữ liệu cho template
                    template_data = {
                        'customer_name': customer.customer_name,
                        'address': customer.address or 'N/A',
                        'tax_id': customer.tax_id or 'N/A',
                        'representative': customer.representative or 'N/A',
                        'position': customer.position or 'N/A',
                        'mobile': customer.mobile or 'N/A',
                        'account_number': customer.account_number or 'N/A',
                        'bank_name': customer.bank_name or 'N/A',
                        'bank_branch': customer.bank_branch or 'N/A',
                        'contract_value': f"{contract.contract_value:,}",
                        'deposit_amount': "0",  # Mặc định là 0 vì không có trường này trong Contract model
                        'from_date': contract.contract_start_date.strftime('%d/%m/%Y'),
                        'to_date': contract.contract_end_date.strftime('%d/%m/%Y'),
                        'birth_date': customer.birth_date.strftime('%d/%m/%Y') if customer.birth_date else 'N/A',
                        'id_card': customer.id_card or 'N/A'
                    }
                    
                    # Render template
                    try:
                        doc = DocxTemplate(template_path)
                        doc.render(template_data)
                        
                        # Tạo tên file output
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_filename = f"{config['output_prefix']}_{customer.customer_id}_{contract.contract_id}_{timestamp}.docx"
                        output_path = os.path.join(output_dir, output_filename)
                        
                        doc.save(output_path)
                        
                        print(f"   ✅ Customer {customer.customer_id}: {output_filename}")
                        contracts_created += 1
                        total_contracts_created += 1
                        
                    except Exception as e:
                        print(f"   ❌ Lỗi khi tạo hợp đồng cho customer {customer.customer_id}: {e}")
                
                print(f"   📊 Đã tạo {contracts_created} hợp đồng {contract_type}")
            
            print(f"\n✅ Hoàn thành tạo tất cả hợp đồng!")
            print(f"📊 Tổng số hợp đồng đã tạo: {total_contracts_created}")
            print(f"📁 Thư mục chứa file: {output_dir}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

def create_specific_contract_type(contract_type, customer_id=None):
    """Tạo hợp đồng cho một loại cụ thể"""
    
    print(f"🚀 Tạo hợp đồng loại: {contract_type}")
    print("=" * 60)
    
    try:
        from src.main import app
        from src.models.user import db
        from src.models.customer import Customer, Contract
        from docxtpl import DocxTemplate
        
        # Mapping loại hợp đồng với template
        contract_templates = {
            "virtual_office": "1.1_virtual_office_jinja.docx",
            "private_office": "2.1_private_office_jinja.docx",
            "hot_desk": "4.1_hot_desk_jinja.docx",
            "event_space": "3.1_event_contract_jinja.docx",
            "event_space_bbtl": "3.2_event_contract_bbtl_jinja.docx",
            "renewal_vo": "1.3_renewal_vo_jinja.docx",
            "liquidation_vo": "1.2_liquidation_vo_jinja.docx",
            "name_change_po": "2.2_name_change_po_jinja.docx",
            "liquidation_po": "2.4_liquidation_po_jinja.docx"
        }
        
        if contract_type not in contract_templates:
            print(f"❌ Loại hợp đồng không hợp lệ: {contract_type}")
            print(f"✅ Các loại hợp đồng có sẵn: {list(contract_templates.keys())}")
            return
        
        template_path = f"templates_jinja/{contract_templates[contract_type]}"
        
        if not os.path.exists(template_path):
            print(f"❌ Template không tồn tại: {template_path}")
            return
        
        # Sử dụng application context
        with app.app_context():
            # Lấy customer
            if customer_id:
                customer = Customer.query.get(customer_id)
                if not customer:
                    print(f"❌ Không tìm thấy customer với ID: {customer_id}")
                    return
                customers = [customer]
            else:
                customers = db.session.query(Customer).join(Contract).all()[:3]
            
            if not customers:
                print("❌ Không tìm thấy customer nào có contract")
                return
            
            # Tạo thư mục output
            output_dir = "generated_contracts"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            contracts_created = 0
            
            for customer in customers:
                contract = customer.contracts[0]
                
                # Chuẩn bị dữ liệu
                template_data = {
                    'customer_name': customer.customer_name,
                    'address': customer.address or 'N/A',
                    'tax_id': customer.tax_id or 'N/A',
                    'representative': customer.representative or 'N/A',
                    'position': customer.position or 'N/A',
                    'mobile': customer.mobile or 'N/A',
                    'account_number': customer.account_number or 'N/A',
                    'bank_name': customer.bank_name or 'N/A',
                    'bank_branch': customer.bank_branch or 'N/A',
                    'contract_value': f"{contract.contract_value:,}",
                    'deposit_amount': "0",  # Mặc định là 0 vì không có trường này trong Contract model
                    'from_date': contract.contract_start_date.strftime('%d/%m/%Y'),
                    'to_date': contract.contract_end_date.strftime('%d/%m/%Y'),
                    'birth_date': customer.birth_date.strftime('%d/%m/%Y') if customer.birth_date else 'N/A',
                    'id_card': customer.id_card or 'N/A'
                }
                
                # Render template
                try:
                    doc = DocxTemplate(template_path)
                    doc.render(template_data)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"{contract_type}_{customer.customer_id}_{contract.contract_id}_{timestamp}.docx"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    doc.save(output_path)
                    
                    print(f"✅ Đã tạo: {output_filename}")
                    contracts_created += 1
                    
                except Exception as e:
                    print(f"❌ Lỗi khi tạo hợp đồng cho customer {customer.customer_id}: {e}")
            
            print(f"\n✅ Hoàn thành tạo {contracts_created} hợp đồng {contract_type}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

def list_available_contract_types():
    """Liệt kê các loại hợp đồng có sẵn"""
    
    print("📋 Các loại hợp đồng có sẵn:")
    print("=" * 50)
    
    contract_types = {
        "virtual_office": "Virtual Office Contract",
        "private_office": "Private Office Contract", 
        "hot_desk": "Hot Desk Contract",
        "event_space": "Event Space Contract",
        "event_space_bbtl": "Event Space BBTL Contract",
        "renewal_vo": "Virtual Office Renewal Contract",
        "liquidation_vo": "Virtual Office Liquidation Contract",
        "name_change_po": "Private Office Name Change Contract",
        "liquidation_po": "Private Office Liquidation Contract"
    }
    
    for contract_type, description in contract_types.items():
        template_path = f"templates_jinja/{contract_type.replace('_', '.')}_jinja.docx"
        if os.path.exists(template_path):
            print(f"✅ {contract_type}: {description}")
        else:
            print(f"❌ {contract_type}: {description} (template không tồn tại)")

def main():
    """Main function"""
    print("🚀 Tạo tất cả các hợp đồng còn lại")
    print("=" * 60)
    
    # Liệt kê các loại hợp đồng có sẵn
    list_available_contract_types()
    
    # Tạo tất cả hợp đồng
    create_all_remaining_contracts()
    
    print("\n✅ Hoàn thành tạo tất cả hợp đồng!")
    print("\n📋 Tóm tắt:")
    print("   - Đã tạo tất cả các loại hợp đồng có sẵn")
    print("   - Files đã được lưu trong thư mục generated_contracts/")
    print("   - Mỗi hợp đồng có dữ liệu thực từ database")
    print("   - Sẵn sàng sử dụng!")

if __name__ == "__main__":
    main() 