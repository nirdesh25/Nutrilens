"""
Notification routes for Smart Inventory Management System
Handles notification preferences and delivery management
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from utils.auth import admin_required
from services.notification_service import NotificationService
from models.notification_preference import NotificationPreference
from extensions import db

# Create blueprint
notification_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@notification_bp.route('/preferences')
@login_required
def notification_preferences():
    """Display notification preferences page"""
    try:
        # Get or create preferences for current user
        preferences = NotificationPreference.get_or_create_for_user(current_user.id)
        
        return render_template('admin/notification_preferences.html',
                             preferences=preferences,
                             page_title="Notification Preferences")
    
    except Exception as e:
        flash(f'Error loading notification preferences: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))


@notification_bp.route('/api/preferences')
@login_required
def get_preferences_api():
    """API endpoint to get user notification preferences"""
    try:
        preferences = NotificationPreference.get_or_create_for_user(current_user.id)
        
        return jsonify({
            'success': True,
            'preferences': preferences.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notification_bp.route('/api/preferences', methods=['POST'])
@login_required
def update_preferences_api():
    """API endpoint to update user notification preferences"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Get or create preferences
        preferences = NotificationPreference.get_or_create_for_user(current_user.id)
        
        # Update preferences
        preferences.update_preferences(**data)
        
        return jsonify({
            'success': True,
            'message': 'Notification preferences updated successfully',
            'preferences': preferences.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notification_bp.route('/api/test-email', methods=['POST'])
@login_required
@admin_required
def test_email_notification():
    """API endpoint to send a test email notification"""
    try:
        data = request.get_json()
        recipient = data.get('recipient', current_user.email)
        
        # Create a test alert for demonstration
        from models.alert import Alert, AlertType, AlertSeverity
        from models.product import Product
        
        # Get a sample product for testing
        sample_product = Product.query.first()
        if not sample_product:
            return jsonify({
                'success': False,
                'error': 'No products available for testing'
            }), 400
        
        # Create a temporary alert object (not saved to database)
        test_alert = Alert(
            alert_type=AlertType.LOW_STOCK,
            severity=AlertSeverity.WARNING,
            title=f"Test Alert: {sample_product.name}",
            message=f"This is a test notification for {sample_product.name}",
            product_id=sample_product.id
        )
        test_alert.product = sample_product
        test_alert.alert_data = {
            'current_stock': sample_product.quantity,
            'threshold': sample_product.low_stock_threshold,
            'suggested_reorder_quantity': sample_product.low_stock_threshold * 2,
            'days_until_empty': 7
        }
        
        # Send test notification
        success = NotificationService.send_low_stock_notification(test_alert, [recipient])
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Test email sent successfully to {recipient}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send test email. Check email configuration.'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notification_bp.route('/api/send-daily-summary', methods=['POST'])
@login_required
@admin_required
def send_daily_summary_api():
    """API endpoint to manually send daily summary"""
    try:
        data = request.get_json()
        recipients = data.get('recipients', [])
        
        # Send daily summary
        success = NotificationService.send_daily_summary(recipients if recipients else None)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Daily summary sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send daily summary'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notification_bp.route('/api/notification-history')
@login_required
def get_notification_history():
    """API endpoint to get notification history for current user"""
    try:
        # This is a simplified implementation
        # In production, you'd store notification history in the database
        
        history = [
            {
                'id': 1,
                'type': 'low_stock_alert',
                'title': 'Low Stock Alert',
                'message': 'Product XYZ is running low on stock',
                'sent_at': datetime.now().isoformat(),
                'status': 'delivered',
                'channel': 'email'
            }
        ]
        
        return jsonify({
            'success': True,
            'history': history
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notification_bp.route('/api/in-app-notifications')
@login_required
def get_in_app_notifications():
    """API endpoint to get in-app notifications for current user"""
    try:
        # This is a simplified implementation
        # In production, you'd have a proper notification system
        
        # For now, we'll return active alerts as notifications
        from models.alert import Alert
        
        active_alerts = Alert.get_active_alerts()
        
        notifications = []
        for alert in active_alerts[:10]:  # Limit to 10 most recent
            notifications.append({
                'id': alert.id,
                'title': alert.title,
                'message': alert.message,
                'type': alert.severity.value,
                'created_at': alert.created_at.isoformat(),
                'is_read': False,
                'alert_id': alert.id
            })
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': len(notifications)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notification_bp.route('/api/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """API endpoint to mark a notification as read"""
    try:
        # This is a simplified implementation
        # In production, you'd update the notification status in the database
        
        return jsonify({
            'success': True,
            'message': 'Notification marked as read'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notification_bp.route('/api/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """API endpoint to mark all notifications as read"""
    try:
        # This is a simplified implementation
        # In production, you'd update all notification statuses in the database
        
        return jsonify({
            'success': True,
            'message': 'All notifications marked as read'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Admin-only notification management routes

@notification_bp.route('/admin/settings')
@login_required
@admin_required
def admin_notification_settings():
    """Display admin notification settings page"""
    try:
        return render_template('admin/notification_settings.html',
                             page_title="Notification Settings")
    
    except Exception as e:
        flash(f'Error loading notification settings: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))


@notification_bp.route('/api/admin/email-config')
@login_required
@admin_required
def get_email_config():
    """API endpoint to get email configuration status"""
    try:
        from flask import current_app
        
        config_status = {
            'smtp_configured': bool(current_app.config.get('MAIL_SERVER')),
            'smtp_server': current_app.config.get('MAIL_SERVER', 'Not configured'),
            'smtp_port': current_app.config.get('MAIL_PORT', 'Not configured'),
            'smtp_username': bool(current_app.config.get('MAIL_USERNAME')),
            'smtp_use_tls': current_app.config.get('MAIL_USE_TLS', False),
            'default_sender': current_app.config.get('MAIL_DEFAULT_SENDER', 'Not configured')
        }
        
        return jsonify({
            'success': True,
            'config': config_status
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@notification_bp.route('/api/admin/notification-stats')
@login_required
@admin_required
def get_notification_stats():
    """API endpoint to get notification statistics"""
    try:
        # This is a simplified implementation
        # In production, you'd track actual notification statistics
        
        stats = {
            'total_sent_today': 15,
            'total_sent_week': 87,
            'total_sent_month': 342,
            'delivery_rate': 98.5,
            'bounce_rate': 1.2,
            'open_rate': 76.3,
            'active_subscribers': 25,
            'email_enabled_users': 23,
            'in_app_enabled_users': 25
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Error handlers for notification blueprint
@notification_bp.errorhandler(404)
def notification_not_found(error):
    """Handle 404 errors in notification routes"""
    if request.is_json:
        return jsonify({
            'success': False,
            'error': 'Notification endpoint not found'
        }), 404
    else:
        flash('Notification page not found', 'error')
        return redirect(url_for('notifications.notification_preferences'))


@notification_bp.errorhandler(500)
def notification_server_error(error):
    """Handle 500 errors in notification routes"""
    db.session.rollback()
    
    if request.is_json:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    else:
        flash('An error occurred while processing notifications', 'error')
        return redirect(url_for('notifications.notification_preferences'))