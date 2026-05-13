"""
Product management routes for Smart Inventory Management System
Enhanced with comprehensive error handling and validation
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from services.product_service import ProductService
from forms import ProductForm, QuantityUpdateForm, SearchForm
from extensions import db
from utils.error_handling import (
    handle_errors, ValidationError, BusinessLogicError, AuthorizationError,
    InputValidator, SecurityValidator, RequestValidator
)
from utils.route_protection import admin_required, api_admin_required

# Create blueprint
product_bp = Blueprint('products', __name__)


@product_bp.route('/admin/products')
@admin_required
@handle_errors
def admin_product_list():
    """Admin product listing page with enhanced error handling"""
    
    # Validate and sanitize filter parameters
    search = SecurityValidator.sanitize_input(request.args.get('search', ''))
    category = SecurityValidator.sanitize_input(request.args.get('category', ''))
    stock_filter = request.args.get('stock_filter', '')
    
    # Validate stock filter
    valid_stock_filters = ['', 'in_stock', 'low_stock', 'out_of_stock']
    if stock_filter not in valid_stock_filters:
        raise ValidationError("Invalid stock filter")
    
    # Validate search length
    if search and len(search) > 100:
        raise ValidationError("Search term is too long")
    
    try:
        # Search products based on filters
        products = ProductService.search_products(
            search_term=search if search else None,
            category=category if category else None,
            in_stock_only=(stock_filter == 'in_stock'),
            low_stock_only=(stock_filter == 'low_stock')
        )
    except Exception as e:
        raise BusinessLogicError(f"Failed to retrieve products: {str(e)}")
    
    # Get categories for filter dropdown
    categories = ProductService.get_categories()
    
    # Get inventory summary
    inventory_summary = ProductService.get_inventory_summary()
    
    return render_template('admin/products.html',
                         products=products,
                         categories=categories,
                         search=search,
                         selected_category=category,
                         stock_filter=stock_filter,
                         inventory_summary=inventory_summary)


@product_bp.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
@handle_errors
def add_product():
    """Add new product page with enhanced validation"""
    
    form = ProductForm()
    
    if form.validate_on_submit():
        # Additional server-side validation
        if form.selling_price.data < form.cost_price.data:
            raise ValidationError("Selling price cannot be less than cost price")
        
        if form.quantity.data < 0:
            raise ValidationError("Quantity cannot be negative")
        
        product_data = {
            'name': SecurityValidator.sanitize_input(form.name.data),
            'description': SecurityValidator.sanitize_input(form.description.data) if form.description.data else None,
            'category': SecurityValidator.sanitize_input(form.category.data),
            'cost_price': form.cost_price.data,
            'selling_price': form.selling_price.data,
            'quantity': form.quantity.data,
            'low_stock_threshold': form.low_stock_threshold.data or 10
        }
        
        try:
            product = ProductService.create_product(product_data)
            flash(f'Product "{product.name}" created successfully!', 'success')
            return redirect(url_for('products.admin_product_list'))
        except ValueError as e:
            raise BusinessLogicError(f'Failed to create product: {str(e)}')
    
    return render_template('admin/add_product.html', form=form)


@product_bp.route('/admin/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
@handle_errors
def edit_product(product_id):
    """Edit product page with enhanced validation"""
    # Validate product ID
    if product_id <= 0:
        raise ValidationError("Invalid product ID")
    
    try:
        product = ProductService.get_product_by_id(product_id)
        if not product:
            raise BusinessLogicError('Product not found')
    except Exception as e:
        raise BusinessLogicError(f'Failed to retrieve product: {str(e)}')
    
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        # Additional server-side validation
        if form.selling_price.data < form.cost_price.data:
            raise ValidationError("Selling price cannot be less than cost price")
        
        update_data = {
            'name': SecurityValidator.sanitize_input(form.name.data),
            'description': SecurityValidator.sanitize_input(form.description.data) if form.description.data else None,
            'category': SecurityValidator.sanitize_input(form.category.data),
            'cost_price': form.cost_price.data,
            'selling_price': form.selling_price.data,
            'quantity': form.quantity.data,
            'low_stock_threshold': form.low_stock_threshold.data or 10
        }
        
        try:
            updated_product = ProductService.update_product(product_id, update_data)
            flash(f'Product "{updated_product.name}" updated successfully!', 'success')
            return redirect(url_for('products.admin_product_list'))
        except ValueError as e:
            raise BusinessLogicError(f'Failed to update product: {str(e)}')
    
    return render_template('admin/edit_product.html', form=form, product=product)


@product_bp.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@admin_required
@handle_errors
def delete_product(product_id):
    """Delete product (soft delete) with enhanced validation"""
    # Validate product ID
    if product_id <= 0:
        raise ValidationError("Invalid product ID")
    
    try:
        ProductService.delete_product(product_id, soft_delete=True)
        flash('Product deleted successfully.', 'success')
        return redirect(url_for('products.admin_product_list'))
    except ValueError as e:
        raise BusinessLogicError(f'Failed to delete product: {str(e)}')


@product_bp.route('/admin/products/<int:product_id>/stock', methods=['POST'])
@api_admin_required
@RequestValidator.validate_form_request(['quantity', 'operation'])
@handle_errors
def update_product_stock(product_id):
    """Update product stock levels with comprehensive validation"""
    # Validate product ID
    if product_id <= 0:
        raise ValidationError("Invalid product ID")
    
    # Validate and sanitize input
    quantity_str = request.form.get('quantity', '0')
    operation = SecurityValidator.sanitize_input(request.form.get('operation', 'set'))
    
    # Validate quantity
    quantity = InputValidator.validate_integer(quantity_str, "Quantity", min_value=0, max_value=1000000)
    
    # Validate operation
    valid_operations = ['add', 'subtract', 'set']
    operation = InputValidator.validate_choice(operation, "Operation", valid_operations)
    
    # Additional validation based on operation
    if operation in ['add', 'subtract'] and quantity <= 0:
        raise ValidationError(f"Quantity for {operation} operation must be greater than 0")
    
    try:
        product = ProductService.update_stock(product_id, quantity, operation)
        
        return jsonify({
            'success': True,
            'message': f'Stock updated successfully. New quantity: {product.quantity}',
            'new_quantity': product.quantity,
            'is_low_stock': product.is_low_stock(),
            'is_out_of_stock': product.is_out_of_stock(),
            'product_name': product.name
        })
    except ValueError as e:
        raise BusinessLogicError(str(e))


# API Routes for AJAX operations
@product_bp.route('/api/products')
@login_required
@handle_errors
def api_get_products():
    """API endpoint to get products with filtering and validation"""
    # Validate and sanitize parameters
    search = SecurityValidator.sanitize_input(request.args.get('search', ''))
    category = SecurityValidator.sanitize_input(request.args.get('category', ''))
    in_stock_only = request.args.get('in_stock_only', 'false').lower() == 'true'
    low_stock_only = request.args.get('low_stock_only', 'false').lower() == 'true'
    
    # Validate search length
    if search and len(search) > 100:
        raise ValidationError("Search term is too long")
    
    # Validate pagination parameters
    page = InputValidator.validate_integer(request.args.get('page', 1), "Page", min_value=1, max_value=1000)
    per_page = InputValidator.validate_integer(request.args.get('per_page', 50), "Per page", min_value=1, max_value=100)
    
    try:
        products = ProductService.search_products(
            search_term=search if search else None,
            category=category if category else None,
            in_stock_only=in_stock_only,
            low_stock_only=low_stock_only
        )
        
        # Apply pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_products = products[start_idx:end_idx]
        
        return jsonify({
            'products': [product.to_dict() for product in paginated_products],
            'count': len(paginated_products),
            'total_count': len(products),
            'page': page,
            'per_page': per_page,
            'has_more': end_idx < len(products)
        })
    except Exception as e:
        raise BusinessLogicError(f"Failed to retrieve products: {str(e)}")


@product_bp.route('/api/products/<int:product_id>')
@login_required
@handle_errors
def api_get_product(product_id):
    """API endpoint to get single product with validation"""
    # Validate product ID
    if product_id <= 0:
        raise ValidationError("Invalid product ID")
    
    try:
        product = ProductService.get_product_by_id(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify(product.to_dict())
    except Exception as e:
        raise BusinessLogicError(f"Failed to retrieve product: {str(e)}")


@product_bp.route('/api/products/categories')
@login_required
def api_get_categories():
    """API endpoint to get all categories"""
    categories = ProductService.get_categories()
    return jsonify({'categories': categories})


@product_bp.route('/api/products/inventory-summary')
@login_required
def api_inventory_summary():
    """API endpoint to get inventory summary"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    summary = ProductService.get_inventory_summary()
    return jsonify(summary)


