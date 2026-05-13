"""
Utilities package for Smart Inventory Management System
"""

from .auth import role_required, admin_required, customer_required
from .database import init_database, create_sample_data

__all__ = ['role_required', 'admin_required', 'customer_required', 'init_database', 'create_sample_data']