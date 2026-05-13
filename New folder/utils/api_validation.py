"""
API-specific validation utilities for Smart Inventory Management System
Provides comprehensive validation for API endpoints
"""

import json
from functools import wraps
from typing import Dict, Any, List, Optional, Union
from flask import request, jsonify
from utils.error_handling import ValidationError, InputValidator, SecurityValidator


class APIValidator:
    """Comprehensive API validation utilities"""
    
    @staticmethod
    def validate_json_schema(schema: Dict[str, Any]):
        """Validate JSON request against schema"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not request.is_json:
                    raise ValidationError("Request must be JSON", code='INVALID_CONTENT_TYPE')
                
                data = request.get_json()
                if not data:
                    raise ValidationError("Request body must contain valid JSON", code='INVALID_JSON')
                
                # Validate against schema
                APIValidator._validate_data_against_schema(data, schema)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def validate_query_params(param_schema: Dict[str, Dict[str, Any]]):
        """Validate query parameters"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                for param_name, param_config in param_schema.items():
                    value = request.args.get(param_name)
                    
                    # Check if required
                    if param_config.get('required', False) and not value:
                        raise ValidationError(f"Missing required parameter: {param_name}")
                    
                    if value:
                        # Validate type
                        param_type = param_config.get('type', 'string')
                        validated_value = APIValidator._validate_param_type(value, param_type, param_name)
                        
                        # Validate range/choices
                        if 'min' in param_config and validated_value < param_config['min']:
                            raise ValidationError(f"{param_name} must be at least {param_config['min']}")
                        
                        if 'max' in param_config and validated_value > param_config['max']:
                            raise ValidationError(f"{param_name} cannot exceed {param_config['max']}")
                        
                        if 'choices' in param_config and validated_value not in param_config['choices']:
                            raise ValidationError(f"{param_name} must be one of: {', '.join(map(str, param_config['choices']))}")
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def validate_pagination():
        """Validate pagination parameters"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                page = request.args.get('page', '1')
                per_page = request.args.get('per_page', '50')
                
                try:
                    page = int(page)
                    per_page = int(per_page)
                except ValueError:
                    raise ValidationError("Page and per_page must be integers")
                
                if page < 1:
                    raise ValidationError("Page must be at least 1")
                
                if per_page < 1 or per_page > 100:
                    raise ValidationError("Per page must be between 1 and 100")
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def validate_product_data():
        """Validate product data for API endpoints"""
        schema = {
            'name': {'type': 'string', 'required': True, 'min_length': 2, 'max_length': 200},
            'description': {'type': 'string', 'max_length': 1000},
            'category': {'type': 'string', 'required': True, 'min_length': 2, 'max_length': 100},
            'cost_price': {'type': 'number', 'required': True, 'min': 0, 'max': 999999.99},
            'selling_price': {'type': 'number', 'required': True, 'min': 0, 'max': 999999.99},
            'quantity': {'type': 'integer', 'min': 0, 'max': 1000000},
            'low_stock_threshold': {'type': 'integer', 'min': 0, 'max': 1000}
        }
        return APIValidator.validate_json_schema(schema)
    
    @staticmethod
    def validate_purchase_request_data():
        """Validate purchase request data for API endpoints"""
        schema = {
            'product_id': {'type': 'integer', 'required': True, 'min': 1},
            'quantity': {'type': 'integer', 'required': True, 'min': 1, 'max': 1000}
        }
        return APIValidator.validate_json_schema(schema)
    
    @staticmethod
    def validate_user_data():
        """Validate user data for API endpoints"""
        schema = {
            'email': {'type': 'email', 'required': True, 'max_length': 120},
            'first_name': {'type': 'string', 'required': True, 'min_length': 2, 'max_length': 80},
            'last_name': {'type': 'string', 'required': True, 'min_length': 2, 'max_length': 80},
            'password': {'type': 'string', 'required': True, 'min_length': 8, 'max_length': 128},
            'role': {'type': 'string', 'choices': ['customer', 'admin']}
        }
        return APIValidator.validate_json_schema(schema)
    
    @staticmethod
    def validate_search_params():
        """Validate search parameters"""
        param_schema = {
            'search': {'type': 'string', 'max_length': 100},
            'category': {'type': 'string', 'max_length': 100},
            'sort_by': {'type': 'string', 'choices': ['name', 'price_asc', 'price_desc', 'quantity', 'created_at']},
            'in_stock_only': {'type': 'boolean'},
            'low_stock_only': {'type': 'boolean'}
        }
        return APIValidator.validate_query_params(param_schema)
    
    @staticmethod
    def validate_date_range():
        """Validate date range parameters"""
        param_schema = {
            'start_date': {'type': 'date', 'required': False},
            'end_date': {'type': 'date', 'required': False}
        }
        return APIValidator.validate_query_params(param_schema)
    
    @staticmethod
    def _validate_data_against_schema(data: Dict[str, Any], schema: Dict[str, Any]):
        """Validate data against schema definition"""
        for field_name, field_config in schema.items():
            value = data.get(field_name)
            
            # Check if required
            if field_config.get('required', False) and value is None:
                raise ValidationError(f"Missing required field: {field_name}")
            
            if value is not None:
                # Validate type
                field_type = field_config.get('type', 'string')
                validated_value = APIValidator._validate_field_type(value, field_type, field_name)
                
                # Validate string length
                if field_type == 'string' and isinstance(validated_value, str):
                    if 'min_length' in field_config and len(validated_value) < field_config['min_length']:
                        raise ValidationError(f"{field_name} must be at least {field_config['min_length']} characters")
                    
                    if 'max_length' in field_config and len(validated_value) > field_config['max_length']:
                        raise ValidationError(f"{field_name} cannot exceed {field_config['max_length']} characters")
                
                # Validate numeric range
                if field_type in ['integer', 'number'] and isinstance(validated_value, (int, float)):
                    if 'min' in field_config and validated_value < field_config['min']:
                        raise ValidationError(f"{field_name} must be at least {field_config['min']}")
                    
                    if 'max' in field_config and validated_value > field_config['max']:
                        raise ValidationError(f"{field_name} cannot exceed {field_config['max']}")
                
                # Validate choices
                if 'choices' in field_config and validated_value not in field_config['choices']:
                    raise ValidationError(f"{field_name} must be one of: {', '.join(map(str, field_config['choices']))}")
                
                # Sanitize string values
                if field_type == 'string' and isinstance(validated_value, str):
                    data[field_name] = SecurityValidator.sanitize_input(validated_value)
    
    @staticmethod
    def _validate_field_type(value: Any, field_type: str, field_name: str) -> Any:
        """Validate field type and convert if necessary"""
        if field_type == 'string':
            if not isinstance(value, str):
                raise ValidationError(f"{field_name} must be a string")
            return value
        
        elif field_type == 'integer':
            try:
                return int(value)
            except (ValueError, TypeError):
                raise ValidationError(f"{field_name} must be an integer")
        
        elif field_type == 'number':
            try:
                return float(value)
            except (ValueError, TypeError):
                raise ValidationError(f"{field_name} must be a number")
        
        elif field_type == 'boolean':
            if isinstance(value, bool):
                return value
            elif isinstance(value, str):
                if value.lower() in ['true', '1', 'yes', 'on']:
                    return True
                elif value.lower() in ['false', '0', 'no', 'off']:
                    return False
            raise ValidationError(f"{field_name} must be a boolean")
        
        elif field_type == 'email':
            if not isinstance(value, str):
                raise ValidationError(f"{field_name} must be a string")
            
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                raise ValidationError(f"{field_name} must be a valid email address")
            return value.lower().strip()
        
        elif field_type == 'date':
            if not isinstance(value, str):
                raise ValidationError(f"{field_name} must be a date string")
            
            import re
            from datetime import datetime
            
            # Validate date format (YYYY-MM-DD)
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                raise ValidationError(f"{field_name} must be in YYYY-MM-DD format")
            
            try:
                datetime.strptime(value, '%Y-%m-%d')
                return value
            except ValueError:
                raise ValidationError(f"{field_name} is not a valid date")
        
        else:
            return value
    
    @staticmethod
    def _validate_param_type(value: str, param_type: str, param_name: str) -> Any:
        """Validate query parameter type"""
        if param_type == 'string':
            return SecurityValidator.sanitize_input(value)
        
        elif param_type == 'integer':
            try:
                return int(value)
            except ValueError:
                raise ValidationError(f"{param_name} must be an integer")
        
        elif param_type == 'number':
            try:
                return float(value)
            except ValueError:
                raise ValidationError(f"{param_name} must be a number")
        
        elif param_type == 'boolean':
            if value.lower() in ['true', '1', 'yes', 'on']:
                return True
            elif value.lower() in ['false', '0', 'no', 'off']:
                return False
            else:
                raise ValidationError(f"{param_name} must be a boolean")
        
        elif param_type == 'date':
            import re
            from datetime import datetime
            
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                raise ValidationError(f"{param_name} must be in YYYY-MM-DD format")
            
            try:
                datetime.strptime(value, '%Y-%m-%d')
                return value
            except ValueError:
                raise ValidationError(f"{param_name} is not a valid date")
        
        else:
            return value


class ResponseValidator:
    """Validate API responses"""
    
    @staticmethod
    def format_success_response(data: Any, message: str = None, status_code: int = 200) -> tuple:
        """Format successful API response"""
        response = {
            'success': True,
            'data': data
        }
        
        if message:
            response['message'] = message
        
        return jsonify(response), status_code
    
    @staticmethod
    def format_error_response(error: str, code: str = None, status_code: int = 400) -> tuple:
        """Format error API response"""
        response = {
            'success': False,
            'error': {
                'message': error
            }
        }
        
        if code:
            response['error']['code'] = code
        
        return jsonify(response), status_code
    
    @staticmethod
    def format_validation_error_response(errors: List[str], status_code: int = 400) -> tuple:
        """Format validation error response"""
        response = {
            'success': False,
            'error': {
                'message': 'Validation failed',
                'code': 'VALIDATION_ERROR',
                'details': errors
            }
        }
        
        return jsonify(response), status_code
    
    @staticmethod
    def format_paginated_response(items: List[Any], total_count: int, page: int, per_page: int) -> Dict[str, Any]:
        """Format paginated response"""
        return {
            'success': True,
            'data': {
                'items': items,
                'pagination': {
                    'total_count': total_count,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total_count + per_page - 1) // per_page,
                    'has_next': page * per_page < total_count,
                    'has_prev': page > 1
                }
            }
        }