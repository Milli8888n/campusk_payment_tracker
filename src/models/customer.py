from src.models.user import db
from datetime import datetime, date
from decimal import Decimal

class Customer(db.Model):
    __tablename__ = 'customers'
    
    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255))
    tax_id = db.Column(db.String(50))
    nationality = db.Column(db.String(100))
    business_type = db.Column(db.String(255))
    enterprise_type = db.Column(db.String(255))
    id_card = db.Column(db.String(50))
    email = db.Column(db.String(255))
    mobile = db.Column(db.String(50))
    zalo = db.Column(db.String(50))
    whatsapp = db.Column(db.String(50))
    kakao = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with contracts
    contracts = db.relationship('Contract', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Customer {self.customer_name}>'
    
    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'company_name': self.company_name,
            'tax_id': self.tax_id,
            'nationality': self.nationality,
            'business_type': self.business_type,
            'enterprise_type': self.enterprise_type,
            'id_card': self.id_card,
            'email': self.email,
            'mobile': self.mobile,
            'zalo': self.zalo,
            'whatsapp': self.whatsapp,
            'kakao': self.kakao,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'contracts': [contract.to_dict() for contract in self.contracts]
        }


class Contract(db.Model):
    __tablename__ = 'contracts'
    
    contract_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    contract_type = db.Column(db.String(255), nullable=False)
    contract_value = db.Column(db.Numeric(18, 2), nullable=False)
    contract_start_date = db.Column(db.Date, nullable=False)
    contract_end_date = db.Column(db.Date, nullable=False)
    amount_paid = db.Column(db.Numeric(18, 2), default=0)
    last_payment_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False, default='Khách hỏi')
    additional_services = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with alerts
    alerts = db.relationship('Alert', backref='contract', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Contract {self.contract_id} - {self.contract_type}>'
    
    def calculate_amount_due(self):
        """Calculate the amount due based on contract value and amount paid"""
        return float(self.contract_value) - float(self.amount_paid)
    
    def to_dict(self):
        return {
            'contract_id': self.contract_id,
            'customer_id': self.customer_id,
            'contract_type': self.contract_type,
            'contract_value': float(self.contract_value),
            'contract_start_date': self.contract_start_date.isoformat() if self.contract_start_date else None,
            'contract_end_date': self.contract_end_date.isoformat() if self.contract_end_date else None,
            'amount_paid': float(self.amount_paid),
            'amount_due': self.calculate_amount_due(),
            'last_payment_date': self.last_payment_date.isoformat() if self.last_payment_date else None,
            'status': self.status,
            'additional_services': self.additional_services,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class WebBooking(db.Model):
    __tablename__ = 'web_bookings'
    
    web_booking_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)
    
    def __repr__(self):
        return f'<WebBooking {self.web_booking_id}>'
    
    def to_dict(self):
        return {
            'web_booking_id': self.web_booking_id,
            'customer_id': self.customer_id,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'details': self.details
        }


class Alert(db.Model):
    __tablename__ = 'alerts'
    
    alert_id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.contract_id'), nullable=False)
    alert_date = db.Column(db.Date, nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # '2_weeks_before', '1_week_before', '3_days_before', 'due_date'
    is_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Alert {self.alert_id} - {self.alert_type}>'
    
    def to_dict(self):
        return {
            'alert_id': self.alert_id,
            'contract_id': self.contract_id,
            'alert_date': self.alert_date.isoformat() if self.alert_date else None,
            'alert_type': self.alert_type,
            'is_sent': self.is_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'contract': self.contract.to_dict() if self.contract else None
        }

