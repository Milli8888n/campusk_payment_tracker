from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.room import Branch, Room, RoomBooking, RoomAlert, WebRoomBooking
from src.models.customer import Customer
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_

room_bp = Blueprint('room', __name__)

# Branch routes
@room_bp.route('/branches', methods=['GET'])
def get_branches():
    try:
        branches = Branch.query.all()
        enriched = []
        for b in branches:
            item = b.to_dict()
            total_rooms = Room.query.filter_by(branch_id=b.branch_id).count()
            available_rooms = Room.query.filter_by(branch_id=b.branch_id, is_available=True).count()
            item['total_rooms'] = total_rooms
            item['available_rooms'] = available_rooms
            item['status'] = 'Hoạt động' if total_rooms > 0 else 'Tạm đóng'
            enriched.append(item)
        return jsonify({
            'branches': enriched,
            'total': len(enriched)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@room_bp.route('/branches', methods=['POST'])
def create_branch():
    try:
        data = request.get_json()
        
        branch = Branch(
            branch_name=data['branch_name'],
            total_rooms=data.get('total_rooms', 0),
            address=data.get('address'),
            description=data.get('description')
        )
        
        db.session.add(branch)
        db.session.commit()
        
        return jsonify(branch.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@room_bp.route('/branches/<int:branch_id>', methods=['GET'])
def get_branch(branch_id):
    try:
        branch = Branch.query.get_or_404(branch_id)
        item = branch.to_dict()
        total_rooms = Room.query.filter_by(branch_id=branch_id).count()
        available_rooms = Room.query.filter_by(branch_id=branch_id, is_available=True).count()
        item['total_rooms'] = total_rooms
        item['available_rooms'] = available_rooms
        item['status'] = 'Hoạt động' if total_rooms > 0 else 'Tạm đóng'
        return jsonify(item)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@room_bp.route('/branches/<int:branch_id>', methods=['PUT'])
def update_branch(branch_id):
    try:
        branch = Branch.query.get_or_404(branch_id)
        data = request.get_json()
        
        branch.branch_name = data.get('branch_name', branch.branch_name)
        branch.total_rooms = data.get('total_rooms', branch.total_rooms)
        branch.address = data.get('address', branch.address)
        branch.description = data.get('description', branch.description)
        branch.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(branch.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@room_bp.route('/branches/<int:branch_id>', methods=['DELETE'])
def delete_branch(branch_id):
    try:
        branch = Branch.query.get_or_404(branch_id)
        db.session.delete(branch)
        db.session.commit()
        return jsonify({'message': 'Branch deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Room routes
@room_bp.route('/rooms', methods=['GET'])
def get_rooms():
    """Get all rooms with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)  # Limit max 100
        branch_id = request.args.get('branch_id', type=int)
        status = request.args.get('status', '')
        room_type = request.args.get('room_type', '')
        search = request.args.get('search', '')
        
        query = Room.query
        
        # Apply filters
        if branch_id:
            query = query.filter_by(branch_id=branch_id)
            
        if status:
            # support legacy and new statuses
            if status in ['available', 'occupied']:
                if status == 'available':
                    query = query.filter(Room.is_available == True)
                else:
                    query = query.filter(Room.is_available == False)
            else:
                query = query.filter(Room.status == status)
        
        if room_type:
            query = query.filter(Room.room_type == room_type)
        
        if search:
            query = query.filter(
                or_(
                    Room.room_number.contains(search),
                    Room.amenities.contains(search)
                )
            )
        
        # Add ordering for consistent results
        query = query.order_by(Room.room_number)
        
        rooms = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'rooms': [room.to_dict(include_bookings=True, include_branch=True) for room in rooms.items],
            'total': rooms.total,
            'pages': rooms.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': rooms.has_next,
            'has_prev': rooms.has_prev
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@room_bp.route('/rooms', methods=['POST'])
def create_room():
    try:
        data = request.get_json()
        
        room = Room(
            branch_id=data['branch_id'],
            room_number=data['room_number'],
            area=data.get('area'),
            orientation=data.get('orientation'),
            rental_price=data['rental_price'],
            capacity=data.get('capacity', 1),
            amenities=data.get('amenities'),
            notes=data.get('notes'),
            is_available=data.get('is_available', True)
        )
        
        db.session.add(room)
        db.session.commit()
        
        return jsonify(room.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@room_bp.route('/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        return jsonify(room.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@room_bp.route('/rooms/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        data = request.get_json()
        
        room.room_number = data.get('room_number', room.room_number)
        room.area = data.get('area', room.area)
        room.orientation = data.get('orientation', room.orientation)
        room.rental_price = data.get('rental_price', room.rental_price)
        room.capacity = data.get('capacity', room.capacity)
        room.amenities = data.get('amenities', room.amenities)
        room.notes = data.get('notes', room.notes)
        room.is_available = data.get('is_available', room.is_available)
        room.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(room.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@room_bp.route('/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        db.session.delete(room)
        db.session.commit()
        return jsonify({'message': 'Room deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Room Booking routes
@room_bp.route('/room-bookings', methods=['GET'])
def get_room_bookings():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        branch_id = request.args.get('branch_id', type=int)
        
        query = RoomBooking.query.join(Room)
        
        if status:
            query = query.filter(RoomBooking.status == status)
        
        if branch_id:
            query = query.filter(Room.branch_id == branch_id)
        
        bookings = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'bookings': [booking.to_dict() for booking in bookings.items],
            'total': bookings.total,
            'pages': bookings.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@room_bp.route('/room-bookings', methods=['POST'])
def create_room_booking():
    try:
        data = request.get_json()
        
        booking = RoomBooking(
            room_id=data['room_id'],
            customer_id=data['customer_id'],
            rental_start_date=datetime.strptime(data['rental_start_date'], '%Y-%m-%d').date(),
            rental_end_date=datetime.strptime(data['rental_end_date'], '%Y-%m-%d').date(),
            status=data.get('status', 'active'),
            contract_signed_date=datetime.strptime(data['contract_signed_date'], '%Y-%m-%d').date() if data.get('contract_signed_date') else None,
            monthly_rent=data.get('monthly_rent'),
            deposit_amount=data.get('deposit_amount'),
            notes=data.get('notes')
        )
        
        db.session.add(booking)
        
        # Update room availability
        room = Room.query.get(data['room_id'])
        if room:
            room.is_available = False
        
        db.session.commit()
        
        # Generate alerts for this booking
        generate_room_alerts(booking)
        
        return jsonify(booking.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@room_bp.route('/room-bookings/<int:booking_id>', methods=['PUT'])
def update_room_booking(booking_id):
    try:
        booking = RoomBooking.query.get_or_404(booking_id)
        data = request.get_json()
        
        old_status = booking.status
        
        booking.rental_start_date = datetime.strptime(data['rental_start_date'], '%Y-%m-%d').date() if data.get('rental_start_date') else booking.rental_start_date
        booking.rental_end_date = datetime.strptime(data['rental_end_date'], '%Y-%m-%d').date() if data.get('rental_end_date') else booking.rental_end_date
        booking.status = data.get('status', booking.status)
        booking.contract_signed_date = datetime.strptime(data['contract_signed_date'], '%Y-%m-%d').date() if data.get('contract_signed_date') else booking.contract_signed_date
        booking.monthly_rent = data.get('monthly_rent', booking.monthly_rent)
        booking.deposit_amount = data.get('deposit_amount', booking.deposit_amount)
        booking.notes = data.get('notes', booking.notes)
        booking.updated_at = datetime.utcnow()
        
        # Update room availability if status changed
        if old_status != booking.status:
            room = Room.query.get(booking.room_id)
            if room:
                if booking.status in ['cancelled', 'expired']:
                    room.is_available = True
                else:
                    room.is_available = False
        
        db.session.commit()
        return jsonify(booking.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@room_bp.route('/room-bookings/<int:booking_id>', methods=['DELETE'])
def delete_room_booking(booking_id):
    try:
        booking = RoomBooking.query.get_or_404(booking_id)
        
        # Make room available again
        room = Room.query.get(booking.room_id)
        if room:
            room.is_available = True
        
        db.session.delete(booking)
        db.session.commit()
        return jsonify({'message': 'Room booking deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Room Dashboard and Statistics
@room_bp.route('/room-dashboard/stats', methods=['GET'])
def get_room_dashboard_stats():
    try:
        total_branches = Branch.query.count()
        total_rooms = Room.query.count()
        occupied_rooms = Room.query.filter(Room.is_available == False).count()
        available_rooms = Room.query.filter(Room.is_available == True).count()
        
        active_bookings = RoomBooking.query.filter(RoomBooking.status == 'active').count()
        
        # Rooms expiring soon (within 30 days)
        thirty_days_from_now = date.today() + timedelta(days=30)
        expiring_soon = RoomBooking.query.filter(
            RoomBooking.rental_end_date <= thirty_days_from_now,
            RoomBooking.rental_end_date >= date.today(),
            RoomBooking.status == 'active'
        ).count()
        
        # Overdue bookings
        overdue_bookings = RoomBooking.query.filter(
            RoomBooking.rental_end_date < date.today(),
            RoomBooking.status == 'active'
        ).count()
        
        return jsonify({
            'total_branches': total_branches,
            'total_rooms': total_rooms,
            'occupied_rooms': occupied_rooms,
            'available_rooms': available_rooms,
            'active_bookings': active_bookings,
            'expiring_soon': expiring_soon,
            'overdue_bookings': overdue_bookings,
            'occupancy_rate': round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0, 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Room Alerts
@room_bp.route('/room-alerts/upcoming', methods=['GET'])
def get_upcoming_room_alerts():
    try:
        today = date.today()
        upcoming_alerts = RoomAlert.query.filter(
            RoomAlert.alert_date >= today,
            RoomAlert.is_sent == False
        ).order_by(RoomAlert.alert_date).all()
        
        return jsonify([alert.to_dict() for alert in upcoming_alerts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@room_bp.route('/room-alerts/<int:alert_id>/mark_sent', methods=['POST'])
def mark_room_alert_as_sent(alert_id):
    try:
        alert = RoomAlert.query.get_or_404(alert_id)
        alert.is_sent = True
        db.session.commit()
        return jsonify({'message': 'Alert marked as sent'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Web Room Bookings (from website)
@room_bp.route('/web-room-bookings', methods=['GET'])
def get_web_room_bookings():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = WebRoomBooking.query
        
        if status:
            query = query.filter(WebRoomBooking.status == status)
        
        bookings = query.order_by(WebRoomBooking.booking_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'bookings': [booking.to_dict() for booking in bookings.items],
            'total': bookings.total,
            'pages': bookings.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@room_bp.route('/web-room-bookings', methods=['POST'])
def create_web_room_booking():
    try:
        data = request.get_json()
        
        booking = WebRoomBooking(
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_phone=data.get('customer_phone'),
            branch_id=data['branch_id'],
            room_id=data.get('room_id'),
            preferred_start_date=datetime.strptime(data['preferred_start_date'], '%Y-%m-%d').date(),
            preferred_end_date=datetime.strptime(data['preferred_end_date'], '%Y-%m-%d').date() if data.get('preferred_end_date') else None,
            message=data.get('message'),
            status='pending'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify(booking.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def generate_room_alerts(booking):
    """Generate alerts for room booking expiration"""
    try:
        alerts_to_create = []
        end_date = booking.rental_end_date
        
        # 20 days before for 30-day contracts
        contract_duration = (booking.rental_end_date - booking.rental_start_date).days
        if contract_duration <= 30:
            alert_date = end_date - timedelta(days=20)
            if alert_date >= date.today():
                alerts_to_create.append(RoomAlert(
                    booking_id=booking.booking_id,
                    alert_date=alert_date,
                    alert_type='20_days_before_30_day_contract'
                ))
        
        # 2 weeks before
        alert_date = end_date - timedelta(days=14)
        if alert_date >= date.today():
            alerts_to_create.append(RoomAlert(
                booking_id=booking.booking_id,
                alert_date=alert_date,
                alert_type='2_weeks_before'
            ))
        
        # 1 week before
        alert_date = end_date - timedelta(days=7)
        if alert_date >= date.today():
            alerts_to_create.append(RoomAlert(
                booking_id=booking.booking_id,
                alert_date=alert_date,
                alert_type='1_week_before'
            ))
        
        # Due date
        alerts_to_create.append(RoomAlert(
            booking_id=booking.booking_id,
            alert_date=end_date,
            alert_type='due_date'
        ))
        
        # 3 days overdue
        alert_date = end_date + timedelta(days=3)
        alerts_to_create.append(RoomAlert(
            booking_id=booking.booking_id,
            alert_date=alert_date,
            alert_type='3_days_overdue'
        ))
        
        # 7 days overdue
        alert_date = end_date + timedelta(days=7)
        alerts_to_create.append(RoomAlert(
            booking_id=booking.booking_id,
            alert_date=alert_date,
            alert_type='7_days_overdue'
        ))
        
        for alert in alerts_to_create:
            db.session.add(alert)
        
        db.session.commit()
    except Exception as e:
        print(f"Error generating room alerts: {e}")
        db.session.rollback() 