import os
import json
from datetime import datetime, date
from decimal import Decimal
from docxtpl import DocxTemplate
from src.models.customer import Customer, Contract
from src.models.room import Branch, Room, RoomBooking

class ContractGenerator:
    """Hệ thống tạo hợp đồng tự động từ template"""
    
    # Mapping trường thông tin với số đánh dấu trong template
    FIELD_MAPPING = {
        "1": "customer_name",           # BÊN THUÊ / THE LESSEE
        "2": "address",                 # ĐỊA CHỈ / ADDRESS
        "3": "tax_id",                  # MST / TAX CODE
        "4": "representative",          # ĐẠI DIỆN BỞI / REPRESENTED BY
        "5": "mobile",                  # SỐ ĐIỆN THOẠI / TEL
        "6": "bank_account",            # TÊN TÀI KHOẢN / BANK ACCOUNT
        "7": "account_number",          # STK / ACCOUNT NUMBER
        "8": "bank_name",               # NGÂN HÀNG / BANK NAME
        "9": "bank_branch",             # CHI NHÁNH / BRANCH
        "10": "position",               # CHỨC VỤ / POSITION
        "11": "contract_value",         # TỔNG GIÁ TRỊ HỢP ĐỒNG / CONTRACT VALUE
        "12": "deposit_amount",         # SỐ TIỀN ĐẶT CỌC / DEPOSIT AMOUNT
        "13": "from_date",              # TỪ (FROM) / FROM
        "14": "birth_date",             # NGÀY SINH / BIRTH DATE
        "15": "id_card",                # SỐ CMND/HỘ CHIẾU / ID CARD
        "16": "to_date"                 # THÀNH (TO) / TO
    }
    
    # Mapping loại hợp đồng với template
    CONTRACT_TEMPLATES = {
        "virtual_office": {
            "template_path": "1.1_virtual_office_jinja.docx",
            "output_name": "virtual_office_contract.docx"
        },
        "private_office": {
            "template_path": "2.1_private_office_jinja.docx", 
            "output_name": "private_office_contract.docx"
        },
        "hot_desk": {
            "template_path": "4.1_hot_desk_jinja.docx",
            "output_name": "hot_desk_contract.docx"
        },
        "event_space": {
            "template_path": "3.1_event_contract_jinja.docx",
            "output_name": "event_contract.docx"
        },
        "event_space_bbtl": {
            "template_path": "3.2_event_contract_bbtl_jinja.docx",
            "output_name": "event_contract_bbtl.docx"
        },
        "renewal_vo": {
            "template_path": "1.3_renewal_vo_jinja.docx",
            "output_name": "renewal_vo_contract.docx"
        },
        # "renewal_po": {
        #     "template_path": "2.3_renewal_po_jinja.docx",
        #     "output_name": "renewal_po_contract.docx"
        # },
        "liquidation_vo": {
            "template_path": "1.2_liquidation_vo_jinja.docx",
            "output_name": "liquidation_vo_contract.docx"
        },
        "liquidation_po": {
            "template_path": "2.4_liquidation_po_jinja.docx",
            "output_name": "liquidation_po_contract.docx"
        },
        "name_change_po": {
            "template_path": "2.2_name_change_po_jinja.docx",
            "output_name": "name_change_po_contract.docx"
        },
        # File .doc không được hỗ trợ bởi docxtpl, cần chuyển sang .docx
        "agency_contract": {
            "template_path": "5.1_agency_contract.doc",
            "output_name": "agency_contract.doc",
            "supported": False,
            "note": "Định dạng .doc không được hỗ trợ. Vui lòng chuyển sang định dạng .docx"
        },
        "payment_request": {
            "template_path": "6.1_payment_request_jinja.docx",
            "output_name": "payment_request.docx"
        }
    }
    
    def __init__(self, template_dir="templates_jinja", output_dir="generated_contracts"):
        # Get the absolute path based on the script's location
        script_dir = os.path.dirname(os.path.dirname(__file__))  # Go up 2 levels from src/
        self.template_dir = os.path.join(script_dir, template_dir)
        self.output_dir = os.path.join(script_dir, output_dir)
        
        # Tạo thư mục output nếu chưa có
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def get_customer_data(self, customer_id):
        """Lấy dữ liệu khách hàng từ database"""
        customer = Customer.query.get(customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found")
        
        return customer.to_dict()
    
    def get_contract_data(self, contract_id):
        """Lấy dữ liệu hợp đồng từ database"""
        contract = Contract.query.get(contract_id)
        if not contract:
            raise ValueError(f"Contract with ID {contract_id} not found")
        
        return contract.to_dict()
    
    def get_room_booking_data(self, booking_id):
        """Lấy dữ liệu đặt phòng từ database"""
        booking = RoomBooking.query.get(booking_id)
        if not booking:
            raise ValueError(f"Room booking with ID {booking_id} not found")
        
        return booking.to_dict()
    
    def format_field_value(self, value, field_type="text"):
        """Format giá trị trường theo yêu cầu"""
        if value is None or value == "":
            return "________"  # Dấu gạch dưới cho trường trống
        
        if field_type == "currency":
            # Format tiền tệ
            return f"{value:,.0f} VND"
        elif field_type == "date":
            # Format ngày tháng
            if isinstance(value, str):
                return value
            elif hasattr(value, 'strftime'):
                return value.strftime("%d/%m/%Y")
            else:
                return str(value)
        else:
            # Format text thường
            return str(value)
    
    def prepare_contract_data(self, customer_data, contract_data=None, booking_data=None):
        """Chuẩn bị dữ liệu cho template hợp đồng với format đúng"""
        context = {
            # Thông tin khách hàng - Format với highlight và dấu cách
            "customer_name": self.format_field_value(customer_data.get("customer_name", "")),
            "company_name": self.format_field_value(customer_data.get("company_name", "")),
            "address": self.format_field_value(customer_data.get("address", "")),
            "tax_id": self.format_field_value(customer_data.get("tax_id", "")),
            "representative": self.format_field_value(customer_data.get("representative", "")),
            "mobile": self.format_field_value(customer_data.get("mobile", "")),
            "position": self.format_field_value(customer_data.get("position", "")),
            "bank_account": self.format_field_value(customer_data.get("bank_account", "")),
            "account_number": self.format_field_value(customer_data.get("account_number", "")),
            "bank_name": self.format_field_value(customer_data.get("bank_name", "")),
            "bank_branch": self.format_field_value(customer_data.get("bank_branch", "")),
            "birth_date": self.format_field_value(customer_data.get("birth_date", ""), "date"),
            "id_card": self.format_field_value(customer_data.get("id_card", "")),
            "email": self.format_field_value(customer_data.get("email", "")),
            
            # Thông tin hợp đồng - Format tiền tệ
            "contract_value": self.format_field_value(contract_data.get("contract_value", 0), "currency") if contract_data else "0 VND",
            "deposit_amount": self.format_field_value(contract_data.get("deposit_amount", 0), "currency") if contract_data else "0 VND",
            "from_date": self.format_field_value(contract_data.get("contract_start_date", ""), "date") if contract_data else "",
            "to_date": self.format_field_value(contract_data.get("contract_end_date", ""), "date") if contract_data else "",
            
            # Thông tin đặt phòng
            "room_number": self.format_field_value(booking_data.get("room", {}).get("room_number", "")) if booking_data else "",
            "monthly_rent": self.format_field_value(booking_data.get("monthly_rent", 0), "currency") if booking_data else "0 VND",
            
            # Thông tin ngày tháng
            "current_date": datetime.now().strftime("%d/%m/%Y"),
            "current_year": datetime.now().year,
            
            # Các trường với số thứ tự (để sử dụng trong template)
            "field_1": self.format_field_value(customer_data.get("customer_name", "")),
            "field_2": self.format_field_value(customer_data.get("address", "")),
            "field_3": self.format_field_value(customer_data.get("tax_id", "")),
            "field_4": self.format_field_value(customer_data.get("representative", "")),
            "field_5": self.format_field_value(customer_data.get("mobile", "")),
            "field_6": self.format_field_value(customer_data.get("bank_account", "")),
            "field_7": self.format_field_value(customer_data.get("account_number", "")),
            "field_8": self.format_field_value(customer_data.get("bank_name", "")),
            "field_9": self.format_field_value(customer_data.get("bank_branch", "")),
            "field_10": self.format_field_value(customer_data.get("position", "")),
            "field_11": self.format_field_value(contract_data.get("contract_value", 0), "currency") if contract_data else "0 VND",
            "field_12": self.format_field_value(contract_data.get("deposit_amount", 0), "currency") if contract_data else "0 VND",
            "field_13": self.format_field_value(contract_data.get("contract_start_date", ""), "date") if contract_data else "",
            "field_14": self.format_field_value(customer_data.get("birth_date", ""), "date"),
            "field_15": self.format_field_value(customer_data.get("id_card", "")),
            "field_16": self.format_field_value(contract_data.get("contract_end_date", ""), "date") if contract_data else ""
        }
        
        return context
    
    def generate_contract(self, contract_type, customer_id, contract_id=None, booking_id=None, output_filename=None):
        """Tạo hợp đồng từ template"""
        try:
            # Kiểm tra loại hợp đồng
            if contract_type not in self.CONTRACT_TEMPLATES:
                raise ValueError(f"Unsupported contract type: {contract_type}")
            
            template_config = self.CONTRACT_TEMPLATES[contract_type]
            
            # Kiểm tra nếu template không được hỗ trợ
            if template_config.get("supported") is False:
                raise ValueError(f"Template không được hỗ trợ: {template_config.get('note', '')}")
                
            template_path = os.path.join(self.template_dir, template_config["template_path"])
            
            # Kiểm tra file template
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template file not found: {template_path}")
            
            # Lấy dữ liệu
            customer_data = self.get_customer_data(customer_id)
            contract_data = self.get_contract_data(contract_id) if contract_id else None
            booking_data = self.get_room_booking_data(booking_id) if booking_id else None
            
            # Chuẩn bị context cho template - sử dụng method phù hợp với loại contract
            if contract_type == "payment_request":
                context = self.prepare_payment_request_data(customer_data, contract_data)
            else:
                context = self.prepare_contract_data(customer_data, contract_data, booking_data)
            
            # Tạo hợp đồng từ template
            doc = DocxTemplate(template_path)
            doc.render(context)
            
            # Tạo tên file output
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                customer_name = customer_data.get("customer_name", "unknown").replace(" ", "_")
                output_filename = f"{contract_type}_{customer_name}_{timestamp}.docx"
            
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Lưu file
            doc.save(output_path)
            
            return {
                "success": True,
                "output_path": output_path,
                "filename": output_filename,
                "contract_type": contract_type,
                "customer_name": customer_data.get("customer_name")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "contract_type": contract_type
            }
    
    def generate_multiple_contracts(self, contracts_data):
        """Tạo nhiều hợp đồng cùng lúc"""
        results = []
        
        for contract_data in contracts_data:
            result = self.generate_contract(
                contract_type=contract_data["contract_type"],
                customer_id=contract_data["customer_id"],
                contract_id=contract_data.get("contract_id"),
                booking_id=contract_data.get("booking_id"),
                output_filename=contract_data.get("output_filename")
            )
            results.append(result)
        
        return results
    
    def list_available_templates(self):
        """Liệt kê các template có sẵn"""
        return list(self.CONTRACT_TEMPLATES.keys())
    
    def validate_template_exists(self, contract_type):
        """Kiểm tra template có tồn tại không"""
        if contract_type not in self.CONTRACT_TEMPLATES:
            return False
        
        template_path = os.path.join(self.template_dir, self.CONTRACT_TEMPLATES[contract_type]["template_path"])
        return os.path.exists(template_path)
    
    def get_template_format_guide(self):
        """Hướng dẫn format template"""
        return {
            "description": "Template phải sử dụng format với highlight, dấu cách và số thứ tự",
            "examples": {
                "field_1": "BÊN THUÊ: {{ customer_name }}",
                "field_2": "ĐỊA CHỈ: {{ address }}", 
                "field_3": "MST: {{ tax_id }}",
                "field_4": "ĐẠI DIỆN BỞI: {{ representative }}",
                "field_5": "SỐ ĐIỆN THOẠI: {{ mobile }}"
            },
            "formatting_rules": [
                "1. Highlight: Sử dụng định dạng làm nổi bật trong Word",
                "2. Dấu cách: Có khoảng trắng giữa label và giá trị",
                "3. Số thứ tự: Đánh dấu bằng số 1, 2, 3, 4, 5...",
                "4. Giá trị trống: Hiển thị dấu gạch dưới ________"
            ]
        } 

    def prepare_payment_request_data(self, customer_data, contract_data):
        """Chuẩn bị dữ liệu cho payment request - chỉ sử dụng 11 trường Jinja thực sự cần thiết"""
        contract_value = float(contract_data.get('contract_value', 0))
        
        # Tính toán các khoản tiền
        service_amount = contract_value * 12
        vat_amount = service_amount * 0.1
        deposit_amount = contract_value * 2
        total_amount = service_amount + vat_amount
        
        # Chuyển đổi số tiền thành chữ
        amount_in_words = self.number_to_words(total_amount)
        
        return {
            # Chỉ 11 trường Jinja thực sự được sử dụng trong template
            'customer_name': customer_data.get('customer_name'),
            'address': customer_data.get('company_name') or 'N/A',  # Sử dụng company_name thay cho address
            'service_name': 'Tiền thuê văn phòng dịch vụ',
            'service_unit': 'Tháng',
            'service_quantity': '12',
            'service_unit_price': f"{contract_value:,}",
            'service_amount': f"{service_amount:,}",
            'vat_amount': f"{vat_amount:,}",
            'deposit_amount': f"{deposit_amount:,}",
            'total_rental_amount': f"{total_amount:,}",
            'amount_in_words': amount_in_words
        }
    
    def number_to_words(self, number):
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
