#!/usr/bin/env python3
"""
Test script for enhanced authentication functionality
Run this to verify User model validation and authentication service work correctly
"""

import os
import sys
from app import app
from models import db, User
from auth_service import AuthenticationService

def test_user_model_validation():
    """Test User model validation features"""
    print("Testing User Model Validation...")
    
    # Test email validation
    try:
        User.validate_email("invalid-email")
        print("✗ Email validation failed - should reject invalid email")
        return False
    except ValueError:
        print("✓ Email validation works - rejects invalid email")
    
    # Test password validation
    try:
        User.validate_password("weak")
        print("✗ Password validation failed - should reject weak password")
        return False
    except ValueError:
        print("✓ Password validation works - rejects weak password")
    
    # Test valid password
    try:
        User.validate_password("StrongPass123!")
        print("✓ Password validation works - accepts strong password")
    except ValueError as e:
        print(f"✗ Password validation failed - should accept strong password: {e}")
        return False
    
    # Test name validation
    try:
        User.validate_name("A", "First name")
        print("✗ Name validation failed - should reject short name")
        return False
    except ValueError:
        print("✓ Name validation works - rejects short name")
    
    return True

def test_authentication_service():
    """Test AuthenticationService functionality"""
    print("\nTesting Authentication Service...")
    
    # Test user registration with validation
    success, user, error = AuthenticationService.register_user(
        email="testuser@example.com",
        password="TestPass123!",
        first_name="Test",
        last_name="User",
        role="customer"
    )
    
    if success and user:
        print("✓ User registration with validation works")
    else:
        print(f"✗ User registration failed: {error}")
        return False
    
    # Test duplicate registration
    success, user, error = AuthenticationService.register_user(
        email="testuser@example.com",
        password="TestPass123!",
        first_name="Test",
        last_name="User",
        role="customer"
    )
    
    if not success and "already exists" in error:
        print("✓ Duplicate registration prevention works")
    else:
        print("✗ Duplicate registration prevention failed")
        return False
    
    # Test authentication
    success, user, error = AuthenticationService.authenticate_user(
        email="testuser@example.com",
        password="TestPass123!"
    )
    
    if success and user:
        print("✓ User authentication works")
    else:
        print(f"✗ User authentication failed: {error}")
        return False
    
    # Test wrong password
    success, user, error = AuthenticationService.authenticate_user(
        email="testuser@example.com",
        password="WrongPassword"
    )
    
    if not success and "Invalid email or password" in error:
        print("✓ Wrong password rejection works")
    else:
        print("✗ Wrong password rejection failed")
        return False
    
    return True

def test_authentication():
    """Test complete authentication functionality"""
    print("Testing Smart Inventory System Authentication...")
    
    with app.app_context():
        # Create database tables
        db.create_all()
        print("✓ Database tables created")
        
        # Test model validation
        if not test_user_model_validation():
            return False
        
        # Test authentication service
        if not test_authentication_service():
            return False
        
        # Create admin user for testing
        admin_success, admin_user, admin_error = AuthenticationService.register_user(
            email="admin@example.com",
            password="AdminPass123!",
            first_name="Admin",
            last_name="User",
            role="admin"
        )
        
        if admin_success or "already exists" in (admin_error or ""):
            print("✓ Admin user created or already exists")
        else:
            print(f"✗ Admin user creation failed: {admin_error}")
            return False
        
        print("\nTest Users Available:")
        print("Customer: testuser@example.com / TestPass123!")
        print("Admin: admin@example.com / AdminPass123!")
        
        # Test role methods
        test_user = AuthenticationService.get_user_by_email("testuser@example.com")
        admin_user = AuthenticationService.get_user_by_email("admin@example.com")
        
        if test_user and test_user.is_customer() and not test_user.is_admin():
            print("✓ Customer role methods work")
        else:
            print("✗ Customer role methods failed")
            return False
        
        if admin_user and admin_user.is_admin() and not admin_user.is_customer():
            print("✓ Admin role methods work")
        else:
            print("✗ Admin role methods failed")
            return False
        
        return True

if __name__ == '__main__':
    if test_authentication():
        print("\n✓ All authentication tests passed!")
        print("\nTo test the web interface:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the app: python app.py")
        print("3. Visit http://localhost:5000/login")
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)