"""
Alert model for inventory management notifications
"""
from datetime import datetime
from enum import Enum
from extensions import db


class AlertType(Enum):
    """Alert type enumeration"""
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    CRITICAL_STOCK = "critical_stock"
    RESTOCK_SUGGESTION = "restock_suggestion"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status enumeration"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class Alert(db.Model):
    """Alert model for system notifications"""
    
    __tablename__ = 'alerts'
    
    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.Enum(AlertType), nullable=False, index=True)
    severity = db.Column(db.Enum(AlertSeverity), nullable=False, index=True)
    status = db.Column(db.Enum(AlertStatus), default=AlertStatus.ACTIVE, index=True)
    
    # Alert content
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Related entities
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # Alert data (JSON for flexible storage)
    alert_data = db.Column(db.JSON, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    product = db.relationship('Product', backref='alerts', lazy='select')
    user = db.relationship('User', backref='alerts', lazy='select')
    
    def __init__(self, alert_type, severity, title, message, product_id=None, 
                 user_id=None, alert_data=None):
        """Initialize alert"""
        self.alert_type = alert_type
        self.severity = severity
        self.title = title
        self.message = message
        self.product_id = product_id
        self.user_id = user_id
        self.alert_data = alert_data or {}
        self.status = AlertStatus.ACTIVE
    
    def acknowledge(self, user_id=None):
        """Mark alert as acknowledged"""
        if self.status == AlertStatus.ACTIVE:
            self.status = AlertStatus.ACKNOWLEDGED
            self.acknowledged_at = datetime.utcnow()
            if user_id:
                self.alert_data = self.alert_data or {}
                self.alert_data['acknowledged_by'] = user_id
    
    def resolve(self, user_id=None):
        """Mark alert as resolved"""
        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.utcnow()
        if user_id:
            self.alert_data = self.alert_data or {}
            self.alert_data['resolved_by'] = user_id
    
    def dismiss(self, user_id=None):
        """Dismiss alert"""
        self.status = AlertStatus.DISMISSED
        if user_id:
            self.alert_data = self.alert_data or {}
            self.alert_data['dismissed_by'] = user_id
    
    @property
    def is_active(self):
        """Check if alert is active"""
        return self.status == AlertStatus.ACTIVE
    
    @property
    def age_in_hours(self):
        """Get alert age in hours"""
        return (datetime.utcnow() - self.created_at).total_seconds() / 3600
    
    @classmethod
    def get_active_alerts(cls, alert_type=None, severity=None):
        """Get active alerts with optional filtering"""
        query = cls.query.filter_by(status=AlertStatus.ACTIVE)
        
        if alert_type:
            query = query.filter_by(alert_type=alert_type)
        
        if severity:
            query = query.filter_by(severity=severity)
        
        return query.order_by(cls.severity.desc(), cls.created_at.desc()).all()
    
    @classmethod
    def get_product_alerts(cls, product_id, status=None):
        """Get alerts for a specific product"""
        query = cls.query.filter_by(product_id=product_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_recent_alerts(cls, hours=24, limit=50):
        """Get recent alerts within specified hours"""
        cutoff_time = datetime.utcnow() - datetime.timedelta(hours=hours)
        
        return cls.query.filter(
            cls.created_at >= cutoff_time
        ).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def cleanup_old_resolved_alerts(cls, days=30):
        """Clean up old resolved alerts"""
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)
        
        old_alerts = cls.query.filter(
            cls.status.in_([AlertStatus.RESOLVED, AlertStatus.DISMISSED]),
            cls.created_at < cutoff_date
        ).all()
        
        for alert in old_alerts:
            db.session.delete(alert)
        
        return len(old_alerts)
    
    def to_dict(self):
        """Convert alert to dictionary"""
        return {
            'id': self.id,
            'alert_type': self.alert_type.value,
            'severity': self.severity.value,
            'status': self.status.value,
            'title': self.title,
            'message': self.message,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'user_id': self.user_id,
            'alert_data': self.alert_data,
            'created_at': self.created_at.isoformat(),
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'age_in_hours': self.age_in_hours,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<Alert {self.alert_type.value}: {self.title}>'