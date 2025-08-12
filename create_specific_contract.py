#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal

# Thêm đường dẫn để import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_specific_contract(contract_type, customer_id=None, output_filename=None):
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
            return None
        
        template_path = f"templates_jinja/{contract_templates[contract_type]}"
        
        if not os.path.exists(template_path):
            print(f"❌ Template không tồn tại: {template_path}")
            return None
        
        # Sử dụng application context
        with app.app_context():
            # Lấy customer
            if customer_id:
                customer = Customer.query.get(customer_id)
                if not customer:
                    print(f"❌ Không tìm thấy customer với ID: {customer_id}")
                    return None
                customers = [customer]
            else:
                customers = db.session.query(Customer).join(Contract).all()[:1]  # Chỉ lấy 1 customer
            
            if not customers:
                print("❌ Không tìm thấy customer nào có contract")
                return None
            
            customer = customers[0]
            contract = customer.contracts[0]
            
            print(f"✅ Sử dụng customer: {customer.customer_name}")
            print(f"✅ Contract ID: {contract.contract_id}")
            print(f"✅ Contract Value: {contract.contract_value:,} VND")
            
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
            
            print(f"\n📊 Dữ liệu cho template:")
            for key, value in template_data.items():
                print(f"   {key}: {value}")
            
            # Render template
            try:
                doc = DocxTemplate(template_path)
                doc.render(template_data)
                
                # Tạo tên file output
                if output_filename:
                    if not output_filename.endswith('.docx'):
                        output_filename += '.docx'
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"{contract_type}_{customer.customer_id}_{contract.contract_id}_{timestamp}.docx"
                
                # Tạo thư mục output nếu chưa có
                output_dir = "generated_contracts"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                output_path = os.path.join(output_dir, output_filename)
                doc.save(output_path)
                
                print(f"\n✅ Đã tạo hợp đồng thành công!")
                print(f"📄 File: {output_filename}")
                print(f"📁 Đường dẫn: {output_path}")
                print(f"📊 Customer: {customer.customer_name}")
                print(f"💰 Contract Value: {contract.contract_value:,} VND")
                
                return output_path
                
            except Exception as e:
                print(f"❌ Lỗi khi tạo hợp đồng: {e}")
                import traceback
                traceback.print_exc()
                return None
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return None

def list_available_contract_types():
    """Liệt kê các loại hợp đồng có sẵn"""
    
    print("📋 Các loại hợp đồng có sẵn:")
    print("=" * 50)
    
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
    
    contract_descriptions = {
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
    
    for contract_type, template_file in contract_templates.items():
        template_path = f"templates_jinja/{template_file}"
        description = contract_descriptions.get(contract_type, contract_type)
        
        if os.path.exists(template_path):
            print(f"✅ {contract_type}: {description}")
        else:
            print(f"❌ {contract_type}: {description} (template không tồn tại)")

def show_usage_examples():
    """Hiển thị ví dụ sử dụng"""
    
    print("\n📖 Ví dụ sử dụng:")
    print("=" * 30)
    print("1. Tạo hợp đồng Virtual Office:")
    print("   python create_specific_contract.py virtual_office")
    print()
    print("2. Tạo hợp đồng Private Office cho customer cụ thể:")
    print("   python create_specific_contract.py private_office 14")
    print()
    print("3. Tạo hợp đồng với tên file tùy chỉnh:")
    print("   python create_specific_contract.py hot_desk 15 my_contract.docx")
    print()
    print("4. Liệt kê các loại hợp đồng có sẵn:")
    print("   python create_specific_contract.py list")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("🚀 Tạo hợp đồng cho loại cụ thể")
        print("=" * 60)
        list_available_contract_types()
        show_usage_examples()
        return
    
    contract_type = sys.argv[1]
    
    if contract_type == "list":
        list_available_contract_types()
        return
    
    customer_id = None
    output_filename = None
    
    if len(sys.argv) >= 3:
        try:
            customer_id = int(sys.argv[2])
        except ValueError:
            output_filename = sys.argv[2]
    
    if len(sys.argv) >= 4:
        output_filename = sys.argv[3]
    
    # Tạo hợp đồng
    result = create_specific_contract(contract_type, customer_id, output_filename)
    
    if result:
        print(f"\n✅ Hoàn thành tạo hợp đồng {contract_type}!")
        print(f"📄 File đã được lưu: {result}")
    else:
        print(f"\n❌ Không thể tạo hợp đồng {contract_type}")

if __name__ == "__main__":
    main() 