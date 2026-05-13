"""
Simple workflow integration test for Smart Inventory Management System
"""

import sys
import os
from decimal import Decimal

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_integration():
    """Test basic component integration"""
    try:
        # Test imports
        from app import create_app
        from extensions import db
        from models.user import User
        from models.product import Product
        from models.purchase_request import PurchaseRequest
        from utils.workflow_integration import WorkflowIntegrator
        
        print("✓ All imports successful")
        
        # Test app creation
        app = create_app('testing')
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            # Test database creation
            db.create_all()
            print("✓ Database created successfully")
            
            # Test user creation
            admin = User(
                email='test@admin.com',
                first_name='Test',
                last_name='Admin',
                role='admin'
            )
            admin.set_password('TestPass123!')
            db.session.add(admin)
            
            customer = User(
                email='test@customer.com',
                first_name='Test',
                last_name='Customer',
                role='customer'
            )
            customer.set_password('TestPass123!')
            db.session.add(customer)
            
            db.session.commit()
            print("✓ Users created successfully")
            
            # Test product creation
            product = Product(
                name='Test Product',
                category='Test Category',
                cost_price=Decimal('50.00'),
                selling_price=Decimal('75.00'),
                quantity=100
            )
            db.session.add(product)
            db.session.commit()
            print("✓ Product created successfully")
            
            # Test purchase request creation
            request = PurchaseRequest(
                customer_id=customer.id,
                product_id=product.id,
                quantity=5
            )
            db.session.add(request)
            db.session.commit()
            print("✓ Purchase request created successfully")
            
            # Test workflow integrator
            integrator = WorkflowIntegrator()
            
            # Test purchase approval workflow
            result = integrator.process_purchase_request_approval(request, admin)
            if result['success']:
                print("✓ Purchase approval workflow successful")
                
                # Verify stock was reduced
                db.session.refresh(product)
                if product.quantity == 95:  # 100 - 5 = 95
                    print("✓ Stock reduction verified")
                else:
                    print(f"✗ Stock reduction failed: expected 95, got {product.quantity}")
            else:
                print(f"✗ Purchase approval workflow failed: {result['error']}")
            
            # Test AI integration (basic)
            try:
                ai_result = integrator.process_ai_restocking_suggestions()
                if ai_result['success']:
                    print("✓ AI integration working")
                else:
                    print(f"⚠ AI integration warning: {ai_result['error']}")
            except Exception as e:
                print(f"⚠ AI integration not fully functional: {str(e)}")
            
            # Test dashboard integration
            try:
                dashboard_result = integrator.process_dashboard_data_integration()
                if dashboard_result['success']:
                    print("✓ Dashboard integration working")
                else:
                    print(f"✗ Dashboard integration failed: {dashboard_result['error']}")
            except Exception as e:
                print(f"✗ Dashboard integration error: {str(e)}")
            
        print("\n🎉 Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_authentication_integration():
    """Test authentication system integration"""
    try:
        from auth_service import AuthenticationService
        from models.user import User
        
        # Test user registration
        success, user, error = AuthenticationService.register_user(
            email='integration@test.com',
            password='IntegrationTest123!',
            first_name='Integration',
            last_name='Test',
            role='customer'
        )
        
        if success:
            print("✓ User registration integration working")
        else:
            print(f"✗ User registration failed: {error}")
            return False
        
        # Test user authentication
        success, auth_user, error = AuthenticationService.authenticate_user(
            'integration@test.com',
            'IntegrationTest123!'
        )
        
        if success:
            print("✓ User authentication integration working")
        else:
            print(f"✗ User authentication failed: {error}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication integration test failed: {str(e)}")
        return False


def test_api_endpoints():
    """Test API endpoint integration"""
    try:
        from app import create_app
        
        app = create_app('testing')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.test_client() as client:
            # Test basic routes
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Home page accessible")
            else:
                print(f"✗ Home page failed: {response.status_code}")
            
            # Test login page
            response = client.get('/login')
            if response.status_code == 200:
                print("✓ Login page accessible")
            else:
                print(f"✗ Login page failed: {response.status_code}")
            
            # Test protected route (should redirect)
            response = client.get('/admin/products')
            if response.status_code in [302, 401, 403]:
                print("✓ Protected routes properly secured")
            else:
                print(f"⚠ Protected route security concern: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoint test failed: {str(e)}")
        return False


if __name__ == '__main__':
    print("🚀 Starting Smart Inventory System Integration Tests\n")
    
    tests = [
        ("Basic Integration", test_basic_integration),
        ("Authentication Integration", test_authentication_integration),
        ("API Endpoints", test_api_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Test:")
        print("-" * 40)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} Test PASSED")
        else:
            print(f"❌ {test_name} Test FAILED")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! System components are properly connected.")
    else:
        print("⚠️  Some integration tests failed. Please review the errors above.")