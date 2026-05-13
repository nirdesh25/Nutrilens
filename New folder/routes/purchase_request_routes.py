"""
Purchase Request routes for Smart Inventory Management System
Enhanced with comprehensive error handling and validation
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from forms import PurchaseRequestForm, QuickPurchaseRequestForm
from models.product import Product
from models.purchase_request import PurchaseRequest
from services.purchase_request_service import PurchaseRequestService
from extensions import db
from utils.error_handling import (
    handle_errors, ValidationError, BusinessLogicError, AuthorizationError,
    InputValidator, SecurityValidator, RequestValidator
)
from utils.route_protection import customer_required, api_customer_required

# Create blueprint
purchase_request_bp = Blueprint('purchase_requests', __name__)


@purchase_request_bp.route('/products')
@customer_required
@handle_errors
def customer_product_list():
    """Display products for customers to browse and request with validation"""
    
    # Validate and sanitize search parameters
    search = SecurityValidator.sanitize_input(request.args.get('search', ''))
    category = SecurityValidator.sanitize_input(request.args.get('category', ''))
    
    # Validate search length
    if search and len(search) > 100:
        raise ValidationError("Search term is too long")
    
    try:
        # Build query with validation
        query = Product.query.filter_by(is_active=True)
        
        if search:
            # Use parameterized query to prevent SQL injection
            search_pattern = f"%{search}%"
            query = query.filter(Product.name.ilike(search_pattern))
        
        if category:
            query = query.filter(Product.category == category)
        
        # Only show products that are in stock for customers
        products = query.filter(Product.quantity > 0).all()
        
        # Get categories safely
        categories = db.session.query(Product.category).filter_by(is_active=True).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
    except Exception as e:
        raise BusinessLogicError(f"Failed to retrieve products: {str(e)}")
    
    form = QuickPurchaseRequestForm()
    
    return render_template('customer/products.html', 
                         products=products, 
                         categories=categories,
                         search=search,
                         selected_category=category,
                         form=form)


@purchase_request_bp.route('/products/<int:product_id>/request', methods=['GET', 'POST'])
@customer_required
@handle_errors
def request_product(product_id):
    """Submit a purchase request for a specific product with validation"""
    # Validate product ID
    if product_id <= 0:
        raise ValidationError("Invalid product ID")
    
    try:
        product = Product.query.get(product_id)
        if not product or not product.is_active:
            raise BusinessLogicError('Product not found or not available')
        
        if product.is_out_of_stock():
            raise BusinessLogicError(f'Product "{product.name}" is currently out of stock')
    except Exception as e:
        if isinstance(e, BusinessLogicError):
            raise
        raise BusinessLogicError(f"Failed to retrieve product: {str(e)}")
    
    form = PurchaseRequestForm()
    form.product_id.data = product_id
    
    if form.validate_on_submit():
        # Additional server-side validation
        quantity = InputValidator.validate_integer(form.quantity.data, "Quantity", min_value=1, max_value=1000)
        
        # Validate product availability
        if not product.can_fulfill_quantity(quantity):
            raise ValidationError(f'Only {product.quantity} units available in stock')
        
        try:
            # Create purchase request using service
            purchase_request = PurchaseRequestService.create_purchase_request(
                customer_id=current_user.id,
                product_id=product_id,
                quantity=quantity
            )
            
            flash(f'Purchase request submitted successfully for {product.name}!', 'success')
            return redirect(url_for('purchase_requests.purchase_history'))
        except ValueError as e:
            raise BusinessLogicError(f'Failed to submit request: {str(e)}')
    
    return render_template('customer/request_product.html', product=product, form=form)


@purchase_request_bp.route('/api/products/<int:product_id>/quick-request', methods=['POST'])
@api_customer_required
@RequestValidator.validate_form_request(['quantity'])
@handle_errors
def quick_request_product(product_id):
    """API endpoint for quick purchase requests with comprehensive validation"""
    # Validate product ID
    if product_id <= 0:
        raise ValidationError("Invalid product ID")
    
    # Validate and sanitize quantity
    quantity_str = request.form.get('quantity', '1')
    quantity = InputValidator.validate_integer(quantity_str, "Quantity", min_value=1, max_value=1000)
    
    # Validate product exists and is available
    try:
        product = Product.query.get(product_id)
        if not product or not product.is_active:
            raise BusinessLogicError('Product not found or not available')
        
        if product.is_out_of_stock():
            raise BusinessLogicError(f'Product "{product.name}" is currently out of stock')
        
        if not product.can_fulfill_quantity(quantity):
            raise ValidationError(f'Only {product.quantity} units available in stock')
    except Exception as e:
        if isinstance(e, (BusinessLogicError, ValidationError)):
            raise
        raise BusinessLogicError(f"Failed to validate product: {str(e)}")
    
    try:
        # Create purchase request using service
        purchase_request = PurchaseRequestService.create_purchase_request(
            customer_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        
        return jsonify({
            'success': True,
            'message': f'Request for {quantity} units of {purchase_request.product.name} submitted successfully!',
            'request_id': purchase_request.id,
            'product_name': purchase_request.product.name,
            'quantity': quantity,
            'total_value': float(purchase_request.total_value)
        })
    except ValueError as e:
        raise BusinessLogicError(f'Failed to create purchase request: {str(e)}')


@purchase_request_bp.route('/purchase-history')
@login_required
def purchase_history():
    """Display customer's purchase request history"""
    if current_user.role != 'customer':
        flash('Access denied. Customer account required.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    
    # Get requests using service
    requests = PurchaseRequestService.get_customer_requests(
        customer_id=current_user.id,
        status=status_filter if status_filter else None
    )
    
    return render_template('customer/purchase_history.html', 
                         requests=requests,
                         status_filter=status_filter)


@purchase_request_bp.route('/api/purchase-requests/history')
@login_required
def api_purchase_history():
    """API endpoint to get customer's purchase request history"""
    if current_user.role != 'customer':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    # Get requests using service with pagination
    requests = PurchaseRequestService.get_customer_requests(
        customer_id=current_user.id,
        status=status_filter if status_filter else None,
        limit=limit,
        offset=offset
    )
    
    # Get total count for pagination
    total_query = PurchaseRequest.get_customer_requests(current_user.id)
    if status_filter:
        total_query = total_query.filter(PurchaseRequest.status == status_filter)
    total_count = total_query.count()
    
    return jsonify({
        'requests': [request.to_dict() for request in requests],
        'total_count': total_count,
        'limit': limit,
        'offset': offset,
        'has_more': (offset + limit) < total_count
    })


@purchase_request_bp.route('/api/purchase-requests/<int:request_id>')
@login_required
def api_get_purchase_request(request_id):
    """API endpoint to get a specific purchase request"""
    if current_user.role != 'customer':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get request using service with access control
    purchase_request = PurchaseRequestService.get_request_by_id(request_id, current_user.id)
    
    if not purchase_request:
        return jsonify({'error': 'Request not found or access denied'}), 404
    
    return jsonify(purchase_request.to_dict())


@purchase_request_bp.route('/api/purchase-requests/stats')
@login_required
def api_purchase_request_stats():
    """API endpoint to get customer's purchase request statistics"""
    if current_user.role != 'customer':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get stats using service
    stats = PurchaseRequestService.get_customer_request_stats(current_user.id)
    return jsonify(stats)


@purchase_request_bp.route('/api/products/check-availability/<int:product_id>')
@login_required
def api_check_product_availability(product_id):
    """API endpoint to check product availability for purchase requests"""
    if current_user.role != 'customer':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        quantity = int(request.args.get('quantity', 1))
        
        # Check availability using service
        availability = PurchaseRequestService.check_product_availability(product_id, quantity)
        
        if not availability.get('exists'):
            return jsonify({'error': availability.get('error', 'Product not found')}), 404
        
        return jsonify(availability)
        
    except ValueError:
        return jsonify({'error': 'Invalid quantity specified'}), 400


@purchase_request_bp.route('/api/purchase-requests/submit', methods=['POST'])
@login_required
def api_submit_purchase_request():
    """API endpoint for submitting purchase requests via JSON"""
    if current_user.role != 'customer':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        
        if not product_id or not quantity:
            return jsonify({'error': 'Product ID and quantity are required'}), 400
        
        # Validate inputs
        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except ValueError:
            return jsonify({'error': 'Invalid product ID or quantity'}), 400
        
        # Create purchase request using service
        purchase_request = PurchaseRequestService.create_purchase_request(
            customer_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        
        return jsonify({
            'success': True,
            'message': f'Purchase request submitted successfully for {purchase_request.product.name}',
            'request_id': purchase_request.id,
            'request': purchase_request.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500