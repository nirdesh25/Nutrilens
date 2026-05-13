"""
Customer Service for analytics, tracking, and management
"""
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, desc, and_
from extensions import db
from models.user import User
from models.purchase_request import PurchaseRequest
from models.sale import Sale
from models.product import Product


class CustomerService:
    """Service for customer analytics, tracking, and management"""
    
    @staticmethod
    def get_all_customers():
        """Get all customers with basic info"""
        return User.query.filter_by(role=User.ROLE_CUSTOMER, is_active=True).all()
    
    @staticmethod
    def get_customer_by_id(customer_id):
        """Get customer by ID"""
        return User.query.filter_by(
            id=customer_id, 
            role=User.ROLE_CUSTOMER, 
            is_active=True
        ).first()
    
    @staticmethod
    def get_customer_activity_summary(customer_id, days=30):
        """Get comprehensive activity summary for a customer"""
        customer = CustomerService.get_customer_by_id(customer_id)
        if not customer:
            return None
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get purchase requests in the period
        requests = PurchaseRequest.query.filter(
            PurchaseRequest.customer_id == customer_id,
            PurchaseRequest.requested_at >= cutoff_date
        ).all()
        
        # Get sales in the period
        sales = Sale.query.filter(
            Sale.customer_id == customer_id,
            Sale.sale_date >= cutoff_date
        ).all()
        
        # Calculate metrics
        total_requests = len(requests)
        approved_requests = len([r for r in requests if r.is_approved()])
        rejected_requests = len([r for r in requests if r.is_rejected()])
        pending_requests = len([r for r in requests if r.is_pending()])
        
        total_spent = sum(sale.total_amount for sale in sales)
        total_items_purchased = sum(sale.quantity for sale in sales)
        
        approval_rate = (approved_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'customer': customer.to_dict(),
            'period_days': days,
            'activity_summary': {
                'total_requests': total_requests,
                'approved_requests': approved_requests,
                'rejected_requests': rejected_requests,
                'pending_requests': pending_requests,
                'approval_rate': round(approval_rate, 2),
                'total_spent': float(total_spent),
                'total_items_purchased': total_items_purchased,
                'average_order_value': float(total_spent / approved_requests) if approved_requests > 0 else 0
            },
            'recent_requests': [req.to_dict() for req in requests[-5:]],
            'recent_purchases': [sale.to_dict() for sale in sales[-5:]]
        }
    
    @staticmethod
    def get_customer_purchase_patterns(customer_id):
        """Analyze customer purchase patterns and preferences"""
        customer = CustomerService.get_customer_by_id(customer_id)
        if not customer:
            return None
        
        # Get all customer sales
        sales = Sale.query.filter_by(customer_id=customer_id).all()
        
        if not sales:
            return {
                'customer': customer.to_dict(),
                'has_purchase_history': False,
                'message': 'No purchase history available'
            }
        
        # Analyze purchase patterns
        product_purchases = {}
        category_purchases = {}
        monthly_spending = {}
        
        for sale in sales:
            # Product analysis
            product_name = sale.product.name if sale.product else 'Unknown'
            if product_name not in product_purchases:
                product_purchases[product_name] = {
                    'quantity': 0,
                    'total_spent': Decimal('0'),
                    'purchase_count': 0
                }
            product_purchases[product_name]['quantity'] += sale.quantity
            product_purchases[product_name]['total_spent'] += sale.total_amount
            product_purchases[product_name]['purchase_count'] += 1
            
            # Category analysis
            category = sale.product.category if sale.product else 'Unknown'
            if category not in category_purchases:
                category_purchases[category] = {
                    'quantity': 0,
                    'total_spent': Decimal('0'),
                    'purchase_count': 0
                }
            category_purchases[category]['quantity'] += sale.quantity
            category_purchases[category]['total_spent'] += sale.total_amount
            category_purchases[category]['purchase_count'] += 1
            
            # Monthly spending analysis
            month_key = sale.sale_date.strftime('%Y-%m')
            if month_key not in monthly_spending:
                monthly_spending[month_key] = Decimal('0')
            monthly_spending[month_key] += sale.total_amount
        
        # Sort and get top items
        top_products = sorted(
            product_purchases.items(),
            key=lambda x: x[1]['total_spent'],
            reverse=True
        )[:5]
        
        top_categories = sorted(
            category_purchases.items(),
            key=lambda x: x[1]['total_spent'],
            reverse=True
        )[:3]
        
        # Calculate customer metrics
        total_spent = sum(sale.total_amount for sale in sales)
        total_purchases = len(sales)
        average_order_value = total_spent / total_purchases if total_purchases > 0 else 0
        
        # Calculate purchase frequency (purchases per month)
        first_purchase = min(sale.sale_date for sale in sales)
        months_active = max(1, (datetime.utcnow() - first_purchase).days / 30)
        purchase_frequency = total_purchases / months_active
        
        return {
            'customer': customer.to_dict(),
            'has_purchase_history': True,
            'lifetime_metrics': {
                'total_spent': float(total_spent),
                'total_purchases': total_purchases,
                'average_order_value': float(average_order_value),
                'first_purchase_date': first_purchase.isoformat(),
                'months_active': round(months_active, 1),
                'purchase_frequency_per_month': round(purchase_frequency, 2)
            },
            'top_products': [
                {
                    'product_name': name,
                    'quantity_purchased': data['quantity'],
                    'total_spent': float(data['total_spent']),
                    'purchase_count': data['purchase_count']
                }
                for name, data in top_products
            ],
            'top_categories': [
                {
                    'category': name,
                    'quantity_purchased': data['quantity'],
                    'total_spent': float(data['total_spent']),
                    'purchase_count': data['purchase_count']
                }
                for name, data in top_categories
            ],
            'monthly_spending': [
                {
                    'month': month,
                    'amount': float(amount)
                }
                for month, amount in sorted(monthly_spending.items())
            ]
        }
    
    @staticmethod
    def get_customer_insights(customer_id):
        """Generate actionable insights about customer behavior"""
        patterns = CustomerService.get_customer_purchase_patterns(customer_id)
        if not patterns or not patterns['has_purchase_history']:
            return {
                'customer_id': customer_id,
                'insights': [],
                'recommendations': []
            }
        
        insights = []
        recommendations = []
        
        metrics = patterns['lifetime_metrics']
        
        # Analyze spending behavior
        if metrics['average_order_value'] > 100:
            insights.append({
                'type': 'high_value_customer',
                'message': f"High-value customer with average order value of ${metrics['average_order_value']:.2f}",
                'priority': 'high'
            })
            recommendations.append({
                'type': 'vip_treatment',
                'message': 'Consider offering VIP customer benefits or priority processing'
            })
        
        # Analyze purchase frequency
        if metrics['purchase_frequency_per_month'] > 2:
            insights.append({
                'type': 'frequent_buyer',
                'message': f"Frequent buyer with {metrics['purchase_frequency_per_month']:.1f} purchases per month",
                'priority': 'medium'
            })
            recommendations.append({
                'type': 'loyalty_program',
                'message': 'Excellent candidate for loyalty program or bulk discounts'
            })
        elif metrics['purchase_frequency_per_month'] < 0.5:
            insights.append({
                'type': 'infrequent_buyer',
                'message': f"Infrequent buyer with {metrics['purchase_frequency_per_month']:.1f} purchases per month",
                'priority': 'medium'
            })
            recommendations.append({
                'type': 'engagement',
                'message': 'Consider targeted marketing to increase engagement'
            })
        
        # Analyze product preferences
        if patterns['top_products']:
            top_product = patterns['top_products'][0]
            insights.append({
                'type': 'product_preference',
                'message': f"Prefers '{top_product['product_name']}' - {top_product['purchase_count']} purchases",
                'priority': 'low'
            })
            recommendations.append({
                'type': 'cross_sell',
                'message': f"Recommend complementary products to '{top_product['product_name']}'"
            })
        
        # Analyze category preferences
        if patterns['top_categories']:
            top_category = patterns['top_categories'][0]
            insights.append({
                'type': 'category_preference',
                'message': f"Strong preference for '{top_category['category']}' category",
                'priority': 'low'
            })
            recommendations.append({
                'type': 'new_arrivals',
                'message': f"Notify about new arrivals in '{top_category['category']}' category"
            })
        
        # Analyze recent activity
        recent_activity = CustomerService.get_customer_activity_summary(customer_id, days=30)
        if recent_activity and recent_activity['activity_summary']['total_requests'] == 0:
            insights.append({
                'type': 'inactive',
                'message': 'No recent activity in the last 30 days',
                'priority': 'high'
            })
            recommendations.append({
                'type': 'reactivation',
                'message': 'Consider sending reactivation campaign or special offers'
            })
        
        return {
            'customer_id': customer_id,
            'insights': insights,
            'recommendations': recommendations,
            'analysis_date': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_customers_overview():
        """Get overview of all customers with key metrics"""
        customers = CustomerService.get_all_customers()
        
        overview_data = []
        for customer in customers:
            # Get basic metrics
            total_requests = PurchaseRequest.query.filter_by(customer_id=customer.id).count()
            total_sales = Sale.query.filter_by(customer_id=customer.id).count()
            
            # Calculate total spent
            total_spent_result = db.session.query(
                func.sum(Sale.total_amount)
            ).filter_by(customer_id=customer.id).scalar()
            total_spent = float(total_spent_result or 0)
            
            # Get last activity
            last_request = PurchaseRequest.query.filter_by(
                customer_id=customer.id
            ).order_by(desc(PurchaseRequest.requested_at)).first()
            
            last_activity = None
            if last_request:
                last_activity = last_request.requested_at
            
            # Calculate days since last activity
            days_since_activity = None
            if last_activity:
                days_since_activity = (datetime.utcnow() - last_activity).days
            
            overview_data.append({
                'customer': customer.to_dict(),
                'metrics': {
                    'total_requests': total_requests,
                    'total_purchases': total_sales,
                    'total_spent': total_spent,
                    'last_activity': last_activity.isoformat() if last_activity else None,
                    'days_since_activity': days_since_activity
                }
            })
        
        # Sort by total spent (descending)
        overview_data.sort(key=lambda x: x['metrics']['total_spent'], reverse=True)
        
        return {
            'total_customers': len(customers),
            'customers': overview_data,
            'summary': {
                'total_customers': len(customers),
                'active_customers': len([c for c in overview_data if c['metrics']['days_since_activity'] is not None and c['metrics']['days_since_activity'] <= 30]),
                'total_customer_value': sum(c['metrics']['total_spent'] for c in overview_data)
            }
        }
    
    @staticmethod
    def get_customer_segmentation():
        """Segment customers based on purchase behavior"""
        customers_data = CustomerService.get_customers_overview()['customers']
        
        segments = {
            'high_value': [],      # High spending customers
            'frequent': [],        # Frequent buyers
            'new': [],            # New customers (< 3 months)
            'inactive': [],       # No activity in 60+ days
            'at_risk': []         # Declining activity
        }
        
        for customer_data in customers_data:
            customer = customer_data['customer']
            metrics = customer_data['metrics']
            
            # High value customers (top 20% by spending or >$500)
            if metrics['total_spent'] > 500:
                segments['high_value'].append(customer_data)
            
            # Frequent buyers (>5 purchases)
            if metrics['total_purchases'] > 5:
                segments['frequent'].append(customer_data)
            
            # New customers (registered in last 3 months)
            if customer['created_at']:
                created_date = datetime.fromisoformat(customer['created_at'].replace('Z', '+00:00'))
                if (datetime.utcnow() - created_date.replace(tzinfo=None)).days <= 90:
                    segments['new'].append(customer_data)
            
            # Inactive customers (no activity in 60+ days)
            if metrics['days_since_activity'] is None or metrics['days_since_activity'] >= 60:
                segments['inactive'].append(customer_data)
            
            # At-risk customers (activity declining)
            if metrics['days_since_activity'] and 30 <= metrics['days_since_activity'] < 60:
                segments['at_risk'].append(customer_data)
        
        return {
            'segments': {
                'high_value': {
                    'count': len(segments['high_value']),
                    'customers': segments['high_value'][:10]  # Top 10 for display
                },
                'frequent': {
                    'count': len(segments['frequent']),
                    'customers': segments['frequent'][:10]
                },
                'new': {
                    'count': len(segments['new']),
                    'customers': segments['new'][:10]
                },
                'inactive': {
                    'count': len(segments['inactive']),
                    'customers': segments['inactive'][:10]
                },
                'at_risk': {
                    'count': len(segments['at_risk']),
                    'customers': segments['at_risk'][:10]
                }
            },
            'analysis_date': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def deactivate_customer(customer_id, admin_id):
        """Deactivate a customer account"""
        customer = CustomerService.get_customer_by_id(customer_id)
        if not customer:
            raise ValueError("Customer not found")
        
        customer.is_active = False
        db.session.commit()
        
        return {
            'success': True,
            'message': f'Customer {customer.full_name} has been deactivated',
            'deactivated_by': admin_id,
            'deactivated_at': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def reactivate_customer(customer_id, admin_id):
        """Reactivate a customer account"""
        customer = User.query.filter_by(
            id=customer_id, 
            role=User.ROLE_CUSTOMER
        ).first()
        
        if not customer:
            raise ValueError("Customer not found")
        
        customer.is_active = True
        db.session.commit()
        
        return {
            'success': True,
            'message': f'Customer {customer.full_name} has been reactivated',
            'reactivated_by': admin_id,
            'reactivated_at': datetime.utcnow().isoformat()
        }