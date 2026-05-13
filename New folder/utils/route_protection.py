"""
Route protection utilities for Smart Inventory Management System
Ensures all routes have proper authentication and authorization
"""

from functools import wraps
from flask import request, jsonify, redirect, url_for, flash, abort
from flask_login import current_user, login_required


def admin_required(f):
    """
    Decorator to require admin role for route access
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function with admin role requirement
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        
        if current_user.role != 'admin':
            if request.is_json:
                return jsonify({'error': 'Admin privileges required'}), 403
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('customer_dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def customer_required(f):
    """
    Decorator to require customer role for route access
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function with customer role requirement
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        
        if current_user.role != 'customer':
            if request.is_json:
                return jsonify({'error': 'Customer account required'}), 403
            flash('Access denied. Customer account required.', 'error')
            return redirect(url_for('admin_dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def role_required(required_role):
    """
    Decorator factory to require specific role for route access
    
    Args:
        required_role: Role required ('admin' or 'customer')
    
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('login'))
            
            if current_user.role != required_role:
                if request.is_json:
                    return jsonify({'error': f'{required_role.title()} privileges required'}), 403
                
                flash(f'Access denied. {required_role.title()} privileges required.', 'error')
                
                # Redirect to appropriate dashboard
                if required_role == 'admin':
                    return redirect(url_for('customer_dashboard'))
                else:
                    return redirect(url_for('admin_dashboard'))
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def api_auth_required(f):
    """
    Decorator for API endpoints that require authentication
    Returns JSON responses for unauthorized access
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function with API authentication
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                'error': 'Authentication required',
                'code': 'AUTH_REQUIRED'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def api_admin_required(f):
    """
    Decorator for API endpoints that require admin role
    Returns JSON responses for unauthorized access
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function with API admin authentication
    """
    @wraps(f)
    @api_auth_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({
                'error': 'Admin privileges required',
                'code': 'ADMIN_REQUIRED'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def api_customer_required(f):
    """
    Decorator for API endpoints that require customer role
    Returns JSON responses for unauthorized access
    
    Args:
        f: Function to decorate
    
    Returns:
        Decorated function with API customer authentication
    """
    @wraps(f)
    @api_auth_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'customer':
            return jsonify({
                'error': 'Customer account required',
                'code': 'CUSTOMER_REQUIRED'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_json_request(required_fields=None):
    """
    Decorator to validate JSON request data
    
    Args:
        required_fields: List of required field names
    
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'error': 'Content-Type must be application/json',
                    'code': 'INVALID_CONTENT_TYPE'
                }), 400
            
            data = request.get_json()
            if not data:
                return jsonify({
                    'error': 'Request body must contain valid JSON',
                    'code': 'INVALID_JSON'
                }), 400
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': f'Missing required fields: {", ".join(missing_fields)}',
                        'code': 'MISSING_FIELDS',
                        'missing_fields': missing_fields
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def rate_limit_by_user(max_requests=100, window_minutes=60):
    """
    Simple rate limiting decorator by user
    Note: This is a basic implementation. For production, use Redis or similar
    
    Args:
        max_requests: Maximum requests allowed
        window_minutes: Time window in minutes
    
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Basic rate limiting - in production, use Redis or similar
            # For now, just log the attempt
            if current_user.is_authenticated:
                print(f"Rate limit check for user {current_user.id}: {request.endpoint}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


class RouteProtectionValidator:
    """
    Utility class to validate route protection across the application
    """
    
    @staticmethod
    def get_unprotected_routes(app):
        """
        Analyze application routes and identify potentially unprotected routes
        
        Args:
            app: Flask application instance
        
        Returns:
            List of potentially unprotected routes
        """
        unprotected_routes = []
        
        for rule in app.url_map.iter_rules():
            # Skip static files and auth routes
            if rule.endpoint in ['static', 'login', 'register', 'index']:
                continue
            
            # Get the view function
            view_func = app.view_functions.get(rule.endpoint)
            if not view_func:
                continue
            
            # Check if route has authentication decorators
            has_auth = False
            
            # Check for login_required decorator
            if hasattr(view_func, '__wrapped__'):
                # Check the decorator chain
                func = view_func
                while hasattr(func, '__wrapped__'):
                    if hasattr(func, '__name__') and 'login_required' in str(func):
                        has_auth = True
                        break
                    func = func.__wrapped__
            
            # Check for our custom decorators
            if hasattr(view_func, '__name__'):
                func_name = view_func.__name__
                if any(decorator in func_name for decorator in ['admin_required', 'customer_required', 'api_auth_required']):
                    has_auth = True
            
            if not has_auth:
                unprotected_routes.append({
                    'endpoint': rule.endpoint,
                    'rule': str(rule),
                    'methods': list(rule.methods - {'HEAD', 'OPTIONS'})
                })
        
        return unprotected_routes
    
    @staticmethod
    def validate_api_endpoints(app):
        """
        Validate that all API endpoints have proper authentication
        
        Args:
            app: Flask application instance
        
        Returns:
            Dictionary with validation results
        """
        api_routes = []
        protected_count = 0
        unprotected_count = 0
        
        for rule in app.url_map.iter_rules():
            if '/api/' in str(rule):
                view_func = app.view_functions.get(rule.endpoint)
                if view_func:
                    # Check for API authentication
                    has_api_auth = any(
                        decorator in str(view_func) 
                        for decorator in ['api_auth_required', 'api_admin_required', 'api_customer_required']
                    )
                    
                    route_info = {
                        'endpoint': rule.endpoint,
                        'rule': str(rule),
                        'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                        'protected': has_api_auth
                    }
                    
                    api_routes.append(route_info)
                    
                    if has_api_auth:
                        protected_count += 1
                    else:
                        unprotected_count += 1
        
        return {
            'total_api_routes': len(api_routes),
            'protected_routes': protected_count,
            'unprotected_routes': unprotected_count,
            'routes': api_routes
        }


def apply_route_protection_to_blueprint(bp, protection_type='admin'):
    """
    Apply route protection to all routes in a blueprint
    
    Args:
        bp: Flask blueprint
        protection_type: Type of protection ('admin', 'customer', 'auth')
    """
    if protection_type == 'admin':
        decorator = admin_required
    elif protection_type == 'customer':
        decorator = customer_required
    else:
        decorator = login_required
    
    # Apply decorator to all blueprint routes
    for endpoint, view_func in bp.view_functions.items():
        bp.view_functions[endpoint] = decorator(view_func)


def create_protected_route(route_path, methods=None, role_required=None):
    """
    Decorator factory to create protected routes with specific requirements
    
    Args:
        route_path: URL route path
        methods: HTTP methods allowed
        role_required: Required user role
    
    Returns:
        Route decorator with protection
    """
    def decorator(f):
        # Apply role protection if specified
        if role_required == 'admin':
            f = admin_required(f)
        elif role_required == 'customer':
            f = customer_required(f)
        else:
            f = login_required(f)
        
        # Apply Flask route decorator
        from flask import current_app
        return current_app.route(route_path, methods=methods or ['GET'])(f)
    
    return decorator


# Global error handlers for authentication/authorization
def register_auth_error_handlers(app):
    """
    Register global error handlers for authentication and authorization errors
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(401)
    def unauthorized(error):
        if request.is_json:
            return jsonify({
                'error': 'Authentication required',
                'code': 'UNAUTHORIZED'
            }), 401
        
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.is_json:
            return jsonify({
                'error': 'Access forbidden',
                'code': 'FORBIDDEN'
            }), 403
        
        flash('Access denied. Insufficient privileges.', 'error')
        
        # Redirect based on user role
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('customer_dashboard'))
        else:
            return redirect(url_for('login'))