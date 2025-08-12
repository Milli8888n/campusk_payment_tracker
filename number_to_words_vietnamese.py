#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def number_to_words_vietnamese(number):
    """Chuyển đổi số thành chữ tiếng Việt"""
    
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
        
        # Xử lý phần nguyên
        integer_part = int(n)
        decimal_part = int((n - integer_part) * 100) if n != integer_part else 0
        
        if integer_part == 0:
            result = "không"
        else:
            # Chia thành các nhóm 3 chữ số
            groups = []
            temp = integer_part
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
            
            result = " ".join(words)
        
        # Thêm phần thập phân nếu có
        if decimal_part > 0:
            result += " phẩy " + convert_less_than_one_thousand(decimal_part)
        
        return result
    
    # Chuyển đổi số
    words = convert_number(number)
    
    # Thêm "đồng" vào cuối
    return words + " đồng"

def number_to_words_simple(number):
    """Hàm đơn giản hơn để chuyển đổi số thành chữ"""
    
    # Làm tròn số
    rounded_number = round(number)
    
    # Chuyển đổi cơ bản
    if rounded_number == 0:
        return "không đồng"
    elif rounded_number == 1:
        return "một đồng"
    elif rounded_number < 1000:
        return f"{rounded_number:,} đồng"
    elif rounded_number < 1000000:
        millions = rounded_number // 1000000
        thousands = (rounded_number % 1000000) // 1000
        remainder = rounded_number % 1000
        
        result = ""
        if millions > 0:
            result += f"{millions} triệu "
        if thousands > 0:
            result += f"{thousands} nghìn "
        if remainder > 0:
            result += f"{remainder} "
        result += "đồng"
        return result
    else:
        # Cho số lớn, sử dụng format đơn giản
        return f"{rounded_number:,} đồng"

def test_number_to_words():
    """Test hàm chuyển đổi số thành chữ"""
    
    test_numbers = [
        0,
        1,
        10,
        15,
        20,
        25,
        100,
        150,
        1000,
        1500,
        10000,
        15000,
        100000,
        150000,
        1000000,
        1500000,
        10000000,
        15000000,
        100000000,
        150000000,
        1000000000,
        1500000000,
        431161473.60,
        216324094.80,
        416314932.00
    ]
    
    print("🧪 Test chuyển đổi số thành chữ tiếng Việt:")
    print("=" * 60)
    
    for number in test_numbers:
        words = number_to_words_simple(number)
        print(f"{number:15,.0f} -> {words}")

def main():
    """Main function"""
    print("🚀 Hàm chuyển đổi số thành chữ tiếng Việt")
    print("=" * 60)
    
    # Test hàm
    test_number_to_words()
    
    print("\n✅ Hoàn thành test!")
    print("📋 Hàm có thể được sử dụng trong Payment Request")

if __name__ == "__main__":
    main() 