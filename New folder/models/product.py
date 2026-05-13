"""
Product model for inventory management
"""
from datetime import datetime
from decimal import Decimal
from extensions import db

class Product(db.Model):
    """Product model for inventory items"""
    
    __tablename__ = 'products'
    
    # Database columns
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
    
    # Relationships
    purchase_requests = db.relationship('PurchaseRequest', backref='product', lazy='dynamic')
    sales = db.relationship('Sale', backref='product', lazy='dynamic')
    ai_predictions = db.relationship('AIPrediction', backref='product', lazy='dynamic')
    
    def __init__(self, name, category, cost_price, selling_price, quantity=0, 
                 description=None, low_stock_threshold=10):
        """Initialize product with validation"""
        self.name = self.validate_name(name)
        self.category = self.validate_category(category)
        self.cost_price = self.validate_price(cost_price, "Cost price")
        self.selling_price = self.validate_price(selling_price, "Selling price")
        self.quantity = self.validate_quantity(quantity)
        self.description = description
        self.low_stock_threshold = max(0, int(low_stock_threshold or 10))
        
        # Validate that selling price is not less than cost price
        if self.selling_price < self.cost_price:
            raise ValueError("Selling price cannot be less than cost price")
    
    # Validation methods
    @staticmethod
    def validate_name(name):
        """Validate product name"""
        if not name or not isinstance(name, str):
            raise ValueError("Product name is required")
        
        name = name.strip()
        
        if len(name) < 2:
            raise ValueError("Product name must be at least 2 characters long")
        
        if len(name) > 200:
            raise ValueError("Product name is too long (maximum 200 characters)")
        
        return name
    
    @staticmethod
    def validate_category(category):
        """Validate product category"""
        if not category or not isinstance(category, str):
            raise ValueError("Product category is required")
        
        category = category.strip()
        
        if len(category) < 2:
            raise ValueError("Category must be at least 2 characters long")
        
        if len(category) > 100:
            raise ValueError("Category is too long (maximum 100 characters)")
        
        return category.title()
    
    @staticmethod
    def validate_price(price, field_name="Price"):
        """Validate price values"""
        try:
            price = Decimal(str(price))
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} must be a valid number")
        
        if price < 0:
            raise ValueError(f"{field_name} cannot be negative")
        
        if price > Decimal('999999.99'):
            raise ValueError(f"{field_name} is too large (maximum $999,999.99)")
        
        return price
    
    @staticmethod
    def validate_quantity(quantity):
        """Validate quantity"""
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            raise ValueError("Quantity must be a valid integer")
        
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        if quantity > 1000000:
            raise ValueError("Quantity is too large (maximum 1,000,000)")
        
        return quantity
    
    # Stock management methods
    def is_low_stock(self):
        """Check if product is low on stock"""
        return self.quantity <= self.low_stock_threshold
    
    def is_out_of_stock(self):
        """Check if product is out of stock"""
        return self.quantity <= 0
    
    def can_fulfill_quantity(self, requested_quantity):
        """Check if we have enough stock for requested quantity"""
        return self.quantity >= requested_quantity
    
    def reduce_stock(self, quantity):
        """Reduce stock by specified quantity"""
        if not self.can_fulfill_quantity(quantity):
            raise ValueError(f"Insufficient stock. Available: {self.quantity}, Requested: {quantity}")
        
        self.quantity -= quantity
        self.updated_at = datetime.utcnow()
        return self.quantity
    
    def increase_stock(self, quantity):
        """Increase stock by specified quantity"""
        if quantity <= 0:
            raise ValueError("Quantity to add must be positive")
        
        self.quantity += quantity
        self.updated_at = datetime.utcnow()
        return self.quantity
    
    def update_stock(self, new_quantity):
        """Update stock to specific quantity"""
        self.quantity = self.validate_quantity(new_quantity)
        self.updated_at = datetime.utcnow()
        return self.quantity
    
    # Financial calculations
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price == 0:
            return Decimal('0')
        return ((self.selling_price - self.cost_price) / self.cost_price) * 100
    
    @property
    def profit_per_unit(self):
        """Calculate profit per unit"""
        return self.selling_price - self.cost_price
    
    @property
    def total_value(self):
        """Calculate total inventory value at cost price"""
        return self.cost_price * self.quantity
    
    @property
    def total_selling_value(self):
        """Calculate total inventory value at selling price"""
        return self.selling_price * self.quantity
    
    # Query methods
    @classmethod
    def get_active_products(cls):
        """Get all active products"""
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def get_low_stock_products(cls):
        """Get products with low stock"""
        return cls.query.filter(
            cls.is_active == True,
            cls.quantity <= cls.low_stock_threshold
        ).all()
    
    @classmethod
    def get_out_of_stock_products(cls):
        """Get products that are out of stock"""
        return cls.query.filter(
            cls.is_active == True,
            cls.quantity <= 0
        ).all()
    
    @classmethod
    def search_products(cls, search_term):
        """Search products by name or category"""
        if not search_term:
            return cls.get_active_products()
        
        search_term = f"%{search_term.strip()}%"
        return cls.query.filter(
            cls.is_active == True,
            (cls.name.ilike(search_term) | cls.category.ilike(search_term))
        ).all()
    
    @classmethod
    def get_products_by_category(cls, category):
        """Get products by category"""
        return cls.query.filter_by(category=category, is_active=True).all()
    
    @classmethod
    def get_categories(cls):
        """Get all unique categories"""
        return db.session.query(cls.category).filter_by(is_active=True).distinct().all()
    
    # Update methods
    def update_details(self, name=None, description=None, category=None, 
                      cost_price=None, selling_price=None, low_stock_threshold=None):
        """Update product details"""
        if name is not None:
            self.name = self.validate_name(name)
        
        if description is not None:
            self.description = description
        
        if category is not None:
            self.category = self.validate_category(category)
        
        if cost_price is not None:
            self.cost_price = self.validate_price(cost_price, "Cost price")
        
        if selling_price is not None:
            self.selling_price = self.validate_price(selling_price, "Selling price")
        
        if low_stock_threshold is not None:
            self.low_stock_threshold = max(0, int(low_stock_threshold))
        
        # Validate price relationship
        if self.selling_price < self.cost_price:
            raise ValueError("Selling price cannot be less than cost price")
        
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate product (soft delete)"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self):
        """Activate product"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    # String representation
    def __repr__(self):
        return f'<Product {self.name} (${self.selling_price})>'
    
    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'cost_price': float(self.cost_price),
            'selling_price': float(self.selling_price),
            'quantity': self.quantity,
            'low_stock_threshold': self.low_stock_threshold,
            'is_low_stock': self.is_low_stock(),
            'is_out_of_stock': self.is_out_of_stock(),
            'profit_margin': float(self.profit_margin),
            'profit_per_unit': float(self.profit_per_unit),
            'total_value': float(self.total_value),
            'total_selling_value': float(self.total_selling_value),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }