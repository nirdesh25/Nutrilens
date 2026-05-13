"""
Database models for Smart Inventory Management System
"""
from .user import User
from .product import Product
from .purchase_request import PurchaseRequest
from .sale import Sale
from .ai_prediction import AIPrediction
from .alert import Alert
from .notification_preference import NotificationPreference

__all__ = ['User', 'Product', 'PurchaseRequest', 'Sale', 'AIPrediction', 'Alert', 'NotificationPreference']