# PAYMENT REQUEST JINJA MAPPING

## Các trường thông tin cho Payment Request:

### Thông tin khách hàng:
| Trường | Jinja Variable | Mô tả |
|--------|----------------|-------|
| Tên khách hàng | {{ customer_name }} | Tên công ty/khách hàng |
| Địa chỉ | {{ address }} | Địa chỉ khách hàng |
| Mã số thuế | {{ tax_id }} | MST của khách hàng |
| Người đại diện | {{ representative }} | Người đại diện |
| Chức vụ | {{ position }} | Chức vụ người đại diện |
| Số điện thoại | {{ mobile }} | Số điện thoại liên hệ |

### Thông tin dịch vụ chính:
| Trường | Jinja Variable | Mô tả |
|--------|----------------|-------|
| Tên dịch vụ | {{ service_name }} | "Tiền thuê văn phòng dịch vụ" |
| Đơn vị tính | {{ service_unit }} | "Tháng" |
| Số lượng | {{ service_quantity }} | "12" |
| Đơn giá | {{ service_unit_price }} | Giá thuê hàng tháng |
| Thành tiền | {{ service_amount }} | Tổng tiền thuê = SL × Đơn giá |

### Thông tin đặt cọc:
| Trường | Jinja Variable | Mô tả |
|--------|----------------|-------|
| Tên dịch vụ | {{ deposit_service_name }} | "Tiền đặt cọc Deposit" |
| Đơn vị tính | {{ deposit_unit }} | "Tháng Month" |
| Số lượng | {{ deposit_quantity }} | Số tháng đặt cọc |
| Đơn giá | {{ deposit_unit_price }} | Đơn giá đặt cọc |
| Thành tiền | {{ deposit_amount }} | Tổng tiền đặt cọc |

### Thông tin tổng hợp:
| Trường | Jinja Variable | Mô tả |
|--------|----------------|-------|
| Tổng tiền thuê | {{ total_rental_amount }} | Tổng tiền thuê trước thuế |
| Thuế VAT | {{ vat_amount }} | Số tiền thuế VAT 10% |
| Tổng cộng | {{ total_amount }} | Tổng tiền sau thuế |
| Số tiền bằng chữ | {{ amount_in_words }} | Số tiền viết bằng chữ |

### Thông tin thời gian:
| Trường | Jinja Variable | Mô tả |
|--------|----------------|-------|
| Ngày hạn thanh toán | {{ payment_due_date }} | Ngày hạn thanh toán |
| Thời hạn hợp đồng | {{ contract_period }} | Thời hạn hợp đồng |
| Từ ngày | {{ from_date }} | Ngày bắt đầu |
| Đến ngày | {{ to_date }} | Ngày kết thúc |

## Cách sử dụng trong ContractGenerator:

```python
def prepare_payment_request_data(self, customer_data, contract_data):
    return {
        # Thông tin khách hàng
        'customer_name': customer_data.get('customer_name'),
        'address': customer_data.get('address'),
        'tax_id': customer_data.get('tax_id'),
        'representative': customer_data.get('representative'),
        'position': customer_data.get('position'),
        'mobile': customer_data.get('mobile'),
        
        # Thông tin dịch vụ
        'service_name': 'Tiền thuê văn phòng dịch vụ',
        'service_unit': 'Tháng',
        'service_quantity': '12',
        'service_unit_price': f"{contract_data.get('contract_value', 0):,}",
        'service_amount': f"{contract_data.get('contract_value', 0) * 12:,}",
        
        # Thông tin đặt cọc
        'deposit_service_name': 'Tiền đặt cọc Deposit',
        'deposit_unit': 'Tháng Month',
        'deposit_quantity': '2',
        'deposit_unit_price': f"{contract_data.get('contract_value', 0):,}",
        'deposit_amount': f"{contract_data.get('contract_value', 0) * 2:,}",
        
        # Thông tin tổng hợp
        'total_rental_amount': f"{contract_data.get('contract_value', 0) * 14:,}",
        'vat_amount': f"{contract_data.get('contract_value', 0) * 14 * 0.1:,}",
        'total_amount': f"{contract_data.get('contract_value', 0) * 14 * 1.1:,}",
        'amount_in_words': self.number_to_words(contract_data.get('contract_value', 0) * 14 * 1.1),
        
        # Thông tin thời gian
        'payment_due_date': '15/12/2026',
        'contract_period': '12 tháng',
        'from_date': contract_data.get('contract_start_date'),
        'to_date': contract_data.get('contract_end_date')
    }
```

## Lưu ý:
- Các trường này sẽ được điền tự động từ database
- Đảm bảo dữ liệu trong database khớp với tên trường
- Có thể cần thêm logic tính toán cho các trường tổng hợp
