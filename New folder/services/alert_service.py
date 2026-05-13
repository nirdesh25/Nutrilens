"""
Alert Service for Smart Inventory Management System
Handles alert generation, monitoring, and management
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import and_, or_
from extensions import db
from models.alert import Alert, AlertType, AlertSeverity, AlertStatus
from models.product import Product
from models.sale import Sale


class AlertService:
    """Service for managing inventory alerts and notifications"""
    
    @staticmethod
    def generate_low_stock_alerts() -> List[Alert]:
        """
        Generate alerts for products with low stock levels
        
        Returns:
            List of newly created alerts
        """
        # Get products that are low on stock
        low_stock_products = Product.query.filter(
            and_(
                Product.is_active == True,
                or_(
                    Product.quantity <= Product.low_stock_threshold,
                    Product.quantity == 0
                )
            )
        ).all()
        
        new_alerts = []
        
        for product in low_stock_products:
            # Check if there's already an active alert for this product
            existing_alert = Alert.query.filter_by(
                product_id=product.id,
                alert_type=AlertType.LOW_STOCK if product.quantity > 0 else AlertType.OUT_OF_STOCK,
                status=AlertStatus.ACTIVE
            ).first()
            
            if existing_alert:
                # Update existing alert if stock level changed significantly
                AlertService._update_existing_stock_alert(existing_alert, product)
                continue
            
            # Determine alert type and severity
            if product.quantity == 0:
                alert_type = AlertType.OUT_OF_STOCK
                severity = AlertSeverity.CRITICAL
                title = f"Out of Stock: {product.name}"
                message = f"Product '{product.name}' is completely out of stock and needs immediate restocking."
            elif product.quantity <= 5:  # Critical low stock
                alert_type = AlertType.CRITICAL_STOCK
                severity = AlertSeverity.CRITICAL
                title = f"Critical Stock Level: {product.name}"
                message = f"Product '{product.name}' has only {product.quantity} units left (threshold: {product.low_stock_threshold})."
            else:  # Regular low stock
                alert_type = AlertType.LOW_STOCK
                severity = AlertSeverity.WARNING
                title = f"Low Stock: {product.name}"
                message = f"Product '{product.name}' is running low with {product.quantity} units (threshold: {product.low_stock_threshold})."
            
            # Calculate additional alert data
            days_until_empty = AlertService._calculate_days_until_empty(product)
            suggested_reorder = AlertService._calculate_suggested_reorder_quantity(product)
            
            alert_data = {
                'current_stock': product.quantity,
                'threshold': product.low_stock_threshold,
                'category': product.category,
                'cost_price': float(product.cost_price),
                'selling_price': float(product.selling_price),
                'days_until_empty': days_until_empty,
                'suggested_reorder_quantity': suggested_reorder,
                'last_sale_date': AlertService._get_last_sale_date(product.id)
            }
            
            # Create new alert
            alert = Alert(
                alert_type=alert_type,
                severity=severity,
                title=title,
                message=message,
                product_id=product.id,
                alert_data=alert_data
            )
            
            db.session.add(alert)
            new_alerts.append(alert)
        
        # Commit all new alerts
        if new_alerts:
            db.session.commit()
            
            # Send notifications for new alerts
            from services.notification_service import NotificationService
            for alert in new_alerts:
                try:
                    NotificationService.process_alert_notifications(alert)
                except Exception as e:
                    # Log error but don't fail the alert creation
                    print(f"Error sending notification for alert {alert.id}: {str(e)}")
        
        return new_alerts
    
    @staticmethod
    def check_and_resolve_stock_alerts():
        """
        Check active stock alerts and resolve them if stock levels are restored
        """
        # Get active stock-related alerts
        active_stock_alerts = Alert.query.filter(
            and_(
                Alert.status == AlertStatus.ACTIVE,
                Alert.alert_type.in_([
                    AlertType.LOW_STOCK,
                    AlertType.OUT_OF_STOCK,
                    AlertType.CRITICAL_STOCK
                ])
            )
        ).all()
        
        resolved_count = 0
        
        for alert in active_stock_alerts:
            if alert.product:
                product = alert.product
                
                # Check if stock level is now above threshold
                if product.quantity > product.low_stock_threshold:
                    alert.resolve()
                    alert.alert_data = alert.alert_data or {}
                    alert.alert_data['auto_resolved'] = True
                    alert.alert_data['resolved_stock_level'] = product.quantity
                    resolved_count += 1
        
        if resolved_count > 0:
            db.session.commit()
        
        return resolved_count
    
    @staticmethod
    def get_dashboard_alerts(limit: int = 10) -> List[Dict]:
        """
        Get alerts for dashboard display
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries formatted for dashboard
        """
        alerts = Alert.get_active_alerts()[:limit]
        
        dashboard_alerts = []
        for alert in alerts:
            alert_dict = alert.to_dict()
            
            # Add additional dashboard-specific data
            alert_dict['urgency_score'] = AlertService._calculate_urgency_score(alert)
            alert_dict['action_required'] = AlertService._get_suggested_action(alert)
            alert_dict['time_ago'] = AlertService._format_time_ago(alert.created_at)
            
            dashboard_alerts.append(alert_dict)
        
        # Sort by urgency score (highest first)
        dashboard_alerts.sort(key=lambda x: x['urgency_score'], reverse=True)
        
        return dashboard_alerts
    
    @staticmethod
    def get_alert_summary() -> Dict:
        """
        Get summary of alert statistics
        
        Returns:
            Dictionary with alert counts and statistics
        """
        # Count alerts by severity
        critical_count = Alert.query.filter_by(
            severity=AlertSeverity.CRITICAL,
            status=AlertStatus.ACTIVE
        ).count()
        
        warning_count = Alert.query.filter_by(
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE
        ).count()
        
        info_count = Alert.query.filter_by(
            severity=AlertSeverity.INFO,
            status=AlertStatus.ACTIVE
        ).count()
        
        # Count alerts by type
        stock_alerts = Alert.query.filter(
            and_(
                Alert.status == AlertStatus.ACTIVE,
                Alert.alert_type.in_([
                    AlertType.LOW_STOCK,
                    AlertType.OUT_OF_STOCK,
                    AlertType.CRITICAL_STOCK
                ])
            )
        ).count()
        
        # Get recent activity
        recent_alerts = Alert.get_recent_alerts(hours=24)
        resolved_today = Alert.query.filter(
            and_(
                Alert.status == AlertStatus.RESOLVED,
                Alert.resolved_at >= datetime.utcnow() - timedelta(days=1)
            )
        ).count()
        
        return {
            'total_active': critical_count + warning_count + info_count,
            'by_severity': {
                'critical': critical_count,
                'warning': warning_count,
                'info': info_count
            },
            'by_type': {
                'stock_related': stock_alerts
            },
            'recent_activity': {
                'new_alerts_24h': len(recent_alerts),
                'resolved_today': resolved_today
            },
            'health_score': AlertService._calculate_system_health_score()
        }
    
    @staticmethod
    def acknowledge_alert(alert_id: int, user_id: int = None) -> bool:
        """
        Acknowledge an alert
        
        Args:
            alert_id: ID of the alert to acknowledge
            user_id: ID of the user acknowledging the alert
            
        Returns:
            True if successful, False otherwise
        """
        alert = Alert.query.get(alert_id)
        if not alert or alert.status != AlertStatus.ACTIVE:
            return False
        
        alert.acknowledge(user_id)
        db.session.commit()
        return True
    
    @staticmethod
    def resolve_alert(alert_id: int, user_id: int = None) -> bool:
        """
        Resolve an alert
        
        Args:
            alert_id: ID of the alert to resolve
            user_id: ID of the user resolving the alert
            
        Returns:
            True if successful, False otherwise
        """
        alert = Alert.query.get(alert_id)
        if not alert:
            return False
        
        alert.resolve(user_id)
        db.session.commit()
        return True
    
    @staticmethod
    def dismiss_alert(alert_id: int, user_id: int = None) -> bool:
        """
        Dismiss an alert
        
        Args:
            alert_id: ID of the alert to dismiss
            user_id: ID of the user dismissing the alert
            
        Returns:
            True if successful, False otherwise
        """
        alert = Alert.query.get(alert_id)
        if not alert:
            return False
        
        alert.dismiss(user_id)
        db.session.commit()
        return True
    
    @staticmethod
    def run_alert_monitoring():
        """
        Run complete alert monitoring cycle
        This should be called periodically (e.g., every hour)
        
        Returns:
            Dictionary with monitoring results
        """
        # Generate new alerts
        new_alerts = AlertService.generate_low_stock_alerts()
        
        # Resolve alerts that are no longer relevant
        resolved_count = AlertService.check_and_resolve_stock_alerts()
        
        # Clean up old alerts
        cleaned_count = Alert.cleanup_old_resolved_alerts(days=30)
        
        return {
            'new_alerts_created': len(new_alerts),
            'alerts_auto_resolved': resolved_count,
            'old_alerts_cleaned': cleaned_count,
            'monitoring_timestamp': datetime.utcnow().isoformat()
        }
    
    # Private helper methods
    
    @staticmethod
    def _update_existing_stock_alert(alert: Alert, product: Product):
        """Update existing stock alert with current product data"""
        # Update alert data with current stock information
        alert.alert_data = alert.alert_data or {}
        alert.alert_data['current_stock'] = product.quantity
        alert.alert_data['last_updated'] = datetime.utcnow().isoformat()
        
        # Update alert type and severity if stock level changed significantly
        if product.quantity == 0 and alert.alert_type != AlertType.OUT_OF_STOCK:
            alert.alert_type = AlertType.OUT_OF_STOCK
            alert.severity = AlertSeverity.CRITICAL
            alert.title = f"Out of Stock: {product.name}"
            alert.message = f"Product '{product.name}' is now completely out of stock."
        elif product.quantity <= 5 and alert.alert_type == AlertType.LOW_STOCK:
            alert.alert_type = AlertType.CRITICAL_STOCK
            alert.severity = AlertSeverity.CRITICAL
            alert.title = f"Critical Stock Level: {product.name}"
            alert.message = f"Product '{product.name}' stock has dropped to critical level: {product.quantity} units."
    
    @staticmethod
    def _calculate_days_until_empty(product: Product) -> Optional[int]:
        """Calculate estimated days until product runs out"""
        if product.quantity == 0:
            return 0
        
        # Get sales data from last 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        recent_sales = Sale.query.filter(
            and_(
                Sale.product_id == product.id,
                Sale.sale_date >= cutoff_date
            )
        ).all()
        
        if not recent_sales:
            return None
        
        total_sold = sum(sale.quantity for sale in recent_sales)
        days_with_data = 30  # We're looking at 30 days of data
        
        if total_sold == 0:
            return None
        
        average_daily_sales = total_sold / days_with_data
        return int(product.quantity / average_daily_sales) if average_daily_sales > 0 else None
    
    @staticmethod
    def _calculate_suggested_reorder_quantity(product: Product) -> int:
        """Calculate suggested reorder quantity"""
        # Base suggestion: 2x threshold or minimum 20 units
        base_suggestion = max(product.low_stock_threshold * 2, 20)
        
        # Adjust based on recent sales velocity
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        recent_sales = Sale.query.filter(
            and_(
                Sale.product_id == product.id,
                Sale.sale_date >= cutoff_date
            )
        ).all()
        
        if recent_sales:
            total_sold = sum(sale.quantity for sale in recent_sales)
            # Suggest enough for 60 days based on recent sales
            velocity_suggestion = int(total_sold * 2)  # 60 days worth
            return max(base_suggestion, velocity_suggestion)
        
        return base_suggestion
    
    @staticmethod
    def _get_last_sale_date(product_id: int) -> Optional[str]:
        """Get the last sale date for a product"""
        last_sale = Sale.query.filter_by(product_id=product_id).order_by(
            Sale.sale_date.desc()
        ).first()
        
        return last_sale.sale_date.isoformat() if last_sale else None
    
    @staticmethod
    def _calculate_urgency_score(alert: Alert) -> int:
        """Calculate urgency score for alert prioritization (0-100)"""
        score = 0
        
        # Base score by severity
        if alert.severity == AlertSeverity.CRITICAL:
            score += 50
        elif alert.severity == AlertSeverity.WARNING:
            score += 30
        else:
            score += 10
        
        # Add score based on alert type
        if alert.alert_type == AlertType.OUT_OF_STOCK:
            score += 30
        elif alert.alert_type == AlertType.CRITICAL_STOCK:
            score += 20
        elif alert.alert_type == AlertType.LOW_STOCK:
            score += 10
        
        # Add score based on age (older alerts get higher priority)
        age_hours = alert.age_in_hours
        if age_hours > 24:
            score += 15
        elif age_hours > 12:
            score += 10
        elif age_hours > 6:
            score += 5
        
        # Add score based on product data
        if alert.alert_data:
            days_until_empty = alert.alert_data.get('days_until_empty')
            if days_until_empty is not None:
                if days_until_empty <= 1:
                    score += 20
                elif days_until_empty <= 3:
                    score += 15
                elif days_until_empty <= 7:
                    score += 10
        
        return min(score, 100)  # Cap at 100
    
    @staticmethod
    def _get_suggested_action(alert: Alert) -> str:
        """Get suggested action for an alert"""
        if alert.alert_type == AlertType.OUT_OF_STOCK:
            return "Restock immediately"
        elif alert.alert_type == AlertType.CRITICAL_STOCK:
            return "Order inventory urgently"
        elif alert.alert_type == AlertType.LOW_STOCK:
            return "Schedule restock order"
        else:
            return "Review and take action"
    
    @staticmethod
    def _format_time_ago(timestamp: datetime) -> str:
        """Format timestamp as 'time ago' string"""
        now = datetime.utcnow()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    @staticmethod
    def get_active_alerts() -> List[Alert]:
        """
        Get all active alerts
        
        Returns:
            List of active Alert objects
        """
        return Alert.query.filter_by(status=AlertStatus.ACTIVE).order_by(Alert.created_at.desc()).all()
    
    @staticmethod
    def get_active_low_stock_alerts() -> List[Alert]:
        """
        Get active low stock alerts
        
        Returns:
            List of active low stock Alert objects
        """
        return Alert.query.filter(
            and_(
                Alert.status == AlertStatus.ACTIVE,
                Alert.alert_type.in_([
                    AlertType.LOW_STOCK,
                    AlertType.OUT_OF_STOCK,
                    AlertType.CRITICAL_STOCK
                ])
            )
        ).order_by(Alert.created_at.desc()).all()
    
    @staticmethod
    def create_low_stock_alert(product: Product) -> Alert:
        """
        Create a low stock alert for a product
        
        Args:
            product: Product object to create alert for
            
        Returns:
            Created Alert object
        """
        # Check if there's already an active alert for this product
        existing_alert = Alert.query.filter_by(
            product_id=product.id,
            status=AlertStatus.ACTIVE
        ).filter(
            Alert.alert_type.in_([
                AlertType.LOW_STOCK,
                AlertType.OUT_OF_STOCK,
                AlertType.CRITICAL_STOCK
            ])
        ).first()
        
        if existing_alert:
            # Update existing alert
            AlertService._update_existing_stock_alert(existing_alert, product)
            db.session.commit()
            return existing_alert
        
        # Determine alert type and severity
        if product.quantity == 0:
            alert_type = AlertType.OUT_OF_STOCK
            severity = AlertSeverity.CRITICAL
            title = f"Out of Stock: {product.name}"
            message = f"Product '{product.name}' is completely out of stock."
        elif product.quantity <= 5:
            alert_type = AlertType.CRITICAL_STOCK
            severity = AlertSeverity.CRITICAL
            title = f"Critical Stock Level: {product.name}"
            message = f"Product '{product.name}' has only {product.quantity} units left."
        else:
            alert_type = AlertType.LOW_STOCK
            severity = AlertSeverity.WARNING
            title = f"Low Stock: {product.name}"
            message = f"Product '{product.name}' is running low with {product.quantity} units."
        
        # Create alert data
        alert_data = {
            'current_stock': product.quantity,
            'threshold': product.low_stock_threshold,
            'category': product.category,
            'suggested_reorder_quantity': AlertService._calculate_suggested_reorder_quantity(product)
        }
        
        # Create new alert
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            product_id=product.id,
            alert_data=alert_data
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return alert
    
    @staticmethod
    def resolve_low_stock_alert(product: Product) -> bool:
        """
        Resolve low stock alert for a product if stock is restored
        
        Args:
            product: Product object to resolve alert for
            
        Returns:
            True if alert was resolved, False otherwise
        """
        active_alert = Alert.query.filter_by(
            product_id=product.id,
            status=AlertStatus.ACTIVE
        ).filter(
            Alert.alert_type.in_([
                AlertType.LOW_STOCK,
                AlertType.OUT_OF_STOCK,
                AlertType.CRITICAL_STOCK
            ])
        ).first()
        
        if active_alert and product.quantity > product.low_stock_threshold:
            active_alert.resolve()
            active_alert.alert_data = active_alert.alert_data or {}
            active_alert.alert_data['auto_resolved'] = True
            active_alert.alert_data['resolved_stock_level'] = product.quantity
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def _calculate_system_health_score() -> int:
        """Calculate overall system health score (0-100)"""
        # Get total products and alert counts
        total_products = Product.query.filter_by(is_active=True).count()
        if total_products == 0:
            return 100
        
        critical_alerts = Alert.query.filter_by(
            severity=AlertSeverity.CRITICAL,
            status=AlertStatus.ACTIVE
        ).count()
        
        warning_alerts = Alert.query.filter_by(
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE
        ).count()
        
        # Calculate health score
        # Critical alerts have more impact on health score
        health_impact = (critical_alerts * 10) + (warning_alerts * 5)
        health_percentage = max(0, 100 - (health_impact / total_products * 100))
        
        return int(health_percentage)