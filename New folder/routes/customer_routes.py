"""
Customer management routes for admin interface
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from services.customer_service import CustomerService
from utils.auth import admin_required

customer_bp = Blueprint('customers', __name__, url_prefix='/admin/customers')


@customer_bp.route('/')
@login_required
@admin_required
def customer_list():
    """Display list of all customers with overview metrics"""
    try:
        customers_data = CustomerService.get_customers_overview()
        segmentation = CustomerService.get_customer_segmentation()
        
        return render_template('admin/customers/list.html', 
                             customers_data=customers_data,
                             segmentation=segmentation)
    except Exception as e:
        flash(f'Error loading customer data: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))


@customer_bp.route('/<int:customer_id>')
@login_required
@admin_required
def customer_detail(customer_id):
    """Display detailed view of a specific customer"""
    try:
        # Get comprehensive customer data
        activity_summary = CustomerService.get_customer_activity_summary(customer_id, days=90)
        purchase_patterns = CustomerService.get_customer_purchase_patterns(customer_id)
        insights = CustomerService.get_customer_insights(customer_id)
        
        if not activity_summary:
            flash('Customer not found.', 'error')
            return redirect(url_for('customers.customer_list'))
        
        return render_template('admin/customers/detail.html',
                             activity_summary=activity_summary,
                             purchase_patterns=purchase_patterns,
                             insights=insights)
    except Exception as e:
        flash(f'Error loading customer details: {str(e)}', 'error')
        return redirect(url_for('customers.customer_list'))


@customer_bp.route('/<int:customer_id>/activity')
@login_required
@admin_required
def customer_activity(customer_id):
    """Get customer activity data for different time periods"""
    try:
        days = request.args.get('days', 30, type=int)
        activity_data = CustomerService.get_customer_activity_summary(customer_id, days=days)
        
        if not activity_data:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify(activity_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/<int:customer_id>/patterns')
@login_required
@admin_required
def customer_patterns(customer_id):
    """Get customer purchase patterns and preferences"""
    try:
        patterns = CustomerService.get_customer_purchase_patterns(customer_id)
        
        if not patterns:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify(patterns)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/<int:customer_id>/insights')
@login_required
@admin_required
def customer_insights(customer_id):
    """Get AI-generated insights about customer behavior"""
    try:
        insights = CustomerService.get_customer_insights(customer_id)
        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/segmentation')
@login_required
@admin_required
def customer_segmentation():
    """Get customer segmentation data"""
    try:
        segmentation = CustomerService.get_customer_segmentation()
        return jsonify(segmentation)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/<int:customer_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_customer(customer_id):
    """Deactivate a customer account"""
    try:
        result = CustomerService.deactivate_customer(customer_id, current_user.id)
        flash(result['message'], 'success')
        return redirect(url_for('customers.customer_detail', customer_id=customer_id))
    except Exception as e:
        flash(f'Error deactivating customer: {str(e)}', 'error')
        return redirect(url_for('customers.customer_detail', customer_id=customer_id))


@customer_bp.route('/<int:customer_id>/reactivate', methods=['POST'])
@login_required
@admin_required
def reactivate_customer(customer_id):
    """Reactivate a customer account"""
    try:
        result = CustomerService.reactivate_customer(customer_id, current_user.id)
        flash(result['message'], 'success')
        return redirect(url_for('customers.customer_detail', customer_id=customer_id))
    except Exception as e:
        flash(f'Error reactivating customer: {str(e)}', 'error')
        return redirect(url_for('customers.customer_detail', customer_id=customer_id))


@customer_bp.route('/api/overview')
@login_required
@admin_required
def api_customers_overview():
    """API endpoint for customers overview data"""
    try:
        customers_data = CustomerService.get_customers_overview()
        return jsonify(customers_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_bp.route('/export')
@login_required
@admin_required
def export_customers():
    """Export customer data to CSV"""
    try:
        import csv
        from io import StringIO
        from flask import make_response
        
        customers_data = CustomerService.get_customers_overview()
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Customer ID', 'Name', 'Email', 'Registration Date', 
            'Total Requests', 'Total Purchases', 'Total Spent', 
            'Last Activity', 'Days Since Activity'
        ])
        
        # Write customer data
        for customer_data in customers_data['customers']:
            customer = customer_data['customer']
            metrics = customer_data['metrics']
            
            writer.writerow([
                customer['id'],
                customer['full_name'],
                customer['email'],
                customer['created_at'],
                metrics['total_requests'],
                metrics['total_purchases'],
                metrics['total_spent'],
                metrics['last_activity'],
                metrics['days_since_activity']
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=customers_export.csv'
        
        return response
    except Exception as e:
        flash(f'Error exporting customer data: {str(e)}', 'error')
        return redirect(url_for('customers.customer_list'))