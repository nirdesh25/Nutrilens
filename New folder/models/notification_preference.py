"""
Notification Preference model for user notification settings
"""
from datetime import datetime
from extensions import db


class NotificationPreference(db.Model):
    """Model for storing user notification preferences"""
    
    __tablename__ = 'notification_preferences'
    
    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    
    # Email notification preferences
    email_notifications = db.Column(db.Boolean, default=True)
    low_stock_alerts = db.Column(db.Boolean, default=True)
    out_of_stock_alerts = db.Column(db.Boolean, default=True)
    daily_summary = db.Column(db.Boolean, default=True)
    weekly_summary = db.Column(db.Boolean, default=False)
    
    # In-app notification preferences
    in_app_notifications = db.Column(db.Boolean, default=True)
    browser_notifications = db.Column(db.Boolean, default=False)
    
    # Notification timing preferences
    daily_summary_time = db.Column(db.String(5), default='09:00')  # HH:MM format
    weekly_summary_day = db.Column(db.Integer, default=1)  # 1=Monday, 7=Sunday
    
    # Alert thresholds
    min_alert_severity = db.Column(db.String(20), default='warning')  # info, warning, critical
    alert_frequency_limit = db.Column(db.Integer, default=3)  # Max alerts per product per day
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notification_preference', lazy='select')
    
    def __init__(self, user_id, **kwargs):
        """Initialize notification preferences with defaults"""
        self.user_id = user_id
        
        # Set any provided preferences
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def get_or_create_for_user(cls, user_id):
        """Get existing preferences or create default ones for a user"""
        preferences = cls.query.filter_by(user_id=user_id).first()
        
        if not preferences:
            preferences = cls(user_id=user_id)
            db.session.add(preferences)
            db.session.commit()
        
        return preferences
    
    def update_preferences(self, **kwargs):
        """Update notification preferences"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'user_id', 'created_at']:
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def should_send_email_alert(self, alert_type, severity):
        """Check if email alert should be sent based on preferences"""
        if not self.email_notifications:
            return False
        
        # Check severity threshold
        severity_levels = {'info': 1, 'warning': 2, 'critical': 3}
        min_level = severity_levels.get(self.min_alert_severity, 2)
        alert_level = severity_levels.get(severity, 2)
        
        if alert_level < min_level:
            return False
        
        # Check specific alert type preferences
        if alert_type == 'low_stock' and not self.low_stock_alerts:
            return False
        
        if alert_type in ['out_of_stock', 'critical_stock'] and not self.out_of_stock_alerts:
            return False
        
        return True
    
    def should_send_in_app_notification(self, severity):
        """Check if in-app notification should be sent"""
        if not self.in_app_notifications:
            return False
        
        # Check severity threshold
        severity_levels = {'info': 1, 'warning': 2, 'critical': 3}
        min_level = severity_levels.get(self.min_alert_severity, 2)
        alert_level = severity_levels.get(severity, 2)
        
        return alert_level >= min_level
    
    def to_dict(self):
        """Convert preferences to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email_notifications': self.email_notifications,
            'low_stock_alerts': self.low_stock_alerts,
            'out_of_stock_alerts': self.out_of_stock_alerts,
            'daily_summary': self.daily_summary,
            'weekly_summary': self.weekly_summary,
            'in_app_notifications': self.in_app_notifications,
            'browser_notifications': self.browser_notifications,
            'daily_summary_time': self.daily_summary_time,
            'weekly_summary_day': self.weekly_summary_day,
            'min_alert_severity': self.min_alert_severity,
            'alert_frequency_limit': self.alert_frequency_limit,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<NotificationPreference user_id={self.user_id}>'