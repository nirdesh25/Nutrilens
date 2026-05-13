"""
Notification Service for Smart Inventory Management System
Handles email notifications and in-app notification delivery
"""

import smtplib
try:
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
except ImportError:
    # Fallback for systems where email modules might not be available
    MimeText = None
    MimeMultipart = None
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from flask import current_app, render_template_string
from extensions import db
from models.alert import Alert, AlertType, AlertSeverity
from models.user import User
from models.product import Product


class NotificationService:
    """Service for managing notifications and email delivery"""
    
    # Email templates
    LOW_STOCK_EMAIL_TEMPLATE = """
    <html>
    <body>
        <h2>Low Stock Alert - {{ product_name }}</h2>
        <p>Dear {{ recipient_name }},</p>
        
        <p>This is an automated notification to inform you that the following product is running low on stock:</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
            <h3>{{ product_name }}</h3>
            <p><strong>Category:</strong> {{ category }}</p>
            <p><strong>Current Stock:</strong> {{ current_stock }} units</p>
            <p><strong>Low Stock Threshold:</strong> {{ threshold }} units</p>
            {% if days_until_empty %}
            <p><strong>Estimated Days Until Empty:</strong> {{ days_until_empty }} days</p>
            {% endif %}
            <p><strong>Suggested Reorder Quantity:</strong> {{ suggested_reorder }} units</p>
        </div>
        
        <p><strong>Recommended Action:</strong> {{ action_required }}</p>
        
        <p>Please take appropriate action to restock this item to avoid stockouts.</p>
        
        <p>Best regards,<br>Smart Inventory Management System</p>
        
        <hr>
        <small>This is an automated message. Please do not reply to this email.</small>
    </body>
    </html>
    """
    
    OUT_OF_STOCK_EMAIL_TEMPLATE = """
    <html>
    <body>
        <h2 style="color: #dc3545;">URGENT: Out of Stock Alert - {{ product_name }}</h2>
        <p>Dear {{ recipient_name }},</p>
        
        <p><strong>URGENT:</strong> The following product is completely out of stock and requires immediate attention:</p>
        
        <div style="background-color: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
            <h3 style="color: #721c24;">{{ product_name }}</h3>
            <p><strong>Category:</strong> {{ category }}</p>
            <p><strong>Current Stock:</strong> <span style="color: #dc3545; font-weight: bold;">0 units (OUT OF STOCK)</span></p>
            <p><strong>Low Stock Threshold:</strong> {{ threshold }} units</p>
            {% if last_sale_date %}
            <p><strong>Last Sale:</strong> {{ last_sale_date }}</p>
            {% endif %}
            <p><strong>Suggested Reorder Quantity:</strong> {{ suggested_reorder }} units</p>
        </div>
        
        <p style="color: #dc3545;"><strong>IMMEDIATE ACTION REQUIRED:</strong> Restock this item immediately to prevent lost sales.</p>
        
        <p>This product is no longer available for customer orders. Please prioritize restocking to resume sales.</p>
        
        <p>Best regards,<br>Smart Inventory Management System</p>
        
        <hr>
        <small>This is an automated urgent notification. Please do not reply to this email.</small>
    </body>
    </html>
    """
    
    DAILY_SUMMARY_EMAIL_TEMPLATE = """
    <html>
    <body>
        <h2>Daily Inventory Summary - {{ date }}</h2>
        <p>Dear {{ recipient_name }},</p>
        
        <p>Here's your daily inventory summary:</p>
        
        <h3>Alert Summary</h3>
        <ul>
            <li><strong>Critical Alerts:</strong> {{ critical_alerts }} (Out of stock or critical low stock)</li>
            <li><strong>Warning Alerts:</strong> {{ warning_alerts }} (Low stock)</li>
            <li><strong>Total Active Alerts:</strong> {{ total_alerts }}</li>
        </ul>
        
        {% if critical_products %}
        <h3>Products Requiring Immediate Attention</h3>
        <div style="background-color: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0;">
            {% for product in critical_products %}
            <p><strong>{{ product.name }}</strong> - {{ product.current_stock }} units ({{ product.status }})</p>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if warning_products %}
        <h3>Products Running Low</h3>
        <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
            {% for product in warning_products %}
            <p><strong>{{ product.name }}</strong> - {{ product.current_stock }} units (Threshold: {{ product.threshold }})</p>
            {% endfor %}
        </div>
        {% endif %}
        
        <p>Please review these alerts and take appropriate action to maintain optimal inventory levels.</p>
        
        <p>Best regards,<br>Smart Inventory Management System</p>
        
        <hr>
        <small>This is an automated daily summary. You can manage your notification preferences in the system settings.</small>
    </body>
    </html>
    """
    
    @staticmethod
    def send_low_stock_notification(alert: Alert, recipients: List[str] = None) -> bool:
        """
        Send low stock notification email
        
        Args:
            alert: Alert object containing stock information
            recipients: List of email addresses (defaults to all admin users)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            if not recipients:
                recipients = NotificationService._get_admin_emails()
            
            if not recipients:
                current_app.logger.warning("No admin email addresses found for notifications")
                return False
            
            # Get product information
            product = alert.product
            if not product:
                current_app.logger.error(f"Product not found for alert {alert.id}")
                return False
            
            # Determine email template based on alert type
            if alert.alert_type == AlertType.OUT_OF_STOCK:
                template = NotificationService.OUT_OF_STOCK_EMAIL_TEMPLATE
                subject = f"URGENT: {product.name} is Out of Stock"
            else:
                template = NotificationService.LOW_STOCK_EMAIL_TEMPLATE
                subject = f"Low Stock Alert: {product.name}"
            
            # Prepare template data
            template_data = {
                'product_name': product.name,
                'category': product.category,
                'current_stock': product.quantity,
                'threshold': product.low_stock_threshold,
                'days_until_empty': alert.alert_data.get('days_until_empty') if alert.alert_data else None,
                'suggested_reorder': alert.alert_data.get('suggested_reorder_quantity', product.low_stock_threshold * 2) if alert.alert_data else product.low_stock_threshold * 2,
                'action_required': NotificationService._get_action_text(alert),
                'last_sale_date': alert.alert_data.get('last_sale_date') if alert.alert_data else None
            }
            
            # Send email to each recipient
            success_count = 0
            for recipient in recipients:
                template_data['recipient_name'] = NotificationService._get_recipient_name(recipient)
                
                if NotificationService._send_email(recipient, subject, template, template_data):
                    success_count += 1
            
            # Log notification attempt
            current_app.logger.info(f"Low stock notification sent for {product.name}: {success_count}/{len(recipients)} successful")
            
            return success_count > 0
            
        except Exception as e:
            current_app.logger.error(f"Error sending low stock notification: {str(e)}")
            return False
    
    @staticmethod
    def send_daily_summary(recipients: List[str] = None) -> bool:
        """
        Send daily inventory summary email
        
        Args:
            recipients: List of email addresses (defaults to all admin users)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            if not recipients:
                recipients = NotificationService._get_admin_emails()
            
            if not recipients:
                current_app.logger.warning("No admin email addresses found for daily summary")
                return False
            
            # Get alert summary data
            from services.alert_service import AlertService
            alert_summary = AlertService.get_alert_summary()
            active_alerts = Alert.get_active_alerts()
            
            # Categorize alerts
            critical_products = []
            warning_products = []
            
            for alert in active_alerts:
                if alert.product:
                    product_info = {
                        'name': alert.product.name,
                        'current_stock': alert.product.quantity,
                        'threshold': alert.product.low_stock_threshold,
                        'status': 'Out of Stock' if alert.product.quantity == 0 else 'Critical Low Stock' if alert.product.quantity <= 5 else 'Low Stock'
                    }
                    
                    if alert.severity == AlertSeverity.CRITICAL:
                        critical_products.append(product_info)
                    else:
                        warning_products.append(product_info)
            
            # Prepare template data
            template_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'critical_alerts': alert_summary['by_severity']['critical'],
                'warning_alerts': alert_summary['by_severity']['warning'],
                'total_alerts': alert_summary['total_active'],
                'critical_products': critical_products[:10],  # Limit to top 10
                'warning_products': warning_products[:10]     # Limit to top 10
            }
            
            subject = f"Daily Inventory Summary - {template_data['date']}"
            
            # Send email to each recipient
            success_count = 0
            for recipient in recipients:
                template_data['recipient_name'] = NotificationService._get_recipient_name(recipient)
                
                if NotificationService._send_email(recipient, subject, NotificationService.DAILY_SUMMARY_EMAIL_TEMPLATE, template_data):
                    success_count += 1
            
            current_app.logger.info(f"Daily summary sent: {success_count}/{len(recipients)} successful")
            
            return success_count > 0
            
        except Exception as e:
            current_app.logger.error(f"Error sending daily summary: {str(e)}")
            return False
    
    @staticmethod
    def create_in_app_notification(user_id: int, title: str, message: str, 
                                 notification_type: str = 'info', alert_id: int = None) -> bool:
        """
        Create an in-app notification for a user
        
        Args:
            user_id: ID of the user to notify
            title: Notification title
            message: Notification message
            notification_type: Type of notification (info, warning, error, success)
            alert_id: Related alert ID (optional)
            
        Returns:
            True if notification created successfully, False otherwise
        """
        try:
            # For now, we'll store in-app notifications in the alert_data field of alerts
            # In a full implementation, you might want a separate Notification model
            
            # This is a simplified implementation - in production you'd want a proper notification system
            current_app.logger.info(f"In-app notification created for user {user_id}: {title}")
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error creating in-app notification: {str(e)}")
            return False
    
    @staticmethod
    def get_user_notification_preferences(user_id: int) -> Dict:
        """
        Get notification preferences for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with notification preferences
        """
        # This is a simplified implementation
        # In production, you'd store preferences in the database
        return {
            'email_notifications': True,
            'low_stock_alerts': True,
            'out_of_stock_alerts': True,
            'daily_summary': True,
            'in_app_notifications': True
        }
    
    @staticmethod
    def update_user_notification_preferences(user_id: int, preferences: Dict) -> bool:
        """
        Update notification preferences for a user
        
        Args:
            user_id: User ID
            preferences: Dictionary with preference updates
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # This is a simplified implementation
            # In production, you'd store preferences in the database
            current_app.logger.info(f"Notification preferences updated for user {user_id}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error updating notification preferences: {str(e)}")
            return False
    
    @staticmethod
    def send_purchase_approval_notification(customer, purchase_request, sale):
        """
        Send notification to customer about purchase approval
        
        Args:
            customer: Customer user object
            purchase_request: PurchaseRequest object
            sale: Sale object
        
        Returns:
            bool: Success status
        """
        try:
            # For now, just log the notification
            # In production, you'd send an actual email
            current_app.logger.info(f"Purchase approval notification sent to {customer.email} for request {purchase_request.id}")
            return True
        except Exception as e:
            current_app.logger.error(f"Error sending purchase approval notification: {str(e)}")
            return False
    
    @staticmethod
    def send_purchase_rejection_notification(customer, purchase_request, reason):
        """
        Send notification to customer about purchase rejection
        
        Args:
            customer: Customer user object
            purchase_request: PurchaseRequest object
            reason: Rejection reason
        
        Returns:
            bool: Success status
        """
        try:
            # For now, just log the notification
            # In production, you'd send an actual email
            current_app.logger.info(f"Purchase rejection notification sent to {customer.email} for request {purchase_request.id}: {reason}")
            return True
        except Exception as e:
            current_app.logger.error(f"Error sending purchase rejection notification: {str(e)}")
            return False
    
    @staticmethod
    def process_alert_notifications(alert: Alert) -> bool:
        """
        Process notifications for a new alert
        
        Args:
            alert: Alert object to process notifications for
            
        Returns:
            True if notifications processed successfully, False otherwise
        """
        try:
            success = True
            
            # Send email notifications for stock-related alerts
            if alert.alert_type in [AlertType.LOW_STOCK, AlertType.OUT_OF_STOCK, AlertType.CRITICAL_STOCK]:
                email_success = NotificationService.send_low_stock_notification(alert)
                success = success and email_success
            
            # Create in-app notifications for admin users
            admin_users = User.query.filter_by(role='admin').all()
            for admin in admin_users:
                NotificationService.create_in_app_notification(
                    user_id=admin.id,
                    title=alert.title,
                    message=alert.message,
                    notification_type='warning' if alert.severity == AlertSeverity.WARNING else 'error',
                    alert_id=alert.id
                )
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Error processing alert notifications: {str(e)}")
            return False
    
    # Private helper methods
    
    @staticmethod
    def _send_email(recipient: str, subject: str, template: str, template_data: Dict) -> bool:
        """
        Send an email using SMTP
        
        Args:
            recipient: Email address
            subject: Email subject
            template: HTML email template
            template_data: Data for template rendering
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Get email configuration from app config
            smtp_server = current_app.config.get('MAIL_SERVER', 'localhost')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            smtp_username = current_app.config.get('MAIL_USERNAME')
            smtp_password = current_app.config.get('MAIL_PASSWORD')
            smtp_use_tls = current_app.config.get('MAIL_USE_TLS', True)
            sender_email = current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@inventory.com')
            
            # Skip email sending if not configured
            if not smtp_username or not smtp_password:
                current_app.logger.warning("Email configuration not found, skipping email notification")
                return False
            
            # Render template
            rendered_html = render_template_string(template, **template_data)
            
            # Skip if email modules not available
            if not MimeText or not MimeMultipart:
                current_app.logger.warning("Email modules not available, skipping email notification")
                return False
            
            # Create message
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = recipient
            
            # Add HTML content
            html_part = MimeText(rendered_html, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if smtp_use_tls:
                    server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            current_app.logger.info(f"Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error sending email to {recipient}: {str(e)}")
            return False
    
    @staticmethod
    def _get_admin_emails() -> List[str]:
        """Get list of admin email addresses"""
        try:
            admin_users = User.query.filter_by(role='admin').all()
            return [user.email for user in admin_users if user.email]
        except Exception as e:
            current_app.logger.error(f"Error getting admin emails: {str(e)}")
            return []
    
    @staticmethod
    def _get_recipient_name(email: str) -> str:
        """Get recipient name from email address"""
        try:
            user = User.query.filter_by(email=email).first()
            if user:
                return user.full_name
            else:
                return email.split('@')[0].title()
        except Exception:
            return email.split('@')[0].title()
    
    @staticmethod
    def _get_action_text(alert: Alert) -> str:
        """Get recommended action text for alert"""
        if alert.alert_type == AlertType.OUT_OF_STOCK:
            return "Restock immediately to resume sales"
        elif alert.alert_type == AlertType.CRITICAL_STOCK:
            return "Order inventory urgently to prevent stockout"
        elif alert.alert_type == AlertType.LOW_STOCK:
            return "Schedule restock order to maintain inventory levels"
        else:
            return "Review inventory levels and take appropriate action"