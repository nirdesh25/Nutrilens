"""
Centralized error handling utilities for Smart Inventory Management System
Provides consistent error responses, logging, and validation
"""

import logging
import traceback
from functools import wraps
from typing import Dict, Any, Optional, List
from flask import request, jsonify, flash, redirect, url_for, current_app
from flask_login import current_user
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from extensions import db


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code or 'VALIDATION_ERROR'
        super().__init__(self.message)


class BusinessLogicError(Exception):
    """Custom exception for business logic errors"""
    
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or 'BUSINESS_LOGIC_ERROR'
        super().__init__(self.message)


class AuthorizationError(Exception):
    """Custom exception for authorization errors"""
    
    def __init__(self, message: str = "Access denied", code: str = None):
        self.message = message
        self.code = code or 'AUTHORIZATION_ERROR'
        super().__init__(self.message)


class ErrorHandler:
    """Centralized error handling class"""
    
    @staticmethod
    def log_error(error: Exception, context: Dict[str, Any] = None):
        """Log error with context information"""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'user_id': current_user.id if current_user.is_authenticated else None,
            'endpoint': request.endpoint if request else None,
            'method': request.method if request else None,
            'url': request.url if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None,
            'ip_address': request.remote_addr if request else None
        }
        
        if context:
            error_info.update(context)
        
        logger.error(f"Application Error: {error_info}")
        
        # Log full traceback for debugging
        if current_app.debug:
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    @staticmethod
    def create_error_response(error: Exception, status_code: int = 500) -> Dict[str, Any]:
        """Create standardized error response"""
        error_response = {
            'error': {
                'message': str(error),
                'type': type(error).__name__,
                'timestamp': request.environ.get('REQUEST_TIME', ''),
                'request_id': getattr(request, 'id', None)
            }
        }
        
        # Add specific error codes for custom exceptions
        if hasattr(error, 'code'):
            error_response['error']['code'] = error.code
        
        if hasattr(error, 'field'):
            error_response['error']['field'] = error.field
        
        return error_response
    
    @staticmethod
    def handle_validation_error(error: ValidationError) -> tuple:
        """Handle validation errors"""
        ErrorHandler.log_error(error)
        
        if request.is_json:
            return jsonify(ErrorHandler.create_error_response(error)), 400
        else:
            flash(error.message, 'error')
            return redirect(request.referrer or url_for('index'))
    
    @staticmethod
    def handle_business_logic_error(error: BusinessLogicError) -> tuple:
        """Handle business logic errors"""
        ErrorHandler.log_error(error)
        
        if request.is_json:
            return jsonify(ErrorHandler.create_error_response(error)), 422
        else:
            flash(error.message, 'error')
            return redirect(request.referrer or url_for('index'))
    
    @staticmethod
    def handle_authorization_error(error: AuthorizationError) -> tuple:
        """Handle authorization errors"""
        ErrorHandler.log_error(error)
        
        if request.is_json:
            return jsonify(ErrorHandler.create_error_response(error)), 403
        else:
            flash(error.message, 'error')
            if current_user.is_authenticated:
                if current_user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('customer_dashboard'))
            else:
                return redirect(url_for('login'))
    
    @staticmethod
    def handle_database_error(error: SQLAlchemyError) -> tuple:
        """Handle database errors"""
        db.session.rollback()
        ErrorHandler.log_error(error)
        
        # Provide user-friendly messages for common database errors
        if isinstance(error, IntegrityError):
            message = "Data integrity error. Please check your input and try again."
        else:
            message = "Database error occurred. Please try again later."
        
        if request.is_json:
            return jsonify({
                'error': {
                    'message': message,
                    'type': 'DatabaseError',
                    'code': 'DATABASE_ERROR'
                }
            }), 500
        else:
            flash(message, 'error')
            return redirect(request.referrer or url_for('index'))


