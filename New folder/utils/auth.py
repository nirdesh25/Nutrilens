"""
Authentication utilities for role-based access control
"""

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(role):
    """
    Decorator to require specific role for route access
    
    Args:
        role (str): Required role ('admin' or 'customer')
    
    Returns:
        decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role != role:
                flash('You do not have permission to access this page.', 'error')
                # Redirect to appropriate dashboard based on user's actual role
                if current_user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('customer_dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorator to require admin role for route access
    
    Args:
        f: Function to decorate
    
    Returns:
        decorated function
    """
    return role_required('admin')(f)

def customer_required(f):
    """
    Decorator to require customer role for route access
    
    Args:
        f: Function to decorate
    
    Returns:
        decorated function
    """
    return role_required('customer')(f)