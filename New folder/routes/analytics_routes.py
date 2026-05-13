"""
Analytics routes for Smart Inventory Management System
Provides API endpoints for dashboard data and analytics
"""

from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from services.analytics_service import AnalyticsService
from services.calendar_service import CalendarService
from services.alert_service import AlertService
from utils.route_protection import api_admin_required, admin_required

# Create blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/admin/analytics')


@analytics_bp.route('/dashboard', methods=['GET'])
@login_required
@admin_required
def get_dashboard_data():
    """
    Get comprehensive dashboard metrics
    
    Query Parameters:
        days (int): Number of days to analyze (default: 30)
    
    Returns:
        JSON response with dashboard metrics
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        # Validate days parameter
        if days < 1 or days > 365:
            return jsonify({
                'error': 'Days parameter must be between 1 and 365'
            }), 400
        
        metrics = AnalyticsService.get_dashboard_metrics(days)
        
        return jsonify({
            'success': True,
            'data': metrics
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch dashboard data: {str(e)}'
        }), 500


@analytics_bp.route('/sales-chart', methods=['GET'])
@login_required
@admin_required
def get_sales_chart_data():
    """
    Get sales data formatted for charts
    
    Query Parameters:
        days (int): Number of days to include (default: 30)
    
    Returns:
        JSON response with chart-ready sales data
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        if days < 1 or days > 365:
            return jsonify({
                'error': 'Days parameter must be between 1 and 365'
            }), 400
        
        chart_data = AnalyticsService.get_sales_chart_data(days)
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch sales chart data: {str(e)}'
        }), 500


@analytics_bp.route('/product-performance', methods=['GET'])
@login_required
@admin_required
def get_product_performance():
    """
    Get product performance analytics
    
    Query Parameters:
        days (int): Number of days to analyze (default: 30)
    
    Returns:
        JSON response with product performance data
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        if days < 1 or days > 365:
            return jsonify({
                'error': 'Days parameter must be between 1 and 365'
            }), 400
        
        performance_data = AnalyticsService.get_product_performance_data(days)
        
        return jsonify({
            'success': True,
            'data': performance_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch product performance data: {str(e)}'
        }), 500


@analytics_bp.route('/low-stock-alerts', methods=['GET'])
@login_required
@admin_required
def get_low_stock_alerts():
    """
    Get low stock alerts for dashboard
    
    Returns:
        JSON response with low stock alerts
    """
    try:
        alerts = AnalyticsService.get_low_stock_alerts()
        
        return jsonify({
            'success': True,
            'data': {
                'alerts': alerts,
                'total_alerts': len(alerts),
                'critical_alerts': len([a for a in alerts if a['alert_level'] == 'critical']),
                'warning_alerts': len([a for a in alerts if a['alert_level'] == 'warning'])
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch low stock alerts: {str(e)}'
        }), 500


@analytics_bp.route('/customer-analytics', methods=['GET'])
@login_required
@admin_required
def get_customer_analytics():
    """
    Get customer analytics data
    
    Query Parameters:
        days (int): Number of days to analyze (default: 30)
    
    Returns:
        JSON response with customer analytics
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        if days < 1 or days > 365:
            return jsonify({
                'error': 'Days parameter must be between 1 and 365'
            }), 400
        
        customer_data = AnalyticsService.get_customer_analytics(days)
        
        return jsonify({
            'success': True,
            'data': customer_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch customer analytics: {str(e)}'
        }), 500


@analytics_bp.route('/summary', methods=['GET'])
@login_required
@admin_required
def get_analytics_summary():
    """
    Get a quick analytics summary for dashboard widgets
    
    Returns:
        JSON response with key metrics summary
    """
    try:
        # Get basic metrics for quick dashboard display
        metrics = AnalyticsService.get_dashboard_metrics(30)
        alerts = AnalyticsService.get_low_stock_alerts()
        
        summary = {
            'total_revenue': metrics['sales_metrics']['total_revenue'],
            'total_sales': metrics['sales_metrics']['total_sales'],
            'pending_requests': metrics['request_metrics']['pending_requests'],
            'low_stock_alerts': len(alerts),
            'critical_alerts': len([a for a in alerts if a['alert_level'] == 'critical']),
            'active_customers': metrics['customer_metrics']['active_customers'],
            'stock_health': metrics['product_metrics']['stock_health_percentage']
        }
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch analytics summary: {str(e)}'
        }), 500


