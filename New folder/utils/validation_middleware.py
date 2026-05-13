"""
Validation middleware for Smart Inventory Management System
Provides request-level validation and sanitization
"""

import re
import json
from functools import wraps
from typing import Dict, Any, List, Optional
from flask import request, jsonify, current_app
from utils.error_handling import ValidationError, SecurityValidator, InputValidator


class RequestValidationMiddleware:
    """Middleware for validating and sanitizing requests"""
    
    # Common validation patterns
    PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'phone': r'^\+?1?-?\.?\s?\(?(\d{3})\)?[\s\-\.]?(\d{3})[\s\-\.]?(\d{4})$',
        'alphanumeric': r'^[a-zA-Z0-9\s]+$',
        'numeric': r'^\d+$',
        'decimal': r'^\d+\.?\d*$',
        'name': r"^[a-zA-Z\s\-']+$",
        'category': r'^[a-zA-Z0-9\s\-_]+$'
    }
    
    # SQL injection patterns to detect
    SQL_INJECTION_PATTERNS = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)',
        r'(--|#|/\*|\*/)',
        r'(\bOR\b.*=.*\bOR\b)',
        r'(\bAND\b.*=.*\bAND\b)',
        r'(\'.*\')',
        r'(;.*)',
        r'(\bxp_\w+)',
        r'(\bsp_\w+)'
    ]
    
    # XSS patterns to detect
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>'
    ]
    
    @classmethod
    def validate_request_size(cls, max_size: int = 16 * 1024 * 1024):
        """Validate request content length"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if request.content_length and request.content_length > max_size:
                    raise ValidationError(f"Request too large. Maximum size: {max_size} bytes")
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @classmethod
    def validate_content_type(cls, allowed_types: List[str]):
        """Validate request content type"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if request.content_type not in allowed_types:
                    raise ValidationError(f"Invalid content type. Allowed: {', '.join(allowed_types)}")
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @classmethod
    def sanitize_json_input(cls, f):
        """Sanitize JSON input data"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                try:
                    data = request.get_json()
                    if data:
                        sanitized_data = cls._sanitize_dict(data)
                        # Replace request data with sanitized version
                        request._cached_json = (sanitized_data, True)
                except Exception as e:
                    raise ValidationError(f"Invalid JSON data: {str(e)}")
            
            return f(*args, **kwargs)
        return decorated_function
    
    @classmethod
    def sanitize_form_input(cls, f):
        """Sanitize form input data"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.form:
                # Create sanitized form data
                sanitized_form = {}
                for key, value in request.form.items():
                    sanitized_form[key] = cls._sanitize_string(value)
                
                # Store original form and replace with sanitized version
                request._original_form = request.form
                request.form = sanitized_form
            
            return f(*args, **kwargs)
        return decorated_function
    
    @classmethod
    def validate_rate_limit(cls, max_requests: int = 100, window_seconds: int = 3600):
        """Basic rate limiting validation"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # In production, implement proper rate limiting with Redis
                # For now, just log the request
                if current_app.debug:
                    current_app.logger.info(f"Rate limit check: {request.remote_addr} - {request.endpoint}")
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @classmethod
    def validate_csrf_token(cls, f):
        """Validate CSRF token for state-changing operations"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                # Flask-WTF handles CSRF validation automatically for forms
                # For API endpoints, implement custom CSRF validation if needed
                pass
            
            return f(*args, **kwargs)
        return decorated_function
    
    @classmethod
    def _sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary data"""
        sanitized = {}
        
        for key, value in data.items():
            sanitized_key = cls._sanitize_string(str(key))
            
            if isinstance(value, dict):
                sanitized[sanitized_key] = cls._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[sanitized_key] = [
                    cls._sanitize_dict(item) if isinstance(item, dict)
                    else cls._sanitize_string(str(item)) if isinstance(item, str)
                    else item
                    for item in value
                ]
            elif isinstance(value, str):
                sanitized[sanitized_key] = cls._sanitize_string(value)
            else:
                sanitized[sanitized_key] = value
        
        return sanitized
    
    @classmethod
    def _sanitize_string(cls, value: str) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return value
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Check for SQL injection attempts
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                try:
                    current_app.logger.warning(f"Potential SQL injection attempt: {value}")
                except RuntimeError:
                    # Outside application context, just print
                    print(f"Warning: Potential SQL injection attempt: {value}")
                # Don't raise error, just sanitize
                value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        # Check for XSS attempts
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
                try:
                    current_app.logger.warning(f"Potential XSS attempt: {value}")
                except RuntimeError:
                    # Outside application context, just print
                    print(f"Warning: Potential XSS attempt: {value}")
                value = re.sub(pattern, '', value, flags=re.IGNORECASE | re.DOTALL)
        
        # Basic HTML entity encoding for safety
        value = value.replace('<', '&lt;').replace('>', '&gt;')
        value = value.replace('"', '&quot;').replace("'", '&#x27;')
        
        return value.strip()
    
    @classmethod
    def validate_field_pattern(cls, field_name: str, pattern_name: str):
        """Validate field against predefined pattern"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if pattern_name not in cls.PATTERNS:
                    raise ValidationError(f"Unknown validation pattern: {pattern_name}")
                
                pattern = cls.PATTERNS[pattern_name]
                
                # Check in JSON data
                if request.is_json:
                    data = request.get_json()
                    if data and field_name in data:
                        value = data[field_name]
                        if isinstance(value, str) and not re.match(pattern, value):
                            raise ValidationError(f"Invalid format for {field_name}")
                
                # Check in form data
                if request.form and field_name in request.form:
                    value = request.form[field_name]
                    if not re.match(pattern, value):
                        raise ValidationError(f"Invalid format for {field_name}")
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator


