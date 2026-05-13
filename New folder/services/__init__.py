"""
Services package for Smart Inventory Management System
"""
from .analytics_service import AnalyticsService
from .product_service import ProductService
from .calendar_service import CalendarService
from .ai_prediction_service import AIPredictionService
from .restocking_service import RestockingService
from .customer_service import CustomerService
from .alert_service import AlertService
from .notification_service import NotificationService

__all__ = ['AnalyticsService', 'ProductService', 'CalendarService', 'AIPredictionService', 'RestockingService', 'CustomerService', 'AlertService', 'NotificationService']