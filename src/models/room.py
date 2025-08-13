from src.models.user import db
from datetime import datetime, date
from decimal import Decimal

class Branch(db.Model):
    __tablename__ = 'branches'
    
    branch_id = db.Column(db.Integer, primary_key=True)
    branch_name = db.Column(db.String(255), nullable=False)
    total_rooms = db.Column(db.Integer, default=0)
    address = db.Column(db.String(500))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with rooms
    rooms = db.relationship('Room', backref='branch', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Branch {self.branch_name}>'
    
    def to_dict(self, include_rooms=False):
        result = {
            'branch_id': self.branch_id,
            'branch_name': self.branch_name,
            'total_rooms': self.total_rooms,
            'address': self.address,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_rooms:
            result['rooms'] = [room.to_dict(include_bookings=False) for room in self.rooms]
        return result


class Room(db.Model):
    __tablename__ = 'rooms'
    
    room_id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.branch_id'), nullable=False)
    room_number = db.Column(db.String(50), nullable=False)
    room_type = db.Column(db.String(100))
    area = db.Column(db.Numeric(10, 2))  # in square meters
    orientation = db.Column(db.String(100))  # e.g., "North", "South-East"
    rental_price = db.Column(db.Numeric(18, 2), nullable=False)
    capacity = db.Column(db.Integer, default=1)
    amenities = db.Column(db.Text)  # JSON string of amenities
    notes = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(50), default='available')  # available|occupied|maintenance|closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with bookings
    bookings = db.relationship('RoomBooking', backref='room', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Room {self.room_number} - Branch {self.branch_id}>'
    
    def to_dict(self, include_bookings=False, include_branch=False):
        result = {
            'room_id': self.room_id,
            'branch_id': self.branch_id,
            'room_number': self.room_number,
            'room_type': self.room_type,
            'area': float(self.area) if self.area else None,
            'orientation': self.orientation,
            'rental_price': float(self.rental_price),
            'capacity': self.capacity,
            'amenities': self.amenities,
            'notes': self.notes,
            'is_available': self.is_available,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_bookings:
            result['current_booking'] = self.get_current_booking()
        if include_branch:
            result['branch'] = self.branch.to_dict(include_rooms=False) if self.branch else None
        return result
    
    def get_current_booking(self):
        """Get current active booking for this room"""
        today = date.today()
        current_booking = RoomBooking.query.filter(
            RoomBooking.room_id == self.room_id,
            RoomBooking.rental_start_date <= today,
            RoomBooking.rental_end_date >= today,
            RoomBooking.status == 'active'
        ).first()
        
        return current_booking.to_dict(include_room=False, include_customer=True) if current_booking else None


class RoomBooking(db.Model):
    __tablename__ = 'room_bookings'
    
    booking_id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)  # Reference to customer table
    rental_start_date = db.Column(db.Date, nullable=False)
    rental_end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='active')  # active, expired, cancelled
    contract_signed_date = db.Column(db.Date)
    monthly_rent = db.Column(db.Numeric(18, 2))
    deposit_amount = db.Column(db.Numeric(18, 2))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with customer and alerts
    customer = db.relationship('Customer', backref='room_bookings', lazy=True)
    alerts = db.relationship('RoomAlert', backref='booking', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<RoomBooking {self.booking_id} - Room {self.room_id}>'
    
    def to_dict(self, include_room=False, include_customer=False):
        result = {
            'booking_id': self.booking_id,
            'room_id': self.room_id,
            'customer_id': self.customer_id,
            'rental_start_date': self.rental_start_date.isoformat() if self.rental_start_date else None,
            'rental_end_date': self.rental_end_date.isoformat() if self.rental_end_date else None,
            'status': self.status,
            'contract_signed_date': self.contract_signed_date.isoformat() if self.contract_signed_date else None,
            'monthly_rent': float(self.monthly_rent) if self.monthly_rent else None,
            'deposit_amount': float(self.deposit_amount) if self.deposit_amount else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_customer and self.customer:
            result['customer'] = {
                'customer_id': self.customer.customer_id,
                'customer_name': self.customer.customer_name,
                'email': getattr(self.customer, 'email', None),
                'mobile': getattr(self.customer, 'mobile', None),
                'company_name': getattr(self.customer, 'company_name', None)
            }
        if include_room and self.room:
            result['room'] = self.room.to_dict(include_bookings=False, include_branch=False)
        return result


class RoomAlert(db.Model):
    __tablename__ = 'room_alerts'
    
    alert_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('room_bookings.booking_id'), nullable=False)
    alert_date = db.Column(db.Date, nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # '2_weeks_before', '1_week_before', 'due_date', '3_days_overdue', '7_days_overdue', '20_days_before_30_day_contract'
    is_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RoomAlert {self.alert_id} - {self.alert_type}>'
    
    def to_dict(self, include_booking=False):
        result = {
            'alert_id': self.alert_id,
            'booking_id': self.booking_id,
            'alert_date': self.alert_date.isoformat() if self.alert_date else None,
            'alert_type': self.alert_type,
            'is_sent': self.is_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_booking and self.booking:
            result['booking'] = self.booking.to_dict(include_room=False, include_customer=True)
        return result


class WebRoomBooking(db.Model):
    __tablename__ = 'web_room_bookings'
    
    web_booking_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    customer_email = db.Column(db.String(255), nullable=False)
    customer_phone = db.Column(db.String(50))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.branch_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.room_id'))
    preferred_start_date = db.Column(db.Date, nullable=False)
    preferred_end_date = db.Column(db.Date)
    message = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, contacted, converted, cancelled
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    branch = db.relationship('Branch', backref='web_bookings', lazy=True)
    room = db.relationship('Room', backref='web_bookings', lazy=True)
    
    def __repr__(self):
        return f'<WebRoomBooking {self.web_booking_id}>'
    
    def to_dict(self, include_branch=False, include_room=False):
        result = {
            'web_booking_id': self.web_booking_id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'branch_id': self.branch_id,
            'room_id': self.room_id,
            'preferred_start_date': self.preferred_start_date.isoformat() if self.preferred_start_date else None,
            'preferred_end_date': self.preferred_end_date.isoformat() if self.preferred_end_date else None,
            'message': self.message,
            'status': self.status,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None
        }
        if include_branch and self.branch:
            result['branch'] = self.branch.to_dict(include_rooms=False)
        if include_room and self.room:
            result['room'] = self.room.to_dict(include_bookings=False, include_branch=False)
        return result

