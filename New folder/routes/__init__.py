"""
Routes package for Smart Inventory Management System
"""

from .product_routes import product_bp
from .ai_routes import ai_bp
from .customer_routes import customer_bp

__all__ = ['product_bp', 'ai_bp', 'customer_bp']