# Dashboard page routes (HTML endpoints)

@analytics_bp.route('/dashboard-page', methods=['GET'])
@login_required
@admin_required
def dashboard_page():
    """
    Render the analytics dashboard page
    
    Returns:
        Rendered dashboard template
    """
    try:
        # Get initial data for server-side rendering
        initial_metrics = AnalyticsService.get_dashboard_metrics(30)
        alerts = AnalyticsService.get_low_stock_alerts()
        
        return render_template('admin/dashboard.html',
                             initial_metrics=initial_metrics,
                             alerts=alerts,
                             current_user=current_user)
        
    except Exception as e:
        return render_template('admin/dashboard.html',
                             error=f'Failed to load dashboard data: {str(e)}',
                             current_user=current_user)


# Utility endpoints for specific dashboard components

@analytics_bp.route('/stock-status', methods=['GET'])
@login_required
@admin_required
def get_stock_status():
    """
    Get current stock status overview
    
    Returns:
        JSON response with stock status data
    """
    try:
        low_stock_products = AnalyticsService.get_low_stock_products()
        
        stock_data = {
            'low_stock_count': len(low_stock_products),
            'out_of_stock_count': len([p for p in low_stock_products if p.quantity == 0]),
            'critical_count': len([p for p in low_stock_products if p.quantity <= 5]),
            'products': [
                {
                    'id': product.id,
                    'name': product.name,
                    'category': product.category,
                    'current_stock': product.quantity,
                    'threshold': product.low_stock_threshold,
                    'status': 'out_of_stock' if product.quantity == 0 else 'critical' if product.quantity <= 5 else 'low'
                }
                for product in low_stock_products[:10]  # Limit to top 10 for quick display
            ]
        }
        
        return jsonify({
            'success': True,
            'data': stock_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch stock status: {str(e)}'
        }), 500