class BusinessRuleValidator:
    """Validator for business-specific rules"""
    
    @staticmethod
    def validate_product_business_rules(product_data: Dict[str, Any]):
        """Validate product-specific business rules"""
        # Selling price should not be less than cost price
        if 'cost_price' in product_data and 'selling_price' in product_data:
            if product_data['selling_price'] < product_data['cost_price']:
                raise ValidationError("Selling price cannot be less than cost price")
        
        # Quantity should be reasonable
        if 'quantity' in product_data:
            if product_data['quantity'] < 0:
                raise ValidationError("Quantity cannot be negative")
            if product_data['quantity'] > 1000000:
                raise ValidationError("Quantity exceeds maximum allowed limit")
        
        # Low stock threshold should be reasonable
        if 'low_stock_threshold' in product_data:
            if product_data['low_stock_threshold'] < 0:
                raise ValidationError("Low stock threshold cannot be negative")
            if product_data['low_stock_threshold'] > 10000:
                raise ValidationError("Low stock threshold is too high")
    
    @staticmethod
    def validate_purchase_request_business_rules(request_data: Dict[str, Any]):
        """Validate purchase request business rules"""
        # Quantity should be reasonable for a single request
        if 'quantity' in request_data:
            if request_data['quantity'] <= 0:
                raise ValidationError("Quantity must be greater than 0")
            if request_data['quantity'] > 1000:
                raise ValidationError("Quantity per request cannot exceed 1000")
    
    @staticmethod
    def validate_user_business_rules(user_data: Dict[str, Any]):
        """Validate user-specific business rules"""
        # Email domain restrictions (if any)
        if 'email' in user_data:
            email = user_data['email'].lower()
            
            # Block common disposable email domains
            disposable_domains = [
                '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
                'mailinator.com', 'throwaway.email'
            ]
            
            domain = email.split('@')[1] if '@' in email else ''
            if domain in disposable_domains:
                raise ValidationError("Disposable email addresses are not allowed")
        
        # Role validation
        if 'role' in user_data:
            valid_roles = ['customer', 'admin']
            if user_data['role'] not in valid_roles:
                raise ValidationError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")


def apply_validation_middleware(app):
    """Apply validation middleware to Flask app"""
    
    @app.before_request
    def validate_request():
        """Global request validation"""
        # Skip validation for static files
        if request.endpoint == 'static':
            return
        
        # Validate request size
        max_size = app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        if request.content_length and request.content_length > max_size:
            raise ValidationError(f"Request too large. Maximum size: {max_size} bytes")
        
        # Log suspicious requests
        try:
            if current_app.debug:
                suspicious_patterns = ['../', '..\\', 'etc/passwd', 'cmd.exe', 'powershell']
                request_str = str(request.url) + str(request.data)
                
                for pattern in suspicious_patterns:
                    if pattern in request_str.lower():
                        current_app.logger.warning(f"Suspicious request pattern detected: {pattern}")
        except RuntimeError:
            # Outside application context, skip logging
            pass
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (basic)
        if not current_app.debug:
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data:; "
                "font-src 'self' https://cdn.jsdelivr.net;"
            )
        
        return response