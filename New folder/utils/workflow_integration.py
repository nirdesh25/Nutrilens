"""
Workflow integration utilities for Smart Inventory Management System
Connects all system components and ensures proper data flow
"""

from datetime import datetime, timedelta
from decimal import Decimal
from flask import current_app
from extensions import db
from models.user import User
from models.product import Product
from models.purchase_request import PurchaseRequest
from models.sale import Sale
from models.ai_prediction import AIPrediction
from models.alert import Alert
from services.ai_prediction_service import AIPredictionService
from services.restocking_service import RestockingService
from services.analytics_service import AnalyticsService
from services.alert_service import AlertService
from services.notification_service import NotificationService


class WorkflowIntegrator:
    """
    Central class for managing workflow integration across all system components
    """
    
    def __init__(self):
        self.ai_service = AIPredictionService()
        self.restocking_service = RestockingService()
        self.analytics_service = AnalyticsService()
        self.alert_service = AlertService()
        self.notification_service = NotificationService()
    
    def process_purchase_request_approval(self, purchase_request, admin_user):
        """
        Complete workflow for purchase request approval
        
        Args:
            purchase_request: PurchaseRequest object
            admin_user: Admin user processing the request
        
        Returns:
            dict: Results of the approval process
        """
        try:
            # 1. Validate request can be processed
            if not purchase_request.can_be_processed():
                return {
                    'success': False,
                    'error': 'Request has already been processed'
                }
            
            # 2. Check product availability
            product = purchase_request.product
            if not product.can_fulfill_quantity(purchase_request.quantity):
                return {
                    'success': False,
                    'error': f'Insufficient stock. Available: {product.quantity}, Requested: {purchase_request.quantity}'
                }
            
            # 3. Approve the request
            purchase_request.approve(admin_user.id)
            
            # 4. Create sale record
            sale = Sale(
                purchase_request_id=purchase_request.id,
                product_id=purchase_request.product_id,
                customer_id=purchase_request.customer_id,
                quantity=purchase_request.quantity,
                unit_price=product.selling_price,
                total_amount=product.selling_price * purchase_request.quantity
            )
            db.session.add(sale)
            
            # 5. Update product stock
            product.reduce_stock(purchase_request.quantity)
            
            # 6. Check for low stock alerts
            if product.is_low_stock():
                self.alert_service.create_low_stock_alert(product)
            
            # 7. Trigger AI prediction update if significant stock change
            if purchase_request.quantity >= product.low_stock_threshold:
                self._trigger_ai_prediction_update(product)
            
            # 8. Send notifications
            self.notification_service.send_purchase_approval_notification(
                purchase_request.customer, purchase_request, sale
            )
            
            # 9. Update analytics cache
            self._update_analytics_cache()
            
            db.session.commit()
            
            return {
                'success': True,
                'sale_id': sale.id,
                'new_stock_level': product.quantity,
                'low_stock_alert': product.is_low_stock()
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error processing purchase approval: {str(e)}")
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}'
            }
    
    def process_purchase_request_rejection(self, purchase_request, admin_user, reason):
        """
        Complete workflow for purchase request rejection
        
        Args:
            purchase_request: PurchaseRequest object
            admin_user: Admin user processing the request
            reason: Rejection reason
        
        Returns:
            dict: Results of the rejection process
        """
        try:
            # 1. Validate request can be processed
            if not purchase_request.can_be_processed():
                return {
                    'success': False,
                    'error': 'Request has already been processed'
                }
            
            # 2. Reject the request
            purchase_request.reject(admin_user.id, reason)
            
            # 3. Send notification to customer
            self.notification_service.send_purchase_rejection_notification(
                purchase_request.customer, purchase_request, reason
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Request rejected successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error processing purchase rejection: {str(e)}")
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}'
            }
    
    def process_new_product_creation(self, product_data, admin_user):
        """
        Complete workflow for new product creation
        
        Args:
            product_data: Dictionary with product information
            admin_user: Admin user creating the product
        
        Returns:
            dict: Results of the creation process
        """
        try:
            # 1. Create product
            product = Product(
                name=product_data['name'],
                category=product_data['category'],
                cost_price=Decimal(str(product_data['cost_price'])),
                selling_price=Decimal(str(product_data['selling_price'])),
                quantity=product_data['quantity'],
                description=product_data.get('description'),
                low_stock_threshold=product_data.get('low_stock_threshold', 10)
            )
            
            db.session.add(product)
            db.session.flush()  # Get product ID
            
            # 2. Check if initial stock is low
            if product.is_low_stock():
                self.alert_service.create_low_stock_alert(product)
            
            # 3. Initialize AI prediction baseline if we have historical data
            self._initialize_product_ai_baseline(product)
            
            # 4. Update analytics cache
            self._update_analytics_cache()
            
            db.session.commit()
            
            return {
                'success': True,
                'product_id': product.id,
                'low_stock_alert': product.is_low_stock()
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating product: {str(e)}")
            return {
                'success': False,
                'error': f'Product creation failed: {str(e)}'
            }
    
    def process_stock_update(self, product_id, quantity_change, operation='set', admin_user=None):
        """
        Complete workflow for stock updates
        
        Args:
            product_id: ID of the product
            quantity_change: Quantity to change
            operation: 'set', 'add', or 'subtract'
            admin_user: Admin user making the change
        
        Returns:
            dict: Results of the stock update
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                return {
                    'success': False,
                    'error': 'Product not found'
                }
            
            old_quantity = product.quantity
            
            # 1. Update stock based on operation
            if operation == 'set':
                product.update_stock(quantity_change)
            elif operation == 'add':
                product.increase_stock(quantity_change)
            elif operation == 'subtract':
                product.reduce_stock(quantity_change)
            else:
                return {
                    'success': False,
                    'error': 'Invalid operation'
                }
            
            # 2. Check for stock level changes
            was_low_stock = old_quantity <= product.low_stock_threshold
            is_now_low_stock = product.is_low_stock()
            
            # 3. Handle alert creation/resolution
            if not was_low_stock and is_now_low_stock:
                self.alert_service.create_low_stock_alert(product)
            elif was_low_stock and not is_now_low_stock:
                self.alert_service.resolve_low_stock_alert(product)
            
            # 4. Trigger AI prediction update for significant changes
            if abs(quantity_change) >= product.low_stock_threshold:
                self._trigger_ai_prediction_update(product)
            
            # 5. Update analytics cache
            self._update_analytics_cache()
            
            db.session.commit()
            
            return {
                'success': True,
                'old_quantity': old_quantity,
                'new_quantity': product.quantity,
                'low_stock_alert': is_now_low_stock,
                'alert_status_changed': was_low_stock != is_now_low_stock
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating stock: {str(e)}")
            return {
                'success': False,
                'error': f'Stock update failed: {str(e)}'
            }
    
    def process_ai_restocking_suggestions(self, min_confidence=0.6, budget_limit=None):
        """
        Generate and process AI restocking suggestions
        
        Args:
            min_confidence: Minimum confidence threshold
            budget_limit: Optional budget constraint
        
        Returns:
            dict: AI suggestions with integrated data
        """
        try:
            # 1. Generate AI suggestions
            suggestions = self.restocking_service.generate_comprehensive_suggestions(
                min_confidence=min_confidence,
                budget_limit=budget_limit
            )
            
            # 2. Integrate with current alerts
            current_alerts = self.alert_service.get_active_low_stock_alerts()
            alert_product_ids = {alert.product_id for alert in current_alerts}
            
            # 3. Enhance suggestions with alert information
            for suggestion in suggestions.get('suggestions', []):
                suggestion['has_active_alert'] = suggestion['product_id'] in alert_product_ids
                
                # Add recent sales velocity
                product = Product.query.get(suggestion['product_id'])
                if product:
                    recent_sales = self._get_recent_sales_velocity(product, days=30)
                    suggestion['recent_sales_velocity'] = recent_sales
            
            # 4. Sort by urgency and alert status
            suggestions['suggestions'].sort(
                key=lambda x: (x.get('has_active_alert', False), x.get('urgency_score', 0)),
                reverse=True
            )
            
            return {
                'success': True,
                'data': suggestions,
                'integration_info': {
                    'active_alerts_count': len(current_alerts),
                    'suggestions_with_alerts': len([s for s in suggestions.get('suggestions', []) if s.get('has_active_alert')])
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error processing AI suggestions: {str(e)}")
            return {
                'success': False,
                'error': f'AI suggestions failed: {str(e)}'
            }
    
    def process_dashboard_data_integration(self, days=30):
        """
        Integrate data from all components for dashboard display
        
        Args:
            days: Number of days to analyze
        
        Returns:
            dict: Integrated dashboard data
        """
        try:
            # 1. Get analytics data
            analytics_data = self.analytics_service.get_dashboard_metrics(days)
            
            # 2. Get AI suggestions summary
            ai_suggestions = self.restocking_service.generate_comprehensive_suggestions(min_confidence=0.7)
            top_suggestions = sorted(
                ai_suggestions.get('suggestions', []),
                key=lambda x: x.get('urgency_score', 0),
                reverse=True
            )[:5]
            
            # 3. Get active alerts
            active_alerts = self.alert_service.get_active_alerts()
            
            # 4. Get recent activity
            recent_sales = Sale.get_recent_sales(7)
            recent_requests = PurchaseRequest.query.order_by(
                PurchaseRequest.requested_at.desc()
            ).limit(10).all()
            
            # 5. Integrate all data
            integrated_data = {
                'analytics': analytics_data,
                'ai_insights': {
                    'top_suggestions': top_suggestions,
                    'total_suggestions': len(ai_suggestions.get('suggestions', [])),
                    'high_priority_count': len([s for s in ai_suggestions.get('suggestions', []) if s.get('urgency_level') == 'critical'])
                },
                'alerts': {
                    'active_alerts': [alert.to_dict() for alert in active_alerts],
                    'total_count': len(active_alerts),
                    'critical_count': len([a for a in active_alerts if a.severity == 'critical'])
                },
                'recent_activity': {
                    'recent_sales': [sale.to_dict() for sale in recent_sales],
                    'recent_requests': [req.to_dict() for req in recent_requests]
                },
                'system_health': self._get_system_health_status()
            }
            
            return {
                'success': True,
                'data': integrated_data
            }
            
        except Exception as e:
            current_app.logger.error(f"Error integrating dashboard data: {str(e)}")
            return {
                'success': False,
                'error': f'Dashboard integration failed: {str(e)}'
            }
    
    def _trigger_ai_prediction_update(self, product):
        """
        Trigger AI prediction update for a product
        
        Args:
            product: Product object
        """
        try:
            # Generate new prediction
            prediction = self.ai_service.predict_demand(product.id, 'monthly')
            if prediction:
                current_app.logger.info(f"Updated AI prediction for product {product.id}")
        except Exception as e:
            current_app.logger.error(f"Error updating AI prediction for product {product.id}: {str(e)}")
    
    def _initialize_product_ai_baseline(self, product):
        """
        Initialize AI baseline for new product
        
        Args:
            product: Product object
        """
        try:
            # Create initial prediction based on category averages
            category_products = Product.query.filter_by(category=product.category).all()
            if len(category_products) > 1:  # Exclude the new product itself
                # Use category average for initial prediction
                avg_sales = self._get_category_average_sales(product.category)
                if avg_sales > 0:
                    initial_prediction = AIPrediction(
                        product_id=product.id,
                        predicted_demand=int(avg_sales),
                        confidence_score=Decimal('0.5'),  # Low confidence for new product
                        prediction_period='monthly',
                        prediction_date=datetime.utcnow()
                    )
                    db.session.add(initial_prediction)
        except Exception as e:
            current_app.logger.error(f"Error initializing AI baseline for product {product.id}: {str(e)}")
    
    def _get_recent_sales_velocity(self, product, days=30):
        """
        Get recent sales velocity for a product
        
        Args:
            product: Product object
            days: Number of days to analyze
        
        Returns:
            float: Sales velocity (units per day)
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            recent_sales = Sale.query.filter(
                Sale.product_id == product.id,
                Sale.sale_date >= cutoff_date
            ).all()
            
            total_quantity = sum(sale.quantity for sale in recent_sales)
            return total_quantity / days if days > 0 else 0
        except Exception as e:
            current_app.logger.error(f"Error calculating sales velocity for product {product.id}: {str(e)}")
            return 0
    
    def _get_category_average_sales(self, category, days=90):
        """
        Get average sales for products in a category
        
        Args:
            category: Product category
            days: Number of days to analyze
        
        Returns:
            float: Average sales per product in category
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            category_products = Product.query.filter_by(category=category).all()
            
            if not category_products:
                return 0
            
            total_sales = 0
            for product in category_products:
                product_sales = Sale.query.filter(
                    Sale.product_id == product.id,
                    Sale.sale_date >= cutoff_date
                ).all()
                total_sales += sum(sale.quantity for sale in product_sales)
            
            return total_sales / len(category_products) if category_products else 0
        except Exception as e:
            current_app.logger.error(f"Error calculating category average for {category}: {str(e)}")
            return 0
    
    def _update_analytics_cache(self):
        """
        Update analytics cache after data changes
        """
        try:
            # In a production system, this would update Redis cache
            # For now, just log the cache update
            current_app.logger.info("Analytics cache updated")
        except Exception as e:
            current_app.logger.error(f"Error updating analytics cache: {str(e)}")
    
    def _get_system_health_status(self):
        """
        Get overall system health status
        
        Returns:
            dict: System health information
        """
        try:
            # Check various system components
            total_products = Product.query.filter_by(is_active=True).count()
            low_stock_count = len(Product.get_low_stock_products())
            pending_requests = PurchaseRequest.query.filter_by(status='pending').count()
            active_users = User.query.filter_by(is_active=True).count()
            
            # Calculate health score
            health_score = 100
            if total_products > 0:
                low_stock_percentage = (low_stock_count / total_products) * 100
                if low_stock_percentage > 20:
                    health_score -= 20
                elif low_stock_percentage > 10:
                    health_score -= 10
            
            if pending_requests > 10:
                health_score -= 15
            
            # Determine status
            if health_score >= 90:
                status = 'excellent'
            elif health_score >= 75:
                status = 'good'
            elif health_score >= 60:
                status = 'fair'
            else:
                status = 'poor'
            
            return {
                'status': status,
                'health_score': health_score,
                'metrics': {
                    'total_products': total_products,
                    'low_stock_count': low_stock_count,
                    'pending_requests': pending_requests,
                    'active_users': active_users
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting system health status: {str(e)}")
            return {
                'status': 'unknown',
                'health_score': 0,
                'error': str(e)
            }


# Global workflow integrator instance
workflow_integrator = WorkflowIntegrator()