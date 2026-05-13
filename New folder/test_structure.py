#!/usr/bin/env python3
"""
Test script to verify the project structure is working correctly
"""

def test_imports():
    """Test that all modules can be imported correctly"""
    try:
        # Test config import
        from config import config
        print("✓ Config module imported successfully")
        
        # Test extensions import
        from extensions import db, login_manager
        print("✓ Extensions module imported successfully")
        
        # Test models import
        from models import User, Product, PurchaseRequest, Sale, AIPrediction
        print("✓ All models imported successfully")
        
        # Test utils import
        from utils import role_required, admin_required, customer_required
        print("✓ Utils module imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_app_creation():
    """Test that Flask app can be created"""
    try:
        from app import create_app
        app = create_app()
        print("✓ Flask app created successfully")
        
        # Test app context
        with app.app_context():
            from extensions import db
            from models import User
            
            # Test database table creation
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Test model creation
            admin_count = User.query.filter_by(role='admin').count()
            print(f"✓ Found {admin_count} admin user(s) in database")
        
        return True
    except Exception as e:
        print(f"✗ App creation error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Smart Inventory Management System Structure")
    print("=" * 50)
    
    success = True
    
    print("\n1. Testing module imports...")
    success &= test_imports()
    
    print("\n2. Testing Flask app creation...")
    success &= test_app_creation()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed! Project structure is working correctly.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == '__main__':
    main()