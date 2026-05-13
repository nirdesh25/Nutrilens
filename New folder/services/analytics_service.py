"""
Analytics Service for Smart Inventory Management System
Provides data processing and dashboard metrics calculation
"""

from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func, and_, or_
from extensions import db
from models.sale import Sale
from models.product import Product
from models.user import User
from models.purchase_request import PurchaseRequest


class AnalyticsService:
    """Service for analytics data processing and dashboard metrics"""
    
    @staticmethod
    def get_dashboard_metrics(days: int = 30) -> Dict:
        """
        Get comprehensive dashboard metrics
        
        Args:
            days: Number of days to analyze (default: 30)
            
        Returns:
            Dictionary containing dashboard metrics
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Sales metrics
        sales_summary = Sale.get_sales_summary(start_date, end_date)
        
        # Product metrics
        total_products = Product.query.count()
        low_stock_products = AnalyticsService.get_low_stock_products()
        out_of_stock_count = Product.query.filter_by(quantity=0).count()
        
        # Customer metrics
        total_customers = User.query.filter_by(role='customer').count()
        active_customers = AnalyticsService.get_active_customers_count(days)
        
        # Purchase request metrics
        pending_requests = PurchaseRequest.query.filter_by(status='pending').count()
        total_requests = PurchaseRequest.query.count()
        
        # Recent activity
        recent_sales = Sale.get_recent_sales(7)  # Last 7 days
        top_products = Sale.get_top_selling_products(5, days)
        
        return {
            'sales_metrics': {
                'total_sales': sales_summary['total_sales'],
                'total_revenue': sales_summary['total_revenue'],
                'average_sale_amount': sales_summary['average_sale_amount'],
                'total_quantity_sold': sales_summary['total_quantity']
            },
            'product_metrics': {
                'total_products': total_products,
                'low_stock_count': len(low_stock_products),
                'out_of_stock_count': out_of_stock_count,
                'stock_health_percentage': AnalyticsService._calculate_stock_health_percentage()
            },
            'customer_metrics': {
                'total_customers': total_customers,
                'active_customers': active_customers,
                'customer_activity_rate': (active_customers / total_customers * 100) if total_customers > 0 else 0
            },
            'request_metrics': {
                'pending_requests': pending_requests,
                'total_requests': total_requests,
                'approval_rate': AnalyticsService._calculate_approval_rate()
            },
            'recent_activity': {
                'recent_sales_count': len(recent_sales),
                'top_products': [
                    {
                        'product_id': item.product_id,
                        'product_name': Product.query.get(item.product_id).name if Product.query.get(item.product_id) else 'Unknown',
                        'total_quantity': item.total_quantity,
                        'total_revenue': float(item.total_revenue)
                    }
                    for item in top_products
                ]
            },
            'period_info': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days_analyzed': days
            }
        }
    
    @staticmethod
    def get_sales_chart_data(days: int = 30) -> Dict:
        """
        Get sales data formatted for charts
        
        Args:
            days: Number of days to include
            
        Returns:
            Dictionary with chart-ready data
        """
        daily_data = Sale.get_daily_sales_data(days)
        
        # Prepare data for different chart types
        dates = [item['date'] for item in daily_data]
        sales_counts = [item['sales_count'] for item in daily_data]
        revenues = [item['revenue'] for item in daily_data]
        
        # Calculate trends
        revenue_trend = AnalyticsService._calculate_trend(revenues)
        sales_trend = AnalyticsService._calculate_trend(sales_counts)
        
        return {
            'daily_sales': {
                'labels': dates,
                'sales_count': sales_counts,
                'revenue': revenues
            },
            'trends': {
                'revenue_trend': revenue_trend,
                'sales_trend': sales_trend
            },
            'summary': {
                'total_days': len(daily_data),
                'total_sales': sum(sales_counts),
                'total_revenue': sum(revenues),
                'average_daily_sales': sum(sales_counts) / len(daily_data) if daily_data else 0,
                'average_daily_revenue': sum(revenues) / len(daily_data) if daily_data else 0
            }
        }
    
    @staticmethod
    def get_product_performance_data(days: int = 30) -> Dict:
        """
        Get product performance analytics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with product performance data
        """
        top_products = Sale.get_top_selling_products(10, days)
        
        # Get detailed product data
        product_data = []
        for item in top_products:
            product = Product.query.get(item.product_id)
            if product:
                # Calculate profit for this product
                sales = Sale.get_product_sales(item.product_id)
                recent_sales = [s for s in sales if s.sale_date >= datetime.utcnow() - timedelta(days=days)]
                total_profit = sum(s.profit for s in recent_sales)
                
                product_data.append({
                    'product_id': product.id,
                    'name': product.name,
                    'category': product.category,
                    'total_quantity_sold': item.total_quantity,
                    'total_revenue': float(item.total_revenue),
                    'total_profit': float(total_profit),
                    'current_stock': product.quantity,
                    'stock_status': AnalyticsService._get_stock_status(product),
                    'profit_margin': float(total_profit / item.total_revenue * 100) if item.total_revenue > 0 else 0
                })
        
        # Category performance
        category_performance = AnalyticsService._get_category_performance(days)
        
        return {
            'top_products': product_data,
            'category_performance': category_performance,
            'analysis_period': days
        }
    
    @staticmethod
    def get_low_stock_alerts() -> List[Dict]:
        """
        Get low stock alerts for dashboard
        
        Returns:
            List of low stock alerts
        """
        low_stock_products = AnalyticsService.get_low_stock_products()
        
        alerts = []
        for product in low_stock_products:
            # Calculate days until out of stock based on recent sales
            days_until_empty = AnalyticsService._calculate_days_until_empty(product)
            
            alert_level = 'critical' if product.quantity == 0 else 'warning' if product.quantity <= 5 else 'info'
            
            alerts.append({
                'product_id': product.id,
                'product_name': product.name,
                'category': product.category,
                'current_stock': product.quantity,
                'threshold': product.low_stock_threshold,
                'alert_level': alert_level,
                'days_until_empty': days_until_empty,
                'suggested_reorder': max(product.low_stock_threshold * 2, 10),
                'message': AnalyticsService._generate_alert_message(product, days_until_empty)
            })
        
        # Sort by urgency (out of stock first, then by days until empty)
        alerts.sort(key=lambda x: (x['current_stock'] == 0, x['days_until_empty'] if x['days_until_empty'] else float('inf')))
        
        return alerts
    
    @staticmethod
    def get_low_stock_products() -> List[Product]:
        """
        Get products with low stock levels
        
        Returns:
            List of products with stock below threshold
        """
        return Product.query.filter(
            or_(
                Product.quantity <= Product.low_stock_threshold,
                Product.quantity == 0
            )
        ).order_by(Product.quantity.asc()).all()
    
    @staticmethod
    def get_customer_analytics(days: int = 30) -> Dict:
        """
        Get customer analytics data
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with customer analytics
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Top customers by revenue
        top_customers = db.session.query(
            Sale.customer_id,
            func.sum(Sale.total_amount).label('total_spent'),
            func.count(Sale.id).label('purchase_count')
        ).filter(
            Sale.sale_date >= start_date
        ).group_by(
            Sale.customer_id
        ).order_by(
            func.sum(Sale.total_amount).desc()
        ).limit(10).all()
        
        # Customer activity data
        customer_data = []
        for customer_stat in top_customers:
            customer = User.query.get(customer_stat.customer_id)
            if customer:
                customer_data.append({
                    'customer_id': customer.id,
                    'name': customer.full_name,
                    'email': customer.email,
                    'total_spent': float(customer_stat.total_spent),
                    'purchase_count': customer_stat.purchase_count,
                    'average_order_value': float(customer_stat.total_spent / customer_stat.purchase_count),
                    'last_purchase': AnalyticsService._get_last_purchase_date(customer.id)
                })
        
        # Customer segments
        segments = AnalyticsService._analyze_customer_segments(days)
        
        return {
            'top_customers': customer_data,
            'customer_segments': segments,
            'total_active_customers': len(customer_data),
            'analysis_period': days
        }
    
    @staticmethod
    def get_active_customers_count(days: int = 30) -> int:
        """
        Get count of customers who made purchases in the specified period
        
        Args:
            days: Number of days to look back
            
        Returns:
            Count of active customers
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return db.session.query(Sale.customer_id).filter(
            Sale.sale_date >= cutoff_date
        ).distinct().count()
    
    # Private helper methods
    
    @staticmethod
    def _calculate_stock_health_percentage() -> float:
        """Calculate overall stock health percentage"""
        total_products = Product.query.count()
        if total_products == 0:
            return 100.0
        
        healthy_products = Product.query.filter(
            Product.quantity > Product.low_stock_threshold
        ).count()
        
        return (healthy_products / total_products) * 100
    
    @staticmethod
    def _calculate_approval_rate() -> float:
        """Calculate purchase request approval rate"""
        total_processed = PurchaseRequest.query.filter(
            PurchaseRequest.status.in_(['approved', 'rejected'])
        ).count()
        
        if total_processed == 0:
            return 0.0
        
        approved = PurchaseRequest.query.filter_by(status='approved').count()
        return (approved / total_processed) * 100
    
    @staticmethod
    def _calculate_trend(values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 2:
            return 'stable'
        
        # Simple trend calculation: compare first half with second half
        mid_point = len(values) // 2
        first_half_avg = sum(values[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(values[mid_point:]) / (len(values) - mid_point)
        
        if second_half_avg > first_half_avg * 1.1:  # 10% increase threshold
            return 'increasing'
        elif second_half_avg < first_half_avg * 0.9:  # 10% decrease threshold
            return 'decreasing'
        else:
            return 'stable'
    
    @staticmethod
    def _get_stock_status(product: Product) -> str:
        """Get stock status for a product"""
        if product.quantity == 0:
            return 'out_of_stock'
        elif product.quantity <= product.low_stock_threshold:
            return 'low_stock'
        else:
            return 'in_stock'
    
    @staticmethod
    def _get_category_performance(days: int) -> List[Dict]:
        """Get performance data by product category"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        category_data = db.session.query(
            Product.category,
            func.sum(Sale.quantity).label('total_quantity'),
            func.sum(Sale.total_amount).label('total_revenue'),
            func.count(Sale.id).label('sales_count')
        ).join(
            Sale, Product.id == Sale.product_id
        ).filter(
            Sale.sale_date >= start_date
        ).group_by(
            Product.category
        ).order_by(
            func.sum(Sale.total_amount).desc()
        ).all()
        
        return [
            {
                'category': item.category,
                'total_quantity': item.total_quantity,
                'total_revenue': float(item.total_revenue),
                'sales_count': item.sales_count,
                'average_sale_value': float(item.total_revenue / item.sales_count) if item.sales_count > 0 else 0
            }
            for item in category_data
        ]
    
    @staticmethod
    def _calculate_days_until_empty(product: Product) -> Optional[int]:
        """Calculate estimated days until product runs out of stock"""
        if product.quantity == 0:
            return 0
        
        # Get average daily sales for the last 30 days
        recent_sales = Sale.get_product_sales(product.id)
        if not recent_sales:
            return None
        
        # Filter to last 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        recent_sales = [s for s in recent_sales if s.sale_date >= cutoff_date]
        
        if not recent_sales:
            return None
        
        total_sold = sum(s.quantity for s in recent_sales)
        days_with_sales = len(set(s.sale_date.date() for s in recent_sales))
        
        if days_with_sales == 0:
            return None
        
        average_daily_sales = total_sold / days_with_sales
        
        if average_daily_sales <= 0:
            return None
        
        return int(product.quantity / average_daily_sales)
    
    @staticmethod
    def _generate_alert_message(product: Product, days_until_empty: Optional[int]) -> str:
        """Generate alert message for low stock product"""
        if product.quantity == 0:
            return f"{product.name} is out of stock!"
        elif days_until_empty is not None and days_until_empty <= 7:
            return f"{product.name} will run out in approximately {days_until_empty} days"
        elif product.quantity <= product.low_stock_threshold:
            return f"{product.name} is running low (only {product.quantity} left)"
        else:
            return f"{product.name} stock level is below threshold"
    
    @staticmethod
    def _get_last_purchase_date(customer_id: int) -> Optional[str]:
        """Get the last purchase date for a customer"""
        last_sale = Sale.query.filter_by(customer_id=customer_id).order_by(
            Sale.sale_date.desc()
        ).first()
        
        return last_sale.sale_date.isoformat() if last_sale else None
    
    @staticmethod
    def _analyze_customer_segments(days: int) -> Dict:
        """Analyze customer segments based on purchase behavior"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get customer spending data
        customer_spending = db.session.query(
            Sale.customer_id,
            func.sum(Sale.total_amount).label('total_spent'),
            func.count(Sale.id).label('purchase_count')
        ).filter(
            Sale.sale_date >= start_date
        ).group_by(
            Sale.customer_id
        ).all()
        
        if not customer_spending:
            return {
                'high_value': 0,
                'medium_value': 0,
                'low_value': 0,
                'one_time': 0
            }
        
        # Calculate thresholds
        spending_amounts = [float(cs.total_spent) for cs in customer_spending]
        spending_amounts.sort(reverse=True)
        
        # Define segments (top 20%, middle 60%, bottom 20%)
        total_customers = len(spending_amounts)
        high_threshold_index = int(total_customers * 0.2)
        low_threshold_index = int(total_customers * 0.8)
        
        high_threshold = spending_amounts[high_threshold_index] if high_threshold_index < len(spending_amounts) else 0
        low_threshold = spending_amounts[low_threshold_index] if low_threshold_index < len(spending_amounts) else 0
        
        segments = {
            'high_value': 0,
            'medium_value': 0,
            'low_value': 0,
            'one_time': 0
        }
        
        for cs in customer_spending:
            if cs.purchase_count == 1:
                segments['one_time'] += 1
            elif cs.total_spent >= high_threshold:
                segments['high_value'] += 1
            elif cs.total_spent >= low_threshold:
                segments['medium_value'] += 1
            else:
                segments['low_value'] += 1
        
        return segments