def handle_errors(f):
    """Decorator to handle errors in route functions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return ErrorHandler.handle_validation_error(e)
        except BusinessLogicError as e:
            return ErrorHandler.handle_business_logic_error(e)
        except AuthorizationError as e:
            return ErrorHandler.handle_authorization_error(e)
        except SQLAlchemyError as e:
            return ErrorHandler.handle_database_error(e)
        except Exception as e:
            ErrorHandler.log_error(e)
            
            if request.is_json:
                return jsonify({
                    'error': {
                        'message': 'An unexpected error occurred. Please try again later.',
                        'type': 'InternalServerError',
                        'code': 'INTERNAL_ERROR'
                    }
                }), 500
            else:
                flash('An unexpected error occurred. Please try again later.', 'error')
                return redirect(request.referrer or url_for('index'))
    
    return decorated_function


class InputValidator:
    """Utility class for input validation"""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]):
        """Validate that all required fields are present and not empty"""
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
                empty_fields.append(field)
        
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                code='MISSING_FIELDS'
            )
        
        if empty_fields:
            raise ValidationError(
                f"Empty required fields: {', '.join(empty_fields)}",
                code='EMPTY_FIELDS'
            )
    
    @staticmethod
    def validate_integer(value: Any, field_name: str, min_value: int = None, max_value: int = None) -> int:
        """Validate integer input"""
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid integer", field=field_name)
        
        if min_value is not None and int_value < min_value:
            raise ValidationError(f"{field_name} must be at least {min_value}", field=field_name)
        
        if max_value is not None and int_value > max_value:
            raise ValidationError(f"{field_name} cannot exceed {max_value}", field=field_name)
        
        return int_value
    
    @staticmethod
    def validate_decimal(value: Any, field_name: str, min_value: float = None, max_value: float = None) -> float:
        """Validate decimal input"""
        try:
            decimal_value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid number", field=field_name)
        
        if min_value is not None and decimal_value < min_value:
            raise ValidationError(f"{field_name} must be at least {min_value}", field=field_name)
        
        if max_value is not None and decimal_value > max_value:
            raise ValidationError(f"{field_name} cannot exceed {max_value}", field=field_name)
        
        return decimal_value
    
    @staticmethod
    def validate_string(value: Any, field_name: str, min_length: int = None, max_length: int = None, 
                       pattern: str = None) -> str:
        """Validate string input"""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string", field=field_name)
        
        value = value.strip()
        
        if min_length is not None and len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters", field=field_name)
        
        if max_length is not None and len(value) > max_length:
            raise ValidationError(f"{field_name} cannot exceed {max_length} characters", field=field_name)
        
        if pattern:
            import re
            if not re.match(pattern, value):
                raise ValidationError(f"{field_name} format is invalid", field=field_name)
        
        return value
    
    @staticmethod
    def validate_choice(value: Any, field_name: str, choices: List[Any]) -> Any:
        """Validate that value is in allowed choices"""
        if value not in choices:
            raise ValidationError(
                f"{field_name} must be one of: {', '.join(map(str, choices))}",
                field=field_name
            )
        return value


class SecurityValidator:
    """Security-focused validation utilities"""
    
    @staticmethod
    def validate_user_access(user_id: int, resource_user_id: int):
        """Validate that user can access resource belonging to another user"""
        if not current_user.is_authenticated:
            raise AuthorizationError("Authentication required")
        
        # Admin can access any resource
        if current_user.role == 'admin':
            return True
        
        # Users can only access their own resources
        if current_user.id != resource_user_id:
            raise AuthorizationError("Access denied to this resource")
        
        return True
    
    @staticmethod
    def validate_admin_access():
        """Validate that current user has admin access"""
        if not current_user.is_authenticated:
            raise AuthorizationError("Authentication required")
        
        if current_user.role != 'admin':
            raise AuthorizationError("Admin privileges required")
        
        return True
    
    @staticmethod
    def validate_customer_access():
        """Validate that current user has customer access"""
        if not current_user.is_authenticated:
            raise AuthorizationError("Authentication required")
        
        if current_user.role != 'customer':
            raise AuthorizationError("Customer account required")
        
        return True
    
    @staticmethod
    def sanitize_input(value: str) -> str:
        """Basic input sanitization"""
        if not isinstance(value, str):
            return value
        
        # Remove potentially dangerous characters
        import re
        # Remove script tags and other potentially dangerous content
        value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
        value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
        value = re.sub(r'on\w+\s*=', '', value, flags=re.IGNORECASE)
        
        return value.strip()


def register_error_handlers(app):
    """Register global error handlers with Flask app"""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return ErrorHandler.handle_validation_error(error)
    
    @app.errorhandler(BusinessLogicError)
    def handle_business_logic_error(error):
        return ErrorHandler.handle_business_logic_error(error)
    
    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error):
        return ErrorHandler.handle_authorization_error(error)
    
    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        return ErrorHandler.handle_database_error(error)
    
    @app.errorhandler(404)
    def handle_not_found(error):
        ErrorHandler.log_error(error)
        
        if request.is_json:
            return jsonify({
                'error': {
                    'message': 'Resource not found',
                    'type': 'NotFound',
                    'code': 'NOT_FOUND'
                }
            }), 404
        else:
            flash('The requested page was not found.', 'error')
            return redirect(url_for('index'))
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        ErrorHandler.log_error(error)
        
        if request.is_json:
            return jsonify({
                'error': {
                    'message': 'Method not allowed',
                    'type': 'MethodNotAllowed',
                    'code': 'METHOD_NOT_ALLOWED'
                }
            }), 405
        else:
            flash('Method not allowed for this endpoint.', 'error')
            return redirect(url_for('index'))
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        db.session.rollback()
        ErrorHandler.log_error(error)
        
        if request.is_json:
            return jsonify({
                'error': {
                    'message': 'Internal server error',
                    'type': 'InternalServerError',
                    'code': 'INTERNAL_ERROR'
                }
            }), 500
        else:
            flash('An internal error occurred. Please try again later.', 'error')
            return redirect(url_for('index'))
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        db.session.rollback()
        ErrorHandler.log_error(error)
        
        if request.is_json:
            return jsonify({
                'error': {
                    'message': 'An unexpected error occurred',
                    'type': 'UnexpectedError',
                    'code': 'UNEXPECTED_ERROR'
                }
            }), 500
        else:
            flash('An unexpected error occurred. Please try again later.', 'error')
            return redirect(url_for('index'))


class RequestValidator:
    """Request-level validation utilities"""
    
    @staticmethod
    def validate_json_request(required_fields: List[str] = None):
        """Decorator to validate JSON requests"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not request.is_json:
                    raise ValidationError("Request must be JSON", code='INVALID_CONTENT_TYPE')
                
                data = request.get_json()
                if not data:
                    raise ValidationError("Request body must contain valid JSON", code='INVALID_JSON')
                
                if required_fields:
                    InputValidator.validate_required_fields(data, required_fields)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def validate_form_request(required_fields: List[str] = None):
        """Decorator to validate form requests"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if required_fields:
                    data = request.form.to_dict()
                    InputValidator.validate_required_fields(data, required_fields)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator