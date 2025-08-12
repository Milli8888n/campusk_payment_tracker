# MAPPING TRƯỜNG THÔNG TIN VỚI CÚ PHÁP JINJA

## Các trường thông tin đã được chuyển đổi:

| Số thứ tự | Tên trường | Cú pháp Jinja | Mô tả |
|-----------|------------|----------------|-------|
| 1 | customer_name | {{ customer_name }} | BÊN THUÊ / THE LESSEE |
| 2 | address | {{ address }} | ĐỊA CHỈ / ADDRESS |
| 3 | tax_id | {{ tax_id }} | MST / TAX CODE |
| 4 | representative | {{ representative }} | ĐẠI DIỆN BỞI / REPRESENTED BY |
| 5 | position | {{ position }} | CHỨC VỤ / POSITION |
| 6 | mobile | {{ mobile }} | SỐ ĐIỆN THOẠI / TEL |
| 7 | account_number | {{ account_number }} | STK / ACCOUNT NUMBER |
| 8 | bank_name | {{ bank_name }} | NGÂN HÀNG / BANK NAME |
| 9 | bank_branch | {{ bank_branch }} | CHI NHÁNH / BRANCH |
| 10 | position | {{ position }} | CHỨC VỤ / POSITION |
| 11 | contract_value | {{ contract_value }} | TỔNG GIÁ TRỊ HỢP ĐỒNG / CONTRACT VALUE |
| 12 | deposit_amount | {{ deposit_amount }} | SỐ TIỀN ĐẶT CỌC / DEPOSIT AMOUNT |
| 13 | from_date | {{ from_date }} | TỪ (FROM) / FROM |
| 14 | birth_date | {{ birth_date }} | NGÀY SINH / BIRTH DATE |
| 15 | id_card | {{ id_card }} | SỐ CMND/HỘ CHIẾU / ID CARD |
| 16 | to_date | {{ to_date }} | THÀNH (TO) / TO |

## Cách sử dụng:

1. Các template đã được chuyển đổi nằm trong thư mục `templates_jinja/`
2. Sử dụng các template này với ContractGenerator để truyền dữ liệu từ database
3. Đảm bảo dữ liệu trong database khớp với tên trường trong mapping

## Ví dụ sử dụng:

```python
from src.contract_generator import ContractGenerator

generator = ContractGenerator()
result = generator.generate_contract(
    contract_type="virtual_office",
    customer_id=1,
    contract_id=2
)
```

## Lưu ý:

- Các template gốc vẫn được giữ nguyên trong thư mục `templates/`
- Các template đã chuyển đổi được lưu trong thư mục `templates_jinja/`
- Đảm bảo cập nhật CONTRACT_TEMPLATES trong contract_generator.py để sử dụng template Jinja
