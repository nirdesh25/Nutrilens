"""
Alert routes for Smart Inventory Management System
Handles alert display, management, and API endpoints
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from utils.auth import admin_required
from services.alert_service import AlertService
from models.alert import Alert, AlertType, AlertSeverity, AlertStatus
from extensions import db

# Create blueprint
alert_bp = Blueprint('alerts', __name__, url_prefix='/alerts')


@alert_bp.route('/')
@login_required
@admin_required
def alert_dashboard():
    """Display alert management dashboard"""
    try:
        # Get alert summary and active alerts
        alert_summary = AlertService.get_alert_summary()
        dashboard_alerts = AlertService.get_dashboard_alerts(limit=20)
        
        return render_template('admin/alerts.html',
                             alert_summary=alert_summary,
                             alerts=dashboard_alerts,
                             page_title="Alert Management")
    
    except Exception as e:
        flash(f'Error loading alerts: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))


@alert_bp.route('/api/alerts')
@login_required
@admin_required
def get_alerts_api():
    """API endpoint to get alerts with filtering"""
    try:
        # Get query parameters
        alert_type = request.args.get('type')
        severity = request.args.get('severity')
        status = request.args.get('status', 'active')
        limit = int(request.args.get('limit', 50))
        
        # Build query
        query = Alert.query
        
        if status == 'active':
            query = query.filter_by(status=AlertStatus.ACTIVE)
        elif status:
            query = query.filter_by(status=AlertStatus(status))
        
        if alert_type:
            query = query.filter_by(alert_type=AlertType(alert_type))
        
        if severity:
            query = query.filter_by(severity=AlertSeverity(severity))
        
        # Order by severity and creation time
        alerts = query.order_by(
            Alert.severity.desc(),
            Alert.created_at.desc()
        ).limit(limit).all()
        
        # Convert to dictionaries
        alert_data = []
        for alert in alerts:
            alert_dict = alert.to_dict()
            alert_dict['urgency_score'] = AlertService._calculate_urgency_score(alert)
            alert_dict['action_required'] = AlertService._get_suggested_action(alert)
            alert_dict['time_ago'] = AlertService._format_time_ago(alert.created_at)
            alert_data.append(alert_dict)
        
        return jsonify({
            'success': True,
            'alerts': alert_data,
            'total_count': len(alert_data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@alert_bp.route('/api/summary')
@login_required
@admin_required
def get_alert_summary_api():
    """API endpoint to get alert summary statistics"""
    try:
        summary = AlertService.get_alert_summary()
        return jsonify({
            'success': True,
            'summary': summary
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@alert_bp.route('/api/acknowledge/<int:alert_id>', methods=['POST'])
@login_required
@admin_required
def acknowledge_alert_api(alert_id):
    """API endpoint to acknowledge an alert"""
    try:
        success = AlertService.acknowledge_alert(alert_id, current_user.id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Alert acknowledged successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Alert not found or already processed'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@alert_bp.route('/api/resolve/<int:alert_id>', methods=['POST'])
@login_required
@admin_required
def resolve_alert_api(alert_id):
    """API endpoint to resolve an alert"""
    try:
        success = AlertService.resolve_alert(alert_id, current_user.id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Alert resolved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Alert not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@alert_bp.route('/api/dismiss/<int:alert_id>', methods=['POST'])
@login_required
@admin_required
def dismiss_alert_api(alert_id):
    """API endpoint to dismiss an alert"""
    try:
        success = AlertService.dismiss_alert(alert_id, current_user.id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Alert dismissed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Alert not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@alert_bp.route('/api/bulk-action', methods=['POST'])
@login_required
@admin_required
def bulk_alert_action_api():
    """API endpoint for bulk alert actions"""
    try:
        data = request.get_json()
        alert_ids = data.get('alert_ids', [])
        action = data.get('action')  # 'acknowledge', 'resolve', 'dismiss'
        
        if not alert_ids or not action:
            return jsonify({
                'success': False,
                'error': 'Missing alert_ids or action'
            }), 400
        
        success_count = 0
        
        for alert_id in alert_ids:
            if action == 'acknowledge':
                if AlertService.acknowledge_alert(alert_id, current_user.id):
                    success_count += 1
            elif action == 'resolve':
                if AlertService.resolve_alert(alert_id, current_user.id):
                    success_count += 1
            elif action == 'dismiss':
                if AlertService.dismiss_alert(alert_id, current_user.id):
                    success_count += 1
        
        return jsonify({
            'success': True,
            'message': f'{success_count} alerts processed successfully',
            'processed_count': success_count,
            'total_requested': len(alert_ids)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@alert_bp.route('/api/generate', methods=['POST'])
@login_required
@admin_required
def generate_alerts_api():
    """API endpoint to manually trigger alert generation"""
    try:
        monitoring_result = AlertService.run_alert_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Alert monitoring completed',
            'result': monitoring_result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@alert_bp.route('/widget')
@login_required
@admin_required
def alert_widget():
    """Get alert widget data for dashboard"""
    try:
        # Get top priority alerts for widget display
        dashboard_alerts = AlertService.get_dashboard_alerts(limit=5)
        alert_summary = AlertService.get_alert_summary()
        
        return jsonify({
            'success': True,
            'alerts': dashboard_alerts,
            'summary': alert_summary
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Error handlers for alert blueprint
@alert_bp.errorhandler(404)
def alert_not_found(error):
    """Handle 404 errors in alert routes"""
    if request.is_json:
        return jsonify({
            'success': False,
            'error': 'Alert not found'
        }), 404
    else:
        flash('Alert not found', 'error')
        return redirect(url_for('alerts.alert_dashboard'))


@alert_bp.errorhandler(500)
def alert_server_error(error):
    """Handle 500 errors in alert routes"""
    db.session.rollback()
    
    if request.is_json:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    else:
        flash('An error occurred while processing alerts', 'error')
        return redirect(url_for('alerts.alert_dashboard'))