@product_bp.route('/api/products/low-stock')
@login_required
def api_low_stock_products():
    """API endpoint to get low stock products"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    products = ProductService.get_low_stock_products()
    return jsonify({
        'products': [product.to_dict() for product in products],
        'count': len(products)
    })


@product_bp.route('/api/products/out-of-stock')
@login_required
def api_out_of_stock_products():
    """API endpoint to get out of stock products"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    products = ProductService.get_out_of_stock_products()
    return jsonify({
        'products': [product.to_dict() for product in products],
        'count': len(products)
    })


@product_bp.route('/api/products/check-stock/<int:product_id>')
@login_required
def api_check_stock(product_id):
    """API endpoint to check stock availability"""
    requested_quantity = int(request.args.get('quantity', 1))
    
    availability = ProductService.check_stock_availability(product_id, requested_quantity)
    return jsonify(availability)


@product_bp.route('/api/products/bulk-stock-update', methods=['POST'])
@login_required
def api_bulk_stock_update():
    """API endpoint for bulk stock updates"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        updates = request.json.get('updates', [])
        
        if not updates:
            return jsonify({'error': 'No updates provided'}), 400
        
        results = ProductService.bulk_update_stock(updates)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Customer-facing product routes
@product_bp.route('/products')
@login_required
def customer_product_list():
    """Customer product browsing page"""
    if current_user.role != 'customer':
        flash('Access denied. Customer account required.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Get search and filter parameters
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    # Get products (only in-stock for customers)
    products = ProductService.search_products(
        search_term=search if search else None,
        category=category if category else None,
        in_stock_only=True  # Customers only see in-stock products
    )
    
    # Get categories for filter dropdown
    categories = ProductService.get_categories()
    
    return render_template('customer/products.html',
                         products=products,
                         categories=categories,
                         search=search,
                         selected_category=category)


@product_bp.route('/products/<int:product_id>')
@login_required
def product_detail(product_id):
    """Product detail page for customers"""
    if current_user.role != 'customer':
        flash('Access denied. Customer account required.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    product = ProductService.get_product_by_id(product_id)
    
    if not product or product.is_out_of_stock():
        flash('Product not available.', 'error')
        return redirect(url_for('products.customer_product_list'))
    
    return render_template('customer/product_detail.html', product=product)