from flask import Blueprint, request, jsonify
from src.models.customer import db, Customer, Contract, WebBooking, Alert
from datetime import datetime, date, timedelta
from sqlalchemy import or_

customer_bp = Blueprint('customer', __name__)

# Test endpoint
@customer_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to check if backend is working"""
    return jsonify({
        'message': 'Backend is working!',
        'timestamp': datetime.utcnow().isoformat()
    })

# Customer CRUD operations
@customer_bp.route('/customers', methods=['GET'])
def get_customers():
    """Get all customers with optional filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)  # Limit max 100
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        
        query = Customer.query
        
        # Apply search filter with optimized OR conditions
        if search:
            search_term = f"%{search}%"
            query = query.filter(or_(
                Customer.customer_name.ilike(search_term),
                Customer.company_name.ilike(search_term),
                Customer.email.ilike(search_term),
                Customer.mobile.ilike(search_term)
            ))
        
        # Apply status filter through contracts - optimized
        if status:
            # Use subquery for better performance
            customer_ids_subquery = db.session.query(Contract.customer_id).filter(
                Contract.status == status
            ).distinct().subquery()
            query = query.filter(Customer.customer_id.in_(
                db.session.query(customer_ids_subquery.c.customer_id)
            ))
        
        # Add consistent ordering
        query = query.order_by(Customer.customer_name)
        
        customers = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Optimize serialization - don't include all contracts by default
        # Instead provide lightweight aggregates for UI columns
        customer_list = []
        for customer in customers.items:
            customer_dict = customer.to_dict()
            # Remove heavy contracts array
            customer_dict.pop('contracts', None)

            # Aggregate contract info
            cust_contracts = Contract.query.filter_by(customer_id=customer.customer_id).all()
            contract_count = len(cust_contracts)
            active_contracts_count = len([
                c for c in cust_contracts if c.status in ('Khách book', 'Khách đã thanh toán')
            ])

            customer_dict['contract_count'] = contract_count
            customer_dict['active_contracts_count'] = active_contracts_count
            if contract_count == 0:
                customer_dict['status_summary'] = 'No Contracts'
            elif active_contracts_count > 0:
                customer_dict['status_summary'] = 'Active'
            else:
                customer_dict['status_summary'] = 'Inactive'

            customer_list.append(customer_dict)
        
        return jsonify({
            'customers': customer_list,
            'total': customers.total,
            'pages': customers.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': customers.has_next,
            'has_prev': customers.has_prev
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get a specific customer by ID"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        return jsonify(customer.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers', methods=['POST'])
def create_customer():
    """Create a new customer"""
    try:
        data = request.get_json()
        
        customer = Customer(
            customer_name=data.get('customer_name'),
            company_name=data.get('company_name'),
            tax_id=data.get('tax_id'),
            nationality=data.get('nationality'),
            business_type=data.get('business_type'),
            enterprise_type=data.get('enterprise_type'),
            id_card=data.get('id_card'),
            email=data.get('email'),
            mobile=data.get('mobile'),
            zalo=data.get('zalo'),
            whatsapp=data.get('whatsapp'),
            kakao=data.get('kakao'),
            notes=data.get('notes')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify(customer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update an existing customer"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        customer.customer_name = data.get('customer_name', customer.customer_name)
        customer.company_name = data.get('company_name', customer.company_name)
        customer.tax_id = data.get('tax_id', customer.tax_id)
        customer.nationality = data.get('nationality', customer.nationality)
        customer.business_type = data.get('business_type', customer.business_type)
        customer.enterprise_type = data.get('enterprise_type', customer.enterprise_type)
        customer.id_card = data.get('id_card', customer.id_card)
        customer.email = data.get('email', customer.email)
        customer.mobile = data.get('mobile', customer.mobile)
        customer.zalo = data.get('zalo', customer.zalo)
        customer.whatsapp = data.get('whatsapp', customer.whatsapp)
        customer.kakao = data.get('kakao', customer.kakao)
        customer.notes = data.get('notes', customer.notes)
        customer.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(customer.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete a customer"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({'message': 'Customer deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Contract CRUD operations
@customer_bp.route('/contracts', methods=['GET'])
def get_contracts():
    """Get all contracts with optional filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        customer_id = request.args.get('customer_id', type=int)
        status = request.args.get('status', '')
        
        query = Contract.query
        
        if customer_id:
            query = query.filter(Contract.customer_id == customer_id)
        
        if status:
            query = query.filter(Contract.status == status)
        
        contracts = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        contracts_list = []
        for contract in contracts.items:
            item = contract.to_dict()
            try:
                cust = Customer.query.get(contract.customer_id)
                if cust:
                    item['customer'] = {
                        'customer_id': cust.customer_id,
                        'customer_name': cust.customer_name,
                        'company_name': cust.company_name
                    }
            except Exception:
                pass
            contracts_list.append(item)

        return jsonify({
            'contracts': contracts_list,
            'total': contracts.total,
            'pages': contracts.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/contracts/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    """Get a specific contract by ID"""
    try:
        contract = Contract.query.get_or_404(contract_id)
        return jsonify(contract.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/contracts', methods=['POST'])
def create_contract():
    """Create a new contract"""
    try:
        data = request.get_json()
        
        contract = Contract(
            customer_id=data.get('customer_id'),
            contract_type=data.get('contract_type'),
            contract_value=data.get('contract_value'),
            contract_start_date=datetime.strptime(data.get('contract_start_date'), '%Y-%m-%d').date(),
            contract_end_date=datetime.strptime(data.get('contract_end_date'), '%Y-%m-%d').date(),
            amount_paid=data.get('amount_paid', 0),
            last_payment_date=datetime.strptime(data.get('last_payment_date'), '%Y-%m-%d').date() if data.get('last_payment_date') else None,
            status=data.get('status', 'Khách hỏi'),
            additional_services=data.get('additional_services')
        )
        
        db.session.add(contract)
        db.session.commit()
        
        # Generate alerts for this contract
        generate_payment_alerts(contract)
        
        return jsonify(contract.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/contracts/<int:contract_id>', methods=['PUT'])
def update_contract(contract_id):
    """Update an existing contract"""
    try:
        contract = Contract.query.get_or_404(contract_id)
        data = request.get_json()
        
        contract.contract_type = data.get('contract_type', contract.contract_type)
        contract.contract_value = data.get('contract_value', contract.contract_value)
        contract.contract_start_date = datetime.strptime(data.get('contract_start_date'), '%Y-%m-%d').date() if data.get('contract_start_date') else contract.contract_start_date
        contract.contract_end_date = datetime.strptime(data.get('contract_end_date'), '%Y-%m-%d').date() if data.get('contract_end_date') else contract.contract_end_date
        contract.amount_paid = data.get('amount_paid', contract.amount_paid)
        contract.last_payment_date = datetime.strptime(data.get('last_payment_date'), '%Y-%m-%d').date() if data.get('last_payment_date') else contract.last_payment_date
        contract.status = data.get('status', contract.status)
        contract.additional_services = data.get('additional_services', contract.additional_services)
        contract.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Regenerate alerts for this contract
        Alert.query.filter_by(contract_id=contract_id).delete()
        generate_payment_alerts(contract)
        
        return jsonify(contract.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/contracts/<int:contract_id>', methods=['DELETE'])
def delete_contract(contract_id):
    """Delete a contract"""
    try:
        contract = Contract.query.get_or_404(contract_id)
        db.session.delete(contract)
        db.session.commit()
        
        return jsonify({'message': 'Contract deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Alert management
@customer_bp.route('/alerts/upcoming', methods=['GET'])
def get_upcoming_alerts():
    """Get upcoming payment alerts"""
    try:
        today = date.today()
        alerts = Alert.query.filter(
            Alert.alert_date >= today,
            Alert.is_sent == False
        ).order_by(Alert.alert_date).all()
        
        enriched = []
        for alert in alerts:
            item = alert.to_dict()
            # Bổ sung thông tin customer tối thiểu cho contract
            try:
                contract = Contract.query.get(alert.contract_id)
                if contract:
                    cust = Customer.query.get(contract.customer_id)
                    contract_dict = contract.to_dict()
                    if cust:
                        contract_dict['customer'] = {
                            'customer_id': cust.customer_id,
                            'customer_name': cust.customer_name,
                            'company_name': cust.company_name,
                            'email': cust.email
                        }
                    item['contract'] = contract_dict
            except Exception:
                pass
            enriched.append(item)

        return jsonify(enriched)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/alerts/<int:alert_id>/mark_sent', methods=['POST'])
def mark_alert_sent(alert_id):
    """Mark an alert as sent"""
    try:
        alert = Alert.query.get_or_404(alert_id)
        alert.is_sent = True
        db.session.commit()
        
        return jsonify({'message': 'Alert marked as sent'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Web booking
@customer_bp.route('/web-bookings', methods=['POST'])
def create_web_booking():
    """Create a web booking and automatically set customer status to 'Khách hỏi'"""
    try:
        data = request.get_json()
        
        # Create or find customer
        customer_data = data.get('customer')
        customer = Customer.query.filter_by(email=customer_data.get('email')).first()
        
        if not customer:
            customer = Customer(
                customer_name=customer_data.get('customer_name'),
                company_name=customer_data.get('company_name'),
                email=customer_data.get('email'),
                mobile=customer_data.get('mobile'),
                notes='Created from web booking'
            )
            db.session.add(customer)
            db.session.flush()  # Get the customer_id
        
        # Create web booking
        web_booking = WebBooking(
            customer_id=customer.customer_id,
            details=data.get('details')
        )
        
        db.session.add(web_booking)
        db.session.commit()
        
        return jsonify({
            'message': 'Web booking created successfully',
            'customer': customer.to_dict(),
            'web_booking': web_booking.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Dashboard statistics
@customer_bp.route('/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_customers = Customer.query.count()
        total_contracts = Contract.query.count()
        active_contracts = Contract.query.filter(Contract.status.in_(['Khách book', 'Khách đã thanh toán'])).count()
        
        # Calculate total revenue and outstanding amounts
        contracts = Contract.query.all()
        total_revenue = sum(float(contract.amount_paid) for contract in contracts)
        total_outstanding = sum(contract.calculate_amount_due() for contract in contracts)
        
        # Get upcoming alerts count
        today = date.today()
        upcoming_alerts = Alert.query.filter(
            Alert.alert_date >= today,
            Alert.is_sent == False
        ).count()
        
        return jsonify({
            'total_customers': total_customers,
            'total_contracts': total_contracts,
            'active_contracts': active_contracts,
            'total_revenue': total_revenue,
            'total_outstanding': total_outstanding,
            'upcoming_alerts': upcoming_alerts
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_payment_alerts(contract):
    """Generate payment alerts for a contract"""
    try:
        # Use contract end date as the payment due date
        due_date = contract.contract_end_date
        
        # Generate alerts for different time periods
        alert_periods = [
            ('2_weeks_before', 14),
            ('1_week_before', 7),
            ('3_days_before', 3),
            ('due_date', 0)
        ]
        
        for alert_type, days_before in alert_periods:
            alert_date = due_date - timedelta(days=days_before)
            
            # Only create alerts for future dates
            if alert_date >= date.today():
                alert = Alert(
                    contract_id=contract.contract_id,
                    alert_date=alert_date,
                    alert_type=alert_type
                )
                db.session.add(alert)
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error generating alerts: {e}")

