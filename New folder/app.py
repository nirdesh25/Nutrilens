"""
Smart Inventory Management System
Flask application with role-based authentication and inventory management
"""

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user, LoginManager, UserMixin, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, TextAreaField, DecimalField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from decimal import Decimal
import re
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///inventory.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    ROLE_CUSTOMER = 'customer'
    ROLE_ADMIN = 'admin'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_CUSTOMER)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == self.ROLE_ADMIN
    
    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# Product Model
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False, index=True)
    cost_price = db.Column(db.Numeric(10, 2), nullable=False)
    selling_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    low_stock_threshold = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold
    
    def is_out_of_stock(self):
        return self.quantity <= 0
    
    def can_fulfill_quantity(self, requested_quantity):
        return self.quantity >= requested_quantity

# Purchase Request Model
class PurchaseRequest(db.Model):
    __tablename__ = 'purchase_requests'
    
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    rejection_reason = db.Column(db.Text)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    processed_at = db.Column(db.DateTime)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='purchase_requests')
    product = db.relationship('Product', backref='purchase_requests')
    processed_by_admin = db.relationship('User', foreign_keys=[admin_id])
    
    @property
    def total_value(self):
        return self.product.selling_price * self.quantity if self.product else 0
    
    def can_be_processed(self):
        return self.status == self.STATUS_PENDING
    
    @classmethod
    def get_customer_requests(cls, customer_id):
        return cls.query.filter_by(customer_id=customer_id).order_by(cls.requested_at.desc())

# Forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=80)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Account Type', choices=[('customer', 'Customer'), ('admin', 'Administrator')], default='customer')
    submit = SubmitField('Register')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=200)])
    description = TextAreaField('Description')
    category = StringField('Category', validators=[DataRequired(), Length(min=2, max=100)])
    cost_price = DecimalField('Cost Price ($)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    selling_price = DecimalField('Selling Price ($)', validators=[DataRequired(), NumberRange(min=0)], places=2)
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    low_stock_threshold = IntegerField('Low Stock Alert Threshold', validators=[NumberRange(min=0)], default=10)
    submit = SubmitField('Save Product')

def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Routes
    @app.route('/')
    def index():
        """Home page - redirect based on authentication status"""
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('customer_dashboard'))
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.lower()).first()
            
            if user and user.check_password(form.password.data):
                login_user(user)
                user.last_login = datetime.utcnow()
                db.session.commit()
                flash(f'Welcome back, {user.first_name}!', 'success')
                
                # Redirect to next page or dashboard based on role
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                elif user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('customer_dashboard'))
            else:
                flash('Invalid email or password', 'error')
        
        return render_template('auth/login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Registration page"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            # Check if user already exists
            existing_user = User.query.filter_by(email=form.email.data.lower()).first()
            if existing_user:
                flash('Email address already registered', 'error')
            else:
                # Create new user
                user = User(
                    email=form.email.data.lower(),
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    role=form.role.data
                )
                user.set_password(form.password.data)
                
                db.session.add(user)
                db.session.commit()
                
                login_user(user)
                flash(f'Registration successful! Welcome, {user.first_name}!', 'success')
                
                # Redirect to appropriate dashboard based on role
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('customer_dashboard'))
        
        return render_template('auth/register.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout and redirect to login page"""
        user_name = current_user.first_name
        logout_user()
        flash(f'Goodbye, {user_name}! You have been logged out successfully.', 'info')
        return redirect(url_for('login'))
    
    # Dashboard routes
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        """Admin dashboard"""
        if current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('customer_dashboard'))
        
        # Get dashboard statistics
        total_products = Product.query.filter_by(is_active=True).count()
        low_stock_products = Product.query.filter(Product.quantity <= Product.low_stock_threshold, Product.is_active == True).count()
        pending_requests = PurchaseRequest.query.filter_by(status=PurchaseRequest.STATUS_PENDING).count()
        total_customers = User.query.filter_by(role=User.ROLE_CUSTOMER, is_active=True).count()
        
        return render_template('admin/dashboard.html', 
                             total_products=total_products,
                             low_stock_products=low_stock_products,
                             pending_requests=pending_requests,
                             total_customers=total_customers)
    
    @app.route('/customer/dashboard')
    @login_required
    def customer_dashboard():
        """Customer dashboard"""
        if current_user.role != 'customer':
            flash('Access denied. Customer account required.', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Get customer statistics
        total_requests = PurchaseRequest.query.filter_by(customer_id=current_user.id).count()
        pending_requests = PurchaseRequest.query.filter_by(customer_id=current_user.id, status=PurchaseRequest.STATUS_PENDING).count()
        approved_requests = PurchaseRequest.query.filter_by(customer_id=current_user.id, status=PurchaseRequest.STATUS_APPROVED).count()
        
        return render_template('customer/dashboard.html',
                             total_requests=total_requests,
                             pending_requests=pending_requests,
                             approved_requests=approved_requests)
    
    # Product routes
    @app.route('/products')
    @login_required
    def products():
        """Display products for customers to browse and request"""
        if current_user.role != 'customer':
            flash('Access denied. Customer account required.', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Get search and filter parameters
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        
        # Build query
        query = Product.query.filter_by(is_active=True)
        
        if search:
            query = query.filter(Product.name.contains(search))
        
        if category:
            query = query.filter(Product.category == category)
        
        products = query.all()
        categories = db.session.query(Product.category).filter_by(is_active=True).distinct().all()
        categories = [cat[0] for cat in categories]
        
        return render_template('customer/products.html', 
                             products=products, 
                             categories=categories,
                             search=search,
                             selected_category=category)
    
    @app.route('/purchase-history')
    @login_required
    def purchase_history():
        """Display customer's purchase request history"""
        if current_user.role != 'customer':
            flash('Access denied. Customer account required.', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Get filter parameters
        status_filter = request.args.get('status', '')
        
        # Build query
        query = PurchaseRequest.get_customer_requests(current_user.id)
        
        if status_filter:
            query = query.filter(PurchaseRequest.status == status_filter)
        
        requests = query.all()
        
        return render_template('customer/purchase_history.html', 
                             requests=requests,
                             status_filter=status_filter)
    
    # Admin Product Management
    @app.route('/admin/products')
    @login_required
    def admin_products():
        """Admin product management"""
        if current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('customer_dashboard'))
        
        products = Product.query.filter_by(is_active=True).all()
        return render_template('admin/products.html', products=products)
    
    @app.route('/admin/products/add', methods=['GET', 'POST'])
    @login_required
    def add_product():
        """Add new product"""
        if current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('customer_dashboard'))
        
        form = ProductForm()
        if form.validate_on_submit():
            product = Product(
                name=form.name.data,
                description=form.description.data,
                category=form.category.data,
                cost_price=form.cost_price.data,
                selling_price=form.selling_price.data,
                quantity=form.quantity.data,
                low_stock_threshold=form.low_stock_threshold.data
            )
            
            db.session.add(product)
            db.session.commit()
            flash(f'Product "{product.name}" added successfully!', 'success')
            return redirect(url_for('admin_products'))
        
        return render_template('admin/add_product.html', form=form)
    
    # Admin Purchase Request Management
    @app.route('/admin/purchase-requests')
    @login_required
    def admin_purchase_requests():
        """Admin purchase request management"""
        if current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('customer_dashboard'))
        
        status_filter = request.args.get('status', 'pending')
        
        if status_filter == 'all':
            requests = PurchaseRequest.query.order_by(PurchaseRequest.requested_at.desc()).all()
        else:
            requests = PurchaseRequest.query.filter_by(status=status_filter).order_by(PurchaseRequest.requested_at.desc()).all()
        
        return render_template('admin/purchase_requests.html', 
                             requests=requests,
                             status_filter=status_filter)
    
    @app.route('/admin/purchase-requests/<int:request_id>/approve', methods=['POST'])
    @login_required
    def approve_request(request_id):
        """Approve purchase request"""
        if current_user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        purchase_request = PurchaseRequest.query.get_or_404(request_id)
        
        if not purchase_request.can_be_processed():
            return jsonify({'error': 'Request already processed'}), 400
        
        if not purchase_request.product.can_fulfill_quantity(purchase_request.quantity):
            return jsonify({'error': f'Insufficient stock. Available: {purchase_request.product.quantity}'}), 400
        
        # Update product stock
        purchase_request.product.quantity -= purchase_request.quantity
        
        # Update request
        purchase_request.status = PurchaseRequest.STATUS_APPROVED
        purchase_request.admin_id = current_user.id
        purchase_request.processed_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Purchase request #{purchase_request.id} approved successfully!', 'success')
        return redirect(url_for('admin_purchase_requests'))
    
    @app.route('/admin/purchase-requests/<int:request_id>/reject', methods=['POST'])
    @login_required
    def reject_request(request_id):
        """Reject purchase request"""
        if current_user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        purchase_request = PurchaseRequest.query.get_or_404(request_id)
        reason = request.form.get('reason', '')
        
        if not purchase_request.can_be_processed():
            return jsonify({'error': 'Request already processed'}), 400
        
        # Update request
        purchase_request.status = PurchaseRequest.STATUS_REJECTED
        purchase_request.admin_id = current_user.id
        purchase_request.rejection_reason = reason
        purchase_request.processed_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Purchase request #{purchase_request.id} rejected.', 'info')
        return redirect(url_for('admin_purchase_requests'))
    
    # API routes for AJAX
    @app.route('/api/products/<int:product_id>/quick-request', methods=['POST'])
    @login_required
    def quick_request_product(product_id):
        """API endpoint for quick purchase requests from product listing"""
        if current_user.role != 'customer':
            return jsonify({'error': 'Access denied'}), 403
        
        try:
            quantity = int(request.form.get('quantity', 1))
            
            if quantity <= 0:
                return jsonify({'error': 'Quantity must be greater than 0'}), 400
            
            product = Product.query.get_or_404(product_id)
            
            if quantity > product.quantity:
                return jsonify({'error': f'Only {product.quantity} units available'}), 400
            
            # Create purchase request
            purchase_request = PurchaseRequest(
                customer_id=current_user.id,
                product_id=product_id,
                quantity=quantity
            )
            
            db.session.add(purchase_request)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Request for {quantity} units of {product.name} submitted successfully!'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # Sample data creation route (for demo purposes)
    @app.route('/admin/create-sample-data')
    @login_required
    def create_sample_data():
        """Create sample products for demonstration"""
        if current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('customer_dashboard'))
        
        # Check if sample data already exists
        if Product.query.count() > 0:
            flash('Sample data already exists!', 'info')
            return redirect(url_for('admin_dashboard'))
        
        # Create sample products
        sample_products = [
            {
                'name': 'Laptop Computer',
                'description': 'High-performance laptop for business and gaming',
                'category': 'Electronics',
                'cost_price': 800.00,
                'selling_price': 1200.00,
                'quantity': 15,
                'low_stock_threshold': 5
            },
            {
                'name': 'Office Chair',
                'description': 'Ergonomic office chair with lumbar support',
                'category': 'Furniture',
                'cost_price': 150.00,
                'selling_price': 250.00,
                'quantity': 8,
                'low_stock_threshold': 3
            },
            {
                'name': 'Wireless Mouse',
                'description': 'Bluetooth wireless mouse with precision tracking',
                'category': 'Electronics',
                'cost_price': 25.00,
                'selling_price': 45.00,
                'quantity': 50,
                'low_stock_threshold': 10
            },
            {
                'name': 'Coffee Maker',
                'description': 'Automatic drip coffee maker with timer',
                'category': 'Appliances',
                'cost_price': 60.00,
                'selling_price': 99.99,
                'quantity': 12,
                'low_stock_threshold': 4
            },
            {
                'name': 'Notebook Set',
                'description': 'Set of 3 professional notebooks',
                'category': 'Stationery',
                'cost_price': 8.00,
                'selling_price': 15.99,
                'quantity': 100,
                'low_stock_threshold': 20
            }
        ]
        
        for product_data in sample_products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        flash('Sample products created successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    # Initialize database
    with app.app_context():
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
            admin.set_password('Admin123!')  # Change in production
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: admin@inventory.com / Admin123!")
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Smart Inventory System")
    print("📍 URL: http://localhost:8080")
    print("🔑 Admin: admin@inventory.com / Admin123!")
    app.run(debug=True, host='localhost', port=8080)