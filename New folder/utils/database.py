"""
Database utilities and helper functions
"""

from datetime import datetime
from extensions import db

def init_database(app):
    """
    Initialize database with app context
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        from models import User, Product, PurchaseRequest, Sale, AIPrediction
        db.create_all()
        
        # Create default admin user if none exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                email='admin@inventory.com',
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            admin.set_password('admin123')  # Change in production
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: admin@inventory.com / admin123")

def create_sample_data():
    """
    Create sample data for development and testing
    """
    from models import User, Product
    
    # Sample products
    sample_products = [
        {
            'name': 'Laptop Computer',
            'description': 'High-performance laptop for business use',
            'category': 'Electronics',
            'cost_price': 800.00,
            'selling_price': 1200.00,
            'quantity': 25,
            'low_stock_threshold': 5
        },
        {
            'name': 'Office Chair',
            'description': 'Ergonomic office chair with lumbar support',
            'category': 'Furniture',
            'cost_price': 150.00,
            'selling_price': 250.00,
            'quantity': 15,
            'low_stock_threshold': 3
        },
        {
            'name': 'Wireless Mouse',
            'description': 'Bluetooth wireless mouse',
            'category': 'Electronics',
            'cost_price': 20.00,
            'selling_price': 35.00,
            'quantity': 50,
            'low_stock_threshold': 10
        }
    ]
    
    for product_data in sample_products:
        existing = Product.query.filter_by(name=product_data['name']).first()
        if not existing:
            product = Product(**product_data)
            db.session.add(product)
    
    # Sample customer
    customer = User.query.filter_by(email='customer@test.com').first()
    if not customer:
        customer = User(
            email='customer@test.com',
            first_name='Test',
            last_name='Customer',
            role='customer'
        )
        customer.set_password('customer123')
        db.session.add(customer)
    
    db.session.commit()
    print("Sample data created successfully")