"""
User model for authentication and role management
"""
import re
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    """User model with role-based authentication"""
    
    __tablename__ = 'users'
    
    # User roles
    ROLE_CUSTOMER = 'customer'
    ROLE_ADMIN = 'admin'
    VALID_ROLES = [ROLE_CUSTOMER, ROLE_ADMIN]
    
    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_CUSTOMER)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    purchase_requests = db.relationship('PurchaseRequest', 
                                      foreign_keys='PurchaseRequest.customer_id',
                                      backref='customer', 
                                      lazy='dynamic')
    processed_requests = db.relationship('PurchaseRequest',
                                       foreign_keys='PurchaseRequest.admin_id',
                                       backref='processed_by_admin',
                                       lazy='dynamic')
    
    def __init__(self, email, first_name, last_name, role=ROLE_CUSTOMER):
        """Initialize user with validation"""
        self.email = self.validate_email(email)
        self.first_name = self.validate_name(first_name, "First name")
        self.last_name = self.validate_name(last_name, "Last name")
        self.role = self.validate_role(role)
    
    def set_password(self, password):
        """Set password with validation and hashing"""
        self.validate_password(password)
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    # Role checking methods
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == self.ROLE_ADMIN
    
    def is_customer(self):
        """Check if user has customer role"""
        return self.role == self.ROLE_CUSTOMER
    
    # Validation methods
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email or not isinstance(email, str):
            raise ValueError("Email is required")
        
        email = email.strip().lower()
        
        # Basic email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        if len(email) > 120:
            raise ValueError("Email is too long (maximum 120 characters)")
        
        return email
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if not password:
            raise ValueError("Password is required")
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if len(password) > 128:
            raise ValueError("Password is too long (maximum 128 characters)")
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            raise ValueError("Password must contain at least one number")
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain at least one special character")
        
        return password
    
    @staticmethod
    def validate_name(name, field_name="Name"):
        """Validate first/last name"""
        if not name or not isinstance(name, str):
            raise ValueError(f"{field_name} is required")
        
        name = name.strip()
        
        if len(name) < 2:
            raise ValueError(f"{field_name} must be at least 2 characters long")
        
        if len(name) > 80:
            raise ValueError(f"{field_name} is too long (maximum 80 characters)")
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            raise ValueError(f"{field_name} can only contain letters, spaces, hyphens, and apostrophes")
        
        return name.title()  # Capitalize properly
    
    @staticmethod
    def validate_role(role):
        """Validate user role"""
        if role not in User.VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(User.VALID_ROLES)}")
        return role
    
    # Query methods
    @classmethod
    def get_by_email(cls, email):
        """Get user by email address"""
        return cls.query.filter_by(email=email.lower().strip()).first()
    
    @classmethod
    def get_active_users(cls):
        """Get all active users"""
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def get_users_by_role(cls, role):
        """Get users by role"""
        return cls.query.filter_by(role=role, is_active=True).all()
    
    # String representation
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
    
    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }