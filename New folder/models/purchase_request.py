"""
Purchase Request model for customer purchase workflow
"""
from datetime import datetime
from extensions import db

class PurchaseRequest(db.Model):
    """Purchase request model for customer-admin workflow"""
    
    __tablename__ = 'purchase_requests'
    
    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    VALID_STATUSES = [STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED]
    
    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_PENDING, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    rejection_reason = db.Column(db.Text)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    processed_at = db.Column(db.DateTime)
    
    # Relationships are defined in User and Product models via backref
    
    def __init__(self, customer_id, product_id, quantity):
        """Initialize purchase request with validation"""
        self.customer_id = customer_id
        self.product_id = product_id
        self.quantity = self.validate_quantity(quantity)
        self.status = self.STATUS_PENDING
    
    @staticmethod
    def validate_quantity(quantity):
        """Validate requested quantity"""
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            raise ValueError("Quantity must be a valid integer")
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        
        if quantity > 1000:
            raise ValueError("Quantity cannot exceed 1000 per request")
        
        return quantity
    
    def can_be_processed(self):
        """Check if request can be processed (is still pending)"""
        return self.status == self.STATUS_PENDING
    
    def approve(self, admin_id):
        """Approve the purchase request and update inventory"""
        if not self.can_be_processed():
            raise ValueError("Request has already been processed")
        
        # Check if product has sufficient stock
        if not self.product.can_fulfill_quantity(self.quantity):
            raise ValueError(f"Insufficient stock. Available: {self.product.quantity}, Requested: {self.quantity}")
        
        # Update product stock
        self.product.reduce_stock(self.quantity)
        
        # Update request status
        self.status = self.STATUS_APPROVED
        self.admin_id = admin_id
        self.processed_at = datetime.utcnow()
        
        # Create sale record
        from .sale import Sale
        sale = Sale(
            purchase_request_id=self.id,
            product_id=self.product_id,
            customer_id=self.customer_id,
            quantity=self.quantity,
            unit_price=self.product.selling_price,
            total_amount=self.product.selling_price * self.quantity
        )
        db.session.add(sale)
        
        return sale
    
    def reject(self, admin_id, reason=None):
        """Reject the purchase request"""
        if not self.can_be_processed():
            raise ValueError("Request has already been processed")
        
        self.status = self.STATUS_REJECTED
        self.admin_id = admin_id
        self.rejection_reason = reason
        self.processed_at = datetime.utcnow()
    
    # Query methods
    @classmethod
    def get_pending_requests(cls):
        """Get all pending purchase requests"""
        return cls.query.filter_by(status=cls.STATUS_PENDING).order_by(cls.requested_at.asc()).all()
    
    @classmethod
    def get_requests_by_status(cls, status):
        """Get requests by status"""
        if status not in cls.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(cls.VALID_STATUSES)}")
        
        return cls.query.filter_by(status=status).order_by(cls.requested_at.desc())
    
    @classmethod
    def get_customer_requests(cls, customer_id):
        """Get all requests for a specific customer"""
        return cls.query.filter_by(customer_id=customer_id).order_by(cls.requested_at.desc())
    
    @classmethod
    def get_admin_processed_requests(cls, admin_id):
        """Get requests processed by a specific admin"""
        return cls.query.filter_by(admin_id=admin_id).order_by(cls.processed_at.desc())
    
    @classmethod
    def get_recent_requests(cls, days=7):
        """Get requests from the last N days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return cls.query.filter(cls.requested_at >= cutoff_date).order_by(cls.requested_at.desc())
    
    # Status checking methods
    def is_pending(self):
        """Check if request is pending"""
        return self.status == self.STATUS_PENDING
    
    def is_approved(self):
        """Check if request is approved"""
        return self.status == self.STATUS_APPROVED
    
    def is_rejected(self):
        """Check if request is rejected"""
        return self.status == self.STATUS_REJECTED
    
    # Calculated properties
    @property
    def total_value(self):
        """Calculate total value of the request"""
        return self.product.selling_price * self.quantity if self.product else 0
    
    @property
    def processing_time(self):
        """Calculate time taken to process the request"""
        if self.processed_at and self.requested_at:
            return self.processed_at - self.requested_at
        return None
    
    @property
    def days_pending(self):
        """Calculate days since request was made"""
        if self.is_pending():
            return (datetime.utcnow() - self.requested_at).days
        return None
    
    # String representation
    def __repr__(self):
        return f'<PurchaseRequest {self.id}: {self.quantity}x {self.product.name if self.product else "Unknown"} ({self.status})>'
    
    def to_dict(self):
        """Convert purchase request to dictionary"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else None,
            'customer_email': self.customer.email if self.customer else None,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'product_price': float(self.product.selling_price) if self.product else None,
            'quantity': self.quantity,
            'total_value': float(self.total_value),
            'status': self.status,
            'admin_id': self.admin_id,
            'admin_name': self.processed_by_admin.full_name if self.processed_by_admin else None,
            'rejection_reason': self.rejection_reason,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'days_pending': self.days_pending,
            'processing_time_hours': self.processing_time.total_seconds() / 3600 if self.processing_time else None
        }