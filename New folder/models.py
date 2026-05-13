"""
Database models for Smart Inventory Management System
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    User model with role-based authentication
    Supports both customer and admin roles with secure password handling
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('customer', 'admin', name='user_roles'), nullable=False, default='customer')
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    purchase_requests = db.relationship('PurchaseRequest', foreign_keys='PurchaseRequest.customer_id', 
                                      backref='customer', lazy='dynamic')
    processed_requests = db.relationship('PurchaseRequest', foreign_keys='PurchaseRequest.admin_id', 
                                       backref='admin', lazy='dynamic')
    
    def __init__(self, email, first_name, last_name, role='customer', **kwargs):
        """Initialize user with validation"""
        self.email = self.validate_email(email)
        self.first_name = self.validate_name(first_name, 'First name')
        self.last_name = self.validate_name(last_name, 'Last name')
        self.role = self.validate_role(role)
        self.is_active = kwargs.get('is_active', True)
        self.created_at = kwargs.get('created_at', datetime.utcnow())
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email or not isinstance(email, str):
            raise ValueError("Email is required and must be a string")
        
        email = email.strip().lower()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        if len(email) > 120:
            raise ValueError("Email must be less than 120 characters")
        
        return email
    
    @staticmethod
    def validate_name(name, field_name):
        """Validate name fields"""
        if not name or not isinstance(name, str):
            raise ValueError(f"{field_name} is required and must be a string")
        
        name = name.strip()
        
        if len(name) < 2:
            raise ValueError(f"{field_name} must be at least 2 characters long")
        
        if len(name) > 80:
            raise ValueError(f"{field_name} must be less than 80 characters")
        
        if not re.match(r'^[a-zA-Z\s\'-]+$', name):
            raise ValueError(f"{field_name} can only contain letters, spaces, hyphens, and apostrophes")
        
        return name
    
    @staticmethod
    def validate_role(role):
        """Validate user role"""
        valid_roles = ['customer', 'admin']
        if role not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return role
    
    @staticmethod
    def validate_password(password):
        """
        Validate password strength
        Requirements: 3.1, 3.2 - Secure password storage and validation
        """
        if not password or not isinstance(password, str):
            raise ValueError("Password is required and must be a string")
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if len(password) > 128:
            raise ValueError("Password must be less than 128 characters")
        
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
            raise ValueError("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
        
        return True
    
    def set_password(self, password):
        """
        Hash and set password with validation
        Requirements: 3.1, 3.2 - Secure password storage
        """
        self.validate_password(password)
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    def check_password(self, password):
        """
        Check if provided password matches hash
        Requirements: 3.2 - Authentication with valid credentials
        """
        if not password or not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
    
    def is_customer(self):
        """Check if user has customer role"""
        return self.role == 'customer'
    
    def get_full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"


# PurchaseRequest model is now implemented in models/purchase_request.py