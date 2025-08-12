from flask import Blueprint, request, jsonify, send_file
from src.models.customer import Customer, Contract
from src.models.room import RoomBooking
from src.contract_generator import ContractGenerator
import os

contract_bp = Blueprint('contracts', __name__)

# Khởi tạo contract generator
contract_generator = ContractGenerator()

@contract_bp.route('/contracts/generate', methods=['POST'])
def generate_contract():
    """Tạo hợp đồng từ template"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['contract_type', 'customer_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        contract_type = data['contract_type']
        customer_id = data['customer_id']
        contract_id = data.get('contract_id')
        booking_id = data.get('booking_id')
        output_filename = data.get('output_filename')
        
        # Kiểm tra template có tồn tại không
        if not contract_generator.validate_template_exists(contract_type):
            return jsonify({
                'error': f'Template not found for contract type: {contract_type}',
                'available_templates': contract_generator.list_available_templates()
            }), 404
        
        # Tạo hợp đồng
        result = contract_generator.generate_contract(
            contract_type=contract_type,
            customer_id=customer_id,
            contract_id=contract_id,
            booking_id=booking_id,
            output_filename=output_filename
        )
        
        if result['success']:
            return jsonify({
                'message': 'Contract generated successfully',
                'data': result
            }), 200
        else:
            return jsonify({
                'error': 'Failed to generate contract',
                'details': result['error']
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/contracts/generate-multiple', methods=['POST'])
def generate_multiple_contracts():
    """Tạo nhiều hợp đồng cùng lúc"""
    try:
        data = request.get_json()
        
        if 'contracts' not in data or not isinstance(data['contracts'], list):
            return jsonify({'error': 'Missing or invalid contracts array'}), 400
        
        contracts_data = data['contracts']
        
        # Validate each contract data
        for i, contract_data in enumerate(contracts_data):
            if 'contract_type' not in contract_data or 'customer_id' not in contract_data:
                return jsonify({
                    'error': f'Missing required fields in contract {i+1}'
                }), 400
        
        # Tạo nhiều hợp đồng
        results = contract_generator.generate_multiple_contracts(contracts_data)
        
        success_count = sum(1 for result in results if result['success'])
        failed_count = len(results) - success_count
        
        return jsonify({
            'message': f'Generated {success_count} contracts successfully, {failed_count} failed',
            'results': results,
            'summary': {
                'total': len(results),
                'success': success_count,
                'failed': failed_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/contracts/templates', methods=['GET'])
def get_available_templates():
    """Lấy danh sách template có sẵn"""
    try:
        templates = contract_generator.list_available_templates()
        
        # Kiểm tra template nào có sẵn file
        available_templates = []
        for template in templates:
            if contract_generator.validate_template_exists(template):
                available_templates.append({
                    'name': template,
                    'available': True,
                    'template_path': contract_generator.CONTRACT_TEMPLATES[template]['template_path']
                })
            else:
                available_templates.append({
                    'name': template,
                    'available': False,
                    'template_path': contract_generator.CONTRACT_TEMPLATES[template]['template_path']
                })
        
        return jsonify({
            'templates': available_templates,
            'total': len(templates)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/contracts/download/<filename>', methods=['GET'])
def download_contract(filename):
    """Download file hợp đồng đã tạo"""
    try:
        file_path = os.path.join(contract_generator.output_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/contracts/list', methods=['GET'])
def list_generated_contracts():
    """Liệt kê các hợp đồng đã tạo"""
    try:
        output_dir = contract_generator.output_dir
        
        if not os.path.exists(output_dir):
            return jsonify({'contracts': [], 'total': 0})
        
        files = []
        for filename in os.listdir(output_dir):
            if filename.endswith('.docx'):
                file_path = os.path.join(output_dir, filename)
                file_stat = os.stat(file_path)
                
                files.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'created_at': file_stat.st_ctime,
                    'modified_at': file_stat.st_mtime
                })
        
        # Sắp xếp theo thời gian tạo mới nhất
        files.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'contracts': files,
            'total': len(files)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/contracts/delete/<filename>', methods=['DELETE'])
def delete_contract(filename):
    """Xóa file hợp đồng đã tạo"""
    try:
        file_path = os.path.join(contract_generator.output_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        os.remove(file_path)
        
        return jsonify({
            'message': f'Contract file {filename} deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_bp.route('/contracts/preview-data/<int:customer_id>', methods=['GET'])
def preview_contract_data(customer_id):
    """Xem trước dữ liệu sẽ được điền vào hợp đồng"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Lấy dữ liệu khách hàng
        customer_data = customer.to_dict()
        
        # Lấy hợp đồng gần nhất của khách hàng
        latest_contract = Contract.query.filter_by(customer_id=customer_id)\
            .order_by(Contract.created_at.desc()).first()
        
        contract_data = latest_contract.to_dict() if latest_contract else None
        
        # Lấy booking gần nhất của khách hàng
        latest_booking = RoomBooking.query.filter_by(customer_id=customer_id)\
            .order_by(RoomBooking.created_at.desc()).first()
        
        booking_data = latest_booking.to_dict() if latest_booking else None
        
        # Chuẩn bị dữ liệu preview
        preview_data = contract_generator.prepare_contract_data(
            customer_data, contract_data, booking_data
        )
        
        return jsonify({
            'customer_data': customer_data,
            'contract_data': contract_data,
            'booking_data': booking_data,
            'preview_data': preview_data,
            'field_mapping': contract_generator.FIELD_MAPPING
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 