from enum import Enum as PyEnum
from datetime import datetime
from extensions import *
from sqlalchemy import Enum,text


class OrderStatus(PyEnum):
    PENDING = "pending"
    VERIFIED = "verified"
    DELIVERED = "delivered"
    PAYMENT_VERIFICATION = "payment_verification"

# Payment Status Enum
class PaymentStatus(PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

# Complaint Status Enum
class ComplaintStatus(PyEnum):
    PENDING = "pending"
    RESOLVED = "resolved"
    REJECTED = "rejected"

# Promo Code Type Enum
class PromoCodeType(PyEnum):
    DELIVERY = "delivery"
    MENU = "menu"

class Role(PyEnum):
    ADMIN = "admin"
    USER ="user"
    MANAGER ="manager"

# User Table
class User(db.Model,UserMixin):
    __tablename__ = 'user'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    whatsapp_no = db.Column(db.String(20), nullable=False)
    role = db.Column(Enum(Role), default=Role.USER, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_active(self):
        return True  # Modify this if you want to deactivate users


    __table_args__ = {'extend_existing': True}  # Allow redefining if the table exists

# Restaurant Table
class Restaurant(db.Model):
    __tablename__ = 'restaurant'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(8), unique=True, nullable=True)  # Restaurant code, e.g., 'K' for KFC
    total_orders = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = {'extend_existing': True}  # Allow redefining if the table exists

# Rider Table
class Rider(db.Model):
    __tablename__ = 'rider'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)

    __table_args__ = {'extend_existing': True}  # Allow redefining if the table exists

# Delivery Location Table
class Location(db.Model):
    __tablename__ = 'location'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    __table_args__ = {'extend_existing': True}  # Allow redefining if the table exists

# Extra Charges Table (Fixed Charges like Standard Fee, Express Fee, Red Alert)
class ExtraCharges(db.Model):
    __tablename__ = 'extra_charges'
    charge_name = db.Column(db.String(50), primary_key=True)  # Fixed names like "Standard Fee", "Express Fee"
    value = db.Column(db.DECIMAL(10,2), nullable=False)  

    __table_args__ = {'extend_existing': True}  

# Menu Table (Each Restaurant Has Its Own Menu)
class Menu(db.Model):
    __tablename__ = 'menu'  
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.DECIMAL(10,2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)

    __table_args__ = {'extend_existing': True}  

# Orders Table (Stores Main Order Info, Items are Stored in a Parseable Format)
class Order(db.Model):
    __tablename__ = 'order'  
    id = db.Column(db.String(64), primary_key=True)
    sequence = db.Column(db.Integer, nullable=False)  # For tracking order numbers per restaurant
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey('rider.id'), nullable=True)  # Assigned later
    items = db.Column(db.Text, nullable=False)  # JSON format to store ordered items
    status = db.Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    special_instructions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships for template access
    user = db.relationship('User', backref='orders')
    restaurant = db.relationship('Restaurant', backref='orders')
    rider = db.relationship('Rider', backref='orders')

    __table_args__ = {'extend_existing': True}

    @staticmethod
    def generate_order_id(restaurant_id):
        """Generate a new order ID using restaurant code and sequence number"""
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant or not restaurant.code:
            raise ValueError("Restaurant not found or has no code")
        
        # Get the last sequence number for this restaurant
        last_order = Order.query.filter_by(restaurant_id=restaurant_id).order_by(Order.sequence.desc()).first()
        sequence = (last_order.sequence + 1) if last_order else 1
        
        # Format: RESTAURANT_CODE-SEQUENCE (e.g., K-000001)
        return f"{restaurant.code}-{str(sequence).zfill(6)}"

    @property
    def display_code(self):
        """Return the display code for the order"""
        return self.id

# Payments Table (Tracks Order Payments)
class Payment(db.Model):
    __tablename__ = 'payment'  
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(64), db.ForeignKey('order.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.DECIMAL(10,2), nullable=False)
    status = db.Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = {'extend_existing': True}  

# Complaints Table (Each Restaurant Has Its Own Complaints, Visible to Managers)
class Complaint(db.Model):
    __tablename__ = 'complaint'  
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    order_id = db.Column(db.String(64), db.ForeignKey('order.id'), nullable=True)  # Foreign Key to Order Table
    description = db.Column(db.Text, nullable=False)
    status = db.Column(Enum(ComplaintStatus), default=ComplaintStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = {'extend_existing': True}  

# Promo Code Table (Each Restaurant Can Have Its Own Promo Codes)
class PromoCode(db.Model):
    __tablename__ = 'promo_code'  
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    discount_percentage = db.Column(db.Integer, nullable=False)
    type = db.Column(Enum(PromoCodeType), nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    time_limit = db.Column(db.DateTime, nullable=True)  # Expiry after activation

    __table_args__ = {'extend_existing': True}  

# Settings Table (Each Restaurant Has Its Own Settings, Only Accessible to Admins)
class RestaurantSettings(db.Model):
    __tablename__ = 'restaurant_settings'
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), unique=True, nullable=False)
    slots = db.Column(db.Text, nullable=True)  # JSON format for available time slots
    ordering_online = db.Column(db.Boolean, default=True, nullable=False)
    midnight = db.Column(db.Time, nullable=True)  # Midnight deals timing

    __table_args__ = {'extend_existing': True}  

# Email Notifications Table (Users Receive Deal Notifications By Default)
class EmailNotification(db.Model):
    __tablename__ = 'email_notification'  
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = {'extend_existing': True}  





