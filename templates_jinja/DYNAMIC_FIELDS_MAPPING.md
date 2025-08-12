# DYNAMIC FIELDS MAPPING

## Các trường động đã được thay thế:

### Thông tin thời gian:
| Template Field | Jinja Variable | Mô tả |
|----------------|----------------|-------|
| xx/xx/2026 | {{ issue_date }} | Ngày xuất yêu cầu thanh toán |
| xx/xx/2026 | {{ due_date }} | Hạn thanh toán |

### Bảng chi tiết thanh toán - Dịch vụ chính:
| Template Field | Jinja Variable | Mô tả |
|----------------|----------------|-------|
| x | {{ service_quantity }} | Số lượng dịch vụ (VD: 12 tháng) |
| y | {{ service_unit_price }} | Đơn giá dịch vụ (VD: 5,000,000 VND/tháng) |
| X x Y | {{ service_amount }} | Thành tiền dịch vụ (tính toán: quantity × unit_price) |

### Bảng chi tiết thanh toán - Thuế VAT:
| Template Field | Jinja Variable | Mô tả |
|----------------|----------------|-------|
| (X x Y)/10% | {{ vat_amount }} | Thuế VAT (tính toán: service_amount × 0.1) |

### Bảng chi tiết thanh toán - Đặt cọc:
| Template Field | Jinja Variable | Mô tả |
|----------------|----------------|-------|
| x | {{ deposit_quantity }} | Số tháng đặt cọc (VD: 2 tháng) |
| y | {{ deposit_unit_price }} | Đơn giá đặt cọc (VD: 5,000,000 VND/tháng) |
| X x Y | {{ deposit_amount }} | Thành tiền đặt cọc (tính toán: quantity × unit_price) |

### Phần tổng kết:
| Template Field | Jinja Variable | Mô tả |
|----------------|----------------|-------|
| (X x Y) + (X x Y)/10% - deposit | {{ total_rental_amount }} | Tổng tiền thuê (tính toán: service_amount + vat_amount - deposit_amount) |
| {{ }} | {{ amount_in_words }} | Số tiền viết bằng chữ |

## Cách tính toán trong ContractGenerator:

```python
def prepare_payment_request_data(self, customer_data, contract_data):
    contract_value = float(contract_data.get('contract_value', 0))
    
    # Tính toán các giá trị
    service_quantity = 12
    service_unit_price = contract_value
    service_amount = contract_value * 12
    
    deposit_quantity = 2
    deposit_unit_price = contract_value
    deposit_amount = contract_value * 2
    
    vat_amount = service_amount * 0.1
    total_rental_amount = service_amount + vat_amount - deposit_amount
    
    return {
        # Thông tin thời gian
        'issue_date': '15/12/2026',
        'due_date': '15/12/2026',
        
        # Bảng chi tiết - Dịch vụ chính
        'service_quantity': str(service_quantity),
        'service_unit_price': f"{service_unit_price:,}",
        'service_amount': f"{service_amount:,}",
        
        # Bảng chi tiết - Thuế VAT
        'vat_amount': f"{vat_amount:,}",
        
        # Bảng chi tiết - Đặt cọc
        'deposit_quantity': str(deposit_quantity),
        'deposit_unit_price': f"{deposit_unit_price:,}",
        'deposit_amount': f"{deposit_amount:,}",
        
        # Phần tổng kết
        'total_rental_amount': f"{total_rental_amount:,}",
        'amount_in_words': self.number_to_words(total_rental_amount),
        
        # Thông tin khách hàng
        'customer_name': customer_data.get('customer_name'),
        'address': customer_data.get('address'),
        # ... các trường khác
    }
```

## Lưu ý:
- Các trường X, Y là dữ liệu động từ database
- Hệ thống sẽ tự động tính toán các giá trị phụ thuộc
- Người dùng chỉ cần nhập contract_value, hệ thống tính toán tất cả