@analytics_bp.route('/recent-activity', methods=['GET'])
@login_required
@admin_required
def get_recent_activity():
    """
    Get recent activity data for dashboard
    
    Query Parameters:
        limit (int): Number of recent items to return (default: 10)
    
    Returns:
        JSON response with recent activity
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        from models.sale import Sale
        from models.purchase_request import PurchaseRequest
        
        # Get recent sales
        recent_sales = Sale.get_recent_sales(7)[:limit]
        
        # Get recent purchase requests
        recent_requests = PurchaseRequest.query.order_by(
            PurchaseRequest.requested_at.desc()
        ).limit(limit).all()
        
        activity_data = {
            'recent_sales': [
                {
                    'id': sale.id,
                    'product_name': sale.product.name if sale.product else 'Unknown',
                    'customer_name': sale.customer.full_name if sale.customer else 'Unknown',
                    'quantity': sale.quantity,
                    'total_amount': float(sale.total_amount),
                    'sale_date': sale.sale_date.isoformat()
                }
                for sale in recent_sales
            ],
            'recent_requests': [
                {
                    'id': req.id,
                    'product_name': req.product.name if req.product else 'Unknown',
                    'customer_name': req.customer.full_name if req.customer else 'Unknown',
                    'quantity': req.quantity,
                    'status': req.status,
                    'requested_at': req.requested_at.isoformat()
                }
                for req in recent_requests
            ]
        }
        
        return jsonify({
            'success': True,
            'data': activity_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch recent activity: {str(e)}'
        }), 500


# Calendar API endpoints

@analytics_bp.route('/calendar', methods=['GET'])
@login_required
@admin_required
def get_calendar_data():
    """
    Get calendar data for the specified date range
    
    Query Parameters:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        month (int): Month number (1-12) - alternative to date range
        year (int): Year - used with month parameter
    
    Returns:
        JSON response with calendar events and summary data
    """
    try:
        # Check if month/year parameters are provided
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if month and year:
            # Use monthly data
            if month < 1 or month > 12:
                return jsonify({
                    'error': 'Month must be between 1 and 12'
                }), 400
            
            calendar_data = CalendarService.get_monthly_calendar_data(year, month)
        else:
            # Use date range parameters
            start_date_str = request.args.get('start_date')
            end_date_str = request.args.get('end_date')
            
            if not start_date_str or not end_date_str:
                # Default to current month if no parameters provided
                today = date.today()
                calendar_data = CalendarService.get_monthly_calendar_data(today.year, today.month)
            else:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    
                    if start_date > end_date:
                        return jsonify({
                            'error': 'Start date must be before or equal to end date'
                        }), 400
                    
                    # Limit date range to prevent excessive data
                    if (end_date - start_date).days > 365:
                        return jsonify({
                            'error': 'Date range cannot exceed 365 days'
                        }), 400
                    
                    calendar_data = CalendarService.get_calendar_data(start_date, end_date)
                    
                except ValueError:
                    return jsonify({
                        'error': 'Invalid date format. Use YYYY-MM-DD'
                    }), 400
        
        return jsonify({
            'success': True,
            'data': calendar_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch calendar data: {str(e)}'
        }), 500


@analytics_bp.route('/calendar/date/<date_str>', methods=['GET'])
@login_required
@admin_required
def get_date_details(date_str):
    """
    Get detailed sales information for a specific date
    
    Path Parameters:
        date_str (str): Date in YYYY-MM-DD format
    
    Returns:
        JSON response with detailed sales information for the date
    """
    try:
        # Parse and validate date
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }), 400
        
        # Check if date is not too far in the future
        if target_date > date.today() + timedelta(days=1):
            return jsonify({
                'error': 'Cannot retrieve data for future dates'
            }), 400
        
        date_details = CalendarService.get_date_details(target_date)
        
        return jsonify({
            'success': True,
            'data': date_details
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch date details: {str(e)}'
        }), 500


@analytics_bp.route('/calendar/patterns', methods=['GET'])
@login_required
@admin_required
def get_sales_patterns():
    """
    Get sales pattern analysis for calendar insights
    
    Query Parameters:
        days (int): Number of days to analyze (default: 90)
    
    Returns:
        JSON response with sales pattern analysis
    """
    try:
        days = request.args.get('days', 90, type=int)
        
        if days < 7 or days > 365:
            return jsonify({
                'error': 'Days parameter must be between 7 and 365'
            }), 400
        
        patterns = CalendarService.analyze_sales_patterns(days)
        
        return jsonify({
            'success': True,
            'data': patterns
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to analyze sales patterns: {str(e)}'
        }), 500


@analytics_bp.route('/calendar/weekly/<int:year>/<int:week>', methods=['GET'])
@login_required
@admin_required
def get_weekly_calendar_data(year, week):
    """
    Get calendar data for a specific week
    
    Path Parameters:
        year (int): Year (e.g., 2024)
        week (int): Week number (1-53)
    
    Returns:
        JSON response with weekly calendar data
    """
    try:
        if week < 1 or week > 53:
            return jsonify({
                'error': 'Week number must be between 1 and 53'
            }), 400
        
        if year < 2020 or year > 2030:
            return jsonify({
                'error': 'Year must be between 2020 and 2030'
            }), 400
        
        calendar_data = CalendarService.get_weekly_calendar_data(year, week)
        
        return jsonify({
            'success': True,
            'data': calendar_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch weekly calendar data: {str(e)}'
        }), 500


# Calendar page route (HTML endpoint)

@analytics_bp.route('/calendar-page', methods=['GET'])
@login_required
@admin_required
def calendar_page():
    """
    Render the sales calendar page
    
    Returns:
        Rendered calendar template
    """
    try:
        return render_template('admin/calendar.html', current_user=current_user)
        
    except Exception as e:
        return render_template('admin/calendar.html',
                             error=f'Failed to load calendar page: {str(e)}',
                             current_user=current_user)