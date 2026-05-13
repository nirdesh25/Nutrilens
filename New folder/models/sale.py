"""
Sale model for tracking completed transactions
"""
from datetime import datetime
from decimal import Decimal
from extensions import db

class Sale(db.Model):
    """Sale model for tracking completed purchase transactions"""
    
    __tablename__ = 'sales'
    
    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    purchase_request_id = db.Column(db.Integer, db.ForeignKey('purchase_requests.id'), nullable=False, unique=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    purchase_request = db.relationship('PurchaseRequest', backref='sale')
    customer = db.relationship('User', backref='sales')
    # product relationship defined in Product model
    
    def __init__(self, purchase_request_id, product_id, customer_id, quantity, unit_price, total_amount):
        """Initialize sale record"""
        self.purchase_request_id = purchase_request_id
        self.product_id = product_id
        self.customer_id = customer_id
        self.quantity = self.validate_quantity(quantity)
        self.unit_price = self.validate_price(unit_price)
        self.total_amount = self.validate_price(total_amount)
        
        # Validate that total_amount matches quantity * unit_price
        expected_total = Decimal(str(unit_price)) * quantity
        if abs(Decimal(str(total_amount)) - expected_total) > Decimal('0.01'):
            raise ValueError("Total amount does not match quantity × unit price")
    
    @staticmethod
    def validate_quantity(quantity):
        """Validate sale quantity"""
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            raise ValueError("Quantity must be a valid integer")
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        
        return quantity
    
    @staticmethod
    def validate_price(price):
        """Validate price values"""
        try:
            price = Decimal(str(price))
        except (ValueError, TypeError):
            raise ValueError("Price must be a valid number")
        
        if price < 0:
            raise ValueError("Price cannot be negative")
        
        return price
    
    # Query methods
    @classmethod
    def get_sales_by_date_range(cls, start_date, end_date):
        """Get sales within a date range"""
        return cls.query.filter(
            cls.sale_date >= start_date,
            cls.sale_date <= end_date
        ).order_by(cls.sale_date.desc()).all()
    
    @classmethod
    def get_sales_by_date(cls, date):
        """Get sales for a specific date"""
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        return cls.get_sales_by_date_range(start_of_day, end_of_day)
    
    @classmethod
    def get_customer_sales(cls, customer_id):
        """Get all sales for a specific customer"""
        return cls.query.filter_by(customer_id=customer_id).order_by(cls.sale_date.desc()).all()
    
    @classmethod
    def get_product_sales(cls, product_id):
        """Get all sales for a specific product"""
        return cls.query.filter_by(product_id=product_id).order_by(cls.sale_date.desc()).all()
    
    @classmethod
    def get_recent_sales(cls, days=30):
        """Get sales from the last N days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return cls.query.filter(cls.sale_date >= cutoff_date).order_by(cls.sale_date.desc()).all()
    
    @classmethod
    def get_top_selling_products(cls, limit=10, days=30):
        """Get top selling products by quantity"""
        from datetime import timedelta
        from sqlalchemy import func
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return db.session.query(
            cls.product_id,
            func.sum(cls.quantity).label('total_quantity'),
            func.sum(cls.total_amount).label('total_revenue')
        ).filter(
            cls.sale_date >= cutoff_date
        ).group_by(
            cls.product_id
        ).order_by(
            func.sum(cls.quantity).desc()
        ).limit(limit).all()
    
    @classmethod
    def get_sales_summary(cls, start_date=None, end_date=None):
        """Get sales summary statistics"""
        from sqlalchemy import func
        
        query = db.session.query(
            func.count(cls.id).label('total_sales'),
            func.sum(cls.quantity).label('total_quantity'),
            func.sum(cls.total_amount).label('total_revenue'),
            func.avg(cls.total_amount).label('average_sale_amount')
        )
        
        if start_date:
            query = query.filter(cls.sale_date >= start_date)
        if end_date:
            query = query.filter(cls.sale_date <= end_date)
        
        result = query.first()
        
        return {
            'total_sales': result.total_sales or 0,
            'total_quantity': result.total_quantity or 0,
            'total_revenue': float(result.total_revenue or 0),
            'average_sale_amount': float(result.average_sale_amount or 0)
        }
    
    @classmethod
    def get_daily_sales_data(cls, days=30):
        """Get daily sales data for charts"""
        from datetime import timedelta, date
        from sqlalchemy import func
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get sales grouped by date
        sales_data = db.session.query(
            func.date(cls.sale_date).label('sale_date'),
            func.count(cls.id).label('sales_count'),
            func.sum(cls.total_amount).label('daily_revenue')
        ).filter(
            cls.sale_date >= start_date
        ).group_by(
            func.date(cls.sale_date)
        ).order_by(
            func.date(cls.sale_date)
        ).all()
        
        # Create a complete date range with zero values for missing dates
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)
        
        # Convert to dictionary for easy lookup
        sales_dict = {row.sale_date: row for row in sales_data}
        
        # Build complete dataset
        complete_data = []
        for date_item in date_range:
            if date_item in sales_dict:
                row = sales_dict[date_item]
                complete_data.append({
                    'date': date_item.isoformat(),
                    'sales_count': row.sales_count,
                    'revenue': float(row.daily_revenue)
                })
            else:
                complete_data.append({
                    'date': date_item.isoformat(),
                    'sales_count': 0,
                    'revenue': 0.0
                })
        
        return complete_data
    
    # Calculated properties
    @property
    def profit(self):
        """Calculate profit for this sale"""
        if self.product:
            return (self.unit_price - self.product.cost_price) * self.quantity
        return Decimal('0')
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.unit_price == 0:
            return Decimal('0')
        return (self.profit / self.total_amount) * 100
    
    # String representation
    def __repr__(self):
        return f'<Sale {self.id}: {self.quantity}x {self.product.name if self.product else "Unknown"} = ${self.total_amount}>'
    
    def to_dict(self):
        """Convert sale to dictionary"""
        return {
            'id': self.id,
            'purchase_request_id': self.purchase_request_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_amount': float(self.total_amount),
            'profit': float(self.profit),
            'profit_margin': float(self.profit_margin),
            'sale_date': self.sale_date.isoformat() if self.sale_date else None
        }