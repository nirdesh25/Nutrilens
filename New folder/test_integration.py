"""
Integration tests for Smart Inventory Management System
Tests the complete workflows and component integration
"""

import pytest
import json
from datetime import datetime, timedelta
from decimal import Decimal
from flask import url_for
from app import create_app
from extensions import db
from models.user import User
from models.product import Product
from models.purchase_request import PurchaseRequest
from models.sale import Sale
from models.ai_prediction import AIPrediction
from services.ai_prediction_service import AIPredictionService
from services.restocking_service import RestockingService
from services.analytics_service import AnalyticsService


class TestIntegration:
    """Integration test suite for complete system workflows"""
    
    @pytest.fixture
    def app(self):
        """Create test application"""
        app = create_app('testing')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture
    def admin_user(self, app):
        """Create admin user for testing"""
        with app.app_context():
            admin = User(
                email='admin@test.com',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            admin.set_password('AdminPass123!')
            db.session.add(admin)
            db.session.commit()
            return admin
    
    @pytest.fixture
    def customer_user(self, app):
        """Create customer user for testing"""
        with app.app_context():
            customer = User(
                email='customer@test.com',
                first_name='Customer',
                last_name='User',
                role='customer'
            )
            customer.set_password('CustomerPass123!')
            db.session.add(customer)
            db.session.commit()
            return customer
    
    @pytest.fixture
    def sample_products(self, app):
        """Create sample products for testing"""
        with app.app_context():
            products = [
                Product(
                    name='Laptop Computer',
                    category='Electronics',
                    cost_price=Decimal('800.00'),
                    selling_price=Decimal('1200.00'),
                    quantity=50,
                    low_stock_threshold=10
                ),
                Product(
                    name='Office Chair',
                    category='Furniture',
                    cost_price=Decimal('150.00'),
                    selling_price=Decimal('250.00'),
                    quantity=5,  # Low stock
                    low_stock_threshold=10
                ),
                Product(
                    name='Wireless Mouse',
                    category='Electronics',
                    cost_price=Decimal('20.00'),
                    selling_price=Decimal('35.00'),
                    quantity=0,  # Out of stock
                    low_stock_threshold=5
                )
            ]
            
            for product in products:
                db.session.add(product)
            
            db.session.commit()
            return products
    
    def login_user(self, client, email, password):
        """Helper method to log in a user"""
        return client.post('/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)
    
    def test_authentication_workflow_integration(self, client, app):
        """Test complete authentication workflow with role-based access"""
        with app.app_context():
            # Test registration
            response = client.post('/register', data={
                'email': 'newuser@test.com',
                'first_name': 'New',
                'last_name': 'User',
                'password': 'NewPass123!',
                'password_confirm': 'NewPass123!',
                'role': 'customer'
            })
            assert response.status_code == 302  # Redirect after successful registration
            
            # Verify user was created
            user = User.get_by_email('newuser@test.com')
            assert user is not None
            assert user.role == 'customer'
            
            # Test login
            response = self.login_user(client, 'newuser@test.com', 'NewPass123!')
            assert response.status_code == 200
            
            # Test role-based access - customer trying to access admin route
            response = client.get('/admin/products')
            assert response.status_code == 302  # Redirect due to insufficient permissions
            
            # Test logout
            response = client.get('/logout', follow_redirects=True)
            assert response.status_code == 200
    
    def test_purchase_workflow_integration(self, client, app, customer_user, admin_user, sample_products):
        """Test complete purchase request workflow from submission to approval"""
        with app.app_context():
            # Login as customer
            self.login_user(client, customer_user.email, 'CustomerPass123!')
            
            # Submit purchase request
            laptop = sample_products[0]  # Laptop with sufficient stock
            response = client.post(f'/products/{laptop.id}/request', data={
                'product_id': laptop.id,
                'quantity': 2
            })
            assert response.status_code == 302  # Redirect after successful submission
            
            # Verify request was created
            request_obj = PurchaseRequest.query.filter_by(
                customer_id=customer_user.id,
                product_id=laptop.id
            ).first()
            assert request_obj is not None
            assert request_obj.status == 'pending'
            assert request_obj.quantity == 2
            
            # Logout customer and login as admin
            client.get('/logout')
            self.login_user(client, admin_user.email, 'AdminPass123!')
            
            # Admin processes the request (approve)
            response = client.post(f'/admin/purchase-requests/{request_obj.id}/process', data={
                'action': 'approve'
            })
            assert response.status_code == 302  # Redirect after processing
            
            # Verify request was approved and stock was reduced
            db.session.refresh(request_obj)
            db.session.refresh(laptop)
            
            assert request_obj.status == 'approved'
            assert laptop.quantity == 48  # 50 - 2 = 48
            
            # Verify sale record was created
            sale = Sale.query.filter_by(purchase_request_id=request_obj.id).first()
            assert sale is not None
            assert sale.quantity == 2
            assert sale.total_amount == laptop.selling_price * 2
    
    def test_inventory_management_integration(self, client, app, admin_user, sample_products):
        """Test inventory management with stock alerts and AI integration"""
        with app.app_context():
            # Login as admin
            self.login_user(client, admin_user.email, 'AdminPass123!')
            
            # Test low stock detection
            low_stock_products = Product.get_low_stock_products()
            assert len(low_stock_products) >= 2  # Office Chair (5) and Wireless Mouse (0)
            
            # Test product creation
            response = client.post('/admin/products/add', data={
                'name': 'Test Product',
                'category': 'Test Category',
                'cost_price': '100.00',
                'selling_price': '150.00',
                'quantity': '25',
                'low_stock_threshold': '5'
            })
            assert response.status_code == 302  # Redirect after creation
            
            # Verify product was created
            new_product = Product.query.filter_by(name='Test Product').first()
            assert new_product is not None
            assert new_product.quantity == 25
            
            # Test stock update
            response = client.post(f'/admin/products/{new_product.id}/stock', data={
                'quantity': '10',
                'operation': 'subtract'
            })
            assert response.status_code == 200
            
            # Verify stock was updated
            db.session.refresh(new_product)
            assert new_product.quantity == 15  # 25 - 10 = 15
    
    def test_ai_predictions_integration(self, client, app, admin_user, sample_products):
        """Test AI prediction system integration with dashboard"""
        with app.app_context():
            # Create some historical sales data for AI training
            laptop = sample_products[0]
            
            # Create sales records for the past 30 days
            for i in range(30):
                sale_date = datetime.utcnow() - timedelta(days=i)
                sale = Sale(
                    product_id=laptop.id,
                    customer_id=admin_user.id,  # Using admin as customer for simplicity
                    quantity=2 + (i % 3),  # Varying quantities
                    unit_price=laptop.selling_price,
                    total_amount=laptop.selling_price * (2 + (i % 3)),
                    sale_date=sale_date
                )
                db.session.add(sale)
            
            db.session.commit()
            
            # Login as admin
            self.login_user(client, admin_user.email, 'AdminPass123!')
            
            # Test AI model training
            ai_service = AIPredictionService()
            training_result = ai_service.train_model(retrain=True)
            assert training_result['success'] is True
            
            # Test demand prediction
            prediction = ai_service.predict_demand(laptop.id, 'monthly')
            assert prediction is not None
            assert 'predicted_demand' in prediction
            assert 'confidence_score' in prediction
            
            # Test restocking suggestions
            restocking_service = RestockingService()
            suggestions = restocking_service.generate_comprehensive_suggestions()
            assert 'suggestions' in suggestions
            assert isinstance(suggestions['suggestions'], list)
            
            # Test AI API endpoints
            response = client.get('/api/admin/ai/suggestions')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'data' in data
    
    def test_analytics_dashboard_integration(self, client, app, admin_user, sample_products):
        """Test analytics dashboard with real data integration"""
        with app.app_context():
            # Create some sales and request data
            laptop = sample_products[0]
            
            # Create purchase requests
            for i in range(5):
                request = PurchaseRequest(
                    customer_id=admin_user.id,  # Using admin as customer for simplicity
                    product_id=laptop.id,
                    quantity=1 + i,
                    status='approved' if i < 3 else 'pending'
                )
                db.session.add(request)
            
            db.session.commit()
            
            # Login as admin
            self.login_user(client, admin_user.email, 'AdminPass123!')
            
            # Test dashboard data endpoint
            response = client.get('/api/admin/analytics/dashboard')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'data' in data
            
            dashboard_data = data['data']
            assert 'sales_metrics' in dashboard_data
            assert 'product_metrics' in dashboard_data
            assert 'request_metrics' in dashboard_data
            
            # Test analytics service directly
            analytics_data = AnalyticsService.get_dashboard_metrics(30)
            assert 'sales_metrics' in analytics_data
            assert 'product_metrics' in analytics_data
            
            # Test low stock alerts
            response = client.get('/api/admin/analytics/low-stock-alerts')
            assert response.status_code == 200
            
            alerts_data = json.loads(response.data)
            assert alerts_data['success'] is True
            assert 'data' in alerts_data
    
    def test_calendar_integration(self, client, app, admin_user, sample_products):
        """Test sales calendar integration with real sales data"""
        with app.app_context():
            # Create sales for specific dates
            laptop = sample_products[0]
            today = datetime.utcnow().date()
            
            # Create sales for today and yesterday
            for days_ago in [0, 1]:
                sale_date = today - timedelta(days=days_ago)
                sale = Sale(
                    product_id=laptop.id,
                    customer_id=admin_user.id,
                    quantity=5,
                    unit_price=laptop.selling_price,
                    total_amount=laptop.selling_price * 5,
                    sale_date=datetime.combine(sale_date, datetime.min.time())
                )
                db.session.add(sale)
            
            db.session.commit()
            
            # Login as admin
            self.login_user(client, admin_user.email, 'AdminPass123!')
            
            # Test calendar data endpoint
            response = client.get(f'/api/admin/analytics/calendar?month={today.month}&year={today.year}')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'data' in data
            
            calendar_data = data['data']
            assert 'events' in calendar_data
            assert 'summary' in calendar_data
            
            # Test specific date details
            response = client.get(f'/api/admin/analytics/calendar/date/{today.isoformat()}')
            assert response.status_code == 200
            
            date_data = json.loads(response.data)
            assert date_data['success'] is True
    
    def test_error_handling_integration(self, client, app, customer_user, sample_products):
        """Test error handling across different components"""
        with app.app_context():
            # Login as customer
            self.login_user(client, customer_user.email, 'CustomerPass123!')
            
            # Test requesting more stock than available
            out_of_stock_product = sample_products[2]  # Wireless Mouse with 0 stock
            
            response = client.post(f'/products/{out_of_stock_product.id}/request', data={
                'product_id': out_of_stock_product.id,
                'quantity': 1
            })
            # Should handle gracefully - either redirect with error or show error message
            assert response.status_code in [200, 302]
            
            # Test accessing non-existent product
            response = client.get('/products/99999')
            assert response.status_code == 404
            
            # Test invalid API requests
            response = client.post('/api/products/99999/quick-request', data={
                'quantity': 1
            })
            assert response.status_code == 404
            
            # Test customer accessing admin endpoints
            response = client.get('/admin/products')
            assert response.status_code == 302  # Redirect due to insufficient permissions
    
    def test_complete_user_journey(self, client, app):
        """Test complete user journey from registration to purchase completion"""
        with app.app_context():
            # 1. Register as customer
            response = client.post('/register', data={
                'email': 'journey@test.com',
                'first_name': 'Journey',
                'last_name': 'User',
                'password': 'JourneyPass123!',
                'password_confirm': 'JourneyPass123!',
                'role': 'customer'
            })
            assert response.status_code == 302
            
            # 2. Create admin and product
            admin = User(
                email='journeyadmin@test.com',
                first_name='Journey',
                last_name='Admin',
                role='admin'
            )
            admin.set_password('AdminPass123!')
            db.session.add(admin)
            
            product = Product(
                name='Journey Product',
                category='Test',
                cost_price=Decimal('50.00'),
                selling_price=Decimal('75.00'),
                quantity=100
            )
            db.session.add(product)
            db.session.commit()
            
            # 3. Customer browses products
            response = client.get('/products')
            assert response.status_code == 200
            
            # 4. Customer submits purchase request
            response = client.post(f'/products/{product.id}/request', data={
                'product_id': product.id,
                'quantity': 3
            })
            assert response.status_code == 302
            
            # 5. Customer views purchase history
            response = client.get('/purchase-history')
            assert response.status_code == 200
            
            # 6. Logout and login as admin
            client.get('/logout')
            self.login_user(client, 'journeyadmin@test.com', 'AdminPass123!')
            
            # 7. Admin views pending requests
            response = client.get('/admin/purchase-requests')
            assert response.status_code == 200
            
            # 8. Admin approves request
            request_obj = PurchaseRequest.query.filter_by(product_id=product.id).first()
            response = client.post(f'/admin/purchase-requests/{request_obj.id}/process', data={
                'action': 'approve'
            })
            assert response.status_code == 302
            
            # 9. Verify complete workflow
            db.session.refresh(request_obj)
            db.session.refresh(product)
            
            assert request_obj.status == 'approved'
            assert product.quantity == 97  # 100 - 3 = 97
            
            # 10. Admin views analytics
            response = client.get('/api/admin/analytics/dashboard')
            assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])