"""
Calendar Service for Smart Inventory Management System
Provides calendar-specific data processing and sales aggregation for interactive calendar views
"""

from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from sqlalchemy import func, and_
from extensions import db
from models.sale import Sale
from models.product import Product


class CalendarService:
    """Service for calendar data processing and sales aggregation"""
    
    # Color coding thresholds for sales volume
    HIGH_SALES_THRESHOLD = 1000.0  # Revenue threshold for high sales (red)
    MEDIUM_SALES_THRESHOLD = 300.0  # Revenue threshold for medium sales (yellow)
    # Low sales or no sales will be green or neutral
    
    @staticmethod
    def get_calendar_data(start_date: date, end_date: date) -> Dict:
        """
        Get calendar data for the specified date range with color coding
        
        Args:
            start_date: Start date for calendar data
            end_date: End date for calendar data
            
        Returns:
            Dictionary containing calendar events and metadata
        """
        # Get daily sales aggregation
        daily_sales = CalendarService._get_daily_sales_aggregation(start_date, end_date)
        
        # Generate calendar events with color coding
        calendar_events = []
        sales_summary = {
            'total_revenue': 0,
            'total_sales': 0,
            'high_sales_days': 0,
            'medium_sales_days': 0,
            'low_sales_days': 0,
            'no_sales_days': 0
        }
        
        # Create complete date range
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            
            if date_str in daily_sales:
                sales_data = daily_sales[date_str]
                color_info = CalendarService._get_color_coding(sales_data['revenue'])
                
                calendar_events.append({
                    'date': date_str,
                    'title': f"${sales_data['revenue']:.2f}",
                    'backgroundColor': color_info['background_color'],
                    'borderColor': color_info['border_color'],
                    'textColor': color_info['text_color'],
                    'sales_count': sales_data['sales_count'],
                    'revenue': sales_data['revenue'],
                    'products_sold': sales_data['products_sold'],
                    'top_product': sales_data['top_product'],
                    'volume_level': color_info['volume_level']
                })
                
                # Update summary
                sales_summary['total_revenue'] += sales_data['revenue']
                sales_summary['total_sales'] += sales_data['sales_count']
                
                if color_info['volume_level'] == 'high':
                    sales_summary['high_sales_days'] += 1
                elif color_info['volume_level'] == 'medium':
                    sales_summary['medium_sales_days'] += 1
                else:
                    sales_summary['low_sales_days'] += 1
            else:
                # No sales day
                calendar_events.append({
                    'date': date_str,
                    'title': 'No Sales',
                    'backgroundColor': '#f8f9fa',
                    'borderColor': '#dee2e6',
                    'textColor': '#6c757d',
                    'sales_count': 0,
                    'revenue': 0,
                    'products_sold': 0,
                    'top_product': None,
                    'volume_level': 'none'
                })
                
                sales_summary['no_sales_days'] += 1
            
            current_date += timedelta(days=1)
        
        return {
            'events': calendar_events,
            'summary': sales_summary,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_days': (end_date - start_date).days + 1
            },
            'thresholds': {
                'high_sales': CalendarService.HIGH_SALES_THRESHOLD,
                'medium_sales': CalendarService.MEDIUM_SALES_THRESHOLD
            }
        }
    
    @staticmethod
    def get_date_details(target_date: date) -> Dict:
        """
        Get detailed sales information for a specific date
        
        Args:
            target_date: Date to get details for
            
        Returns:
            Dictionary with detailed sales information
        """
        # Get all sales for the specific date
        sales = Sale.get_sales_by_date(target_date)
        
        if not sales:
            return {
                'date': target_date.isoformat(),
                'has_sales': False,
                'sales_count': 0,
                'total_revenue': 0,
                'products_sold': [],
                'customer_purchases': [],
                'summary': {
                    'unique_products': 0,
                    'unique_customers': 0,
                    'average_sale_amount': 0,
                    'total_quantity': 0
                }
            }
        
        # Process sales data
        products_sold = {}
        customer_purchases = {}
        total_revenue = 0
        total_quantity = 0
        
        for sale in sales:
            # Aggregate by product
            if sale.product_id not in products_sold:
                products_sold[sale.product_id] = {
                    'product_id': sale.product_id,
                    'product_name': sale.product.name if sale.product else 'Unknown',
                    'category': sale.product.category if sale.product else 'Unknown',
                    'quantity_sold': 0,
                    'revenue': 0,
                    'sales_count': 0,
                    'unit_price': float(sale.unit_price)
                }
            
            products_sold[sale.product_id]['quantity_sold'] += sale.quantity
            products_sold[sale.product_id]['revenue'] += float(sale.total_amount)
            products_sold[sale.product_id]['sales_count'] += 1
            
            # Aggregate by customer
            if sale.customer_id not in customer_purchases:
                customer_purchases[sale.customer_id] = {
                    'customer_id': sale.customer_id,
                    'customer_name': sale.customer.full_name if sale.customer else 'Unknown',
                    'customer_email': sale.customer.email if sale.customer else 'Unknown',
                    'purchases': [],
                    'total_spent': 0,
                    'items_bought': 0
                }
            
            customer_purchases[sale.customer_id]['purchases'].append({
                'product_name': sale.product.name if sale.product else 'Unknown',
                'quantity': sale.quantity,
                'unit_price': float(sale.unit_price),
                'total_amount': float(sale.total_amount),
                'sale_time': sale.sale_date.strftime('%H:%M:%S')
            })
            customer_purchases[sale.customer_id]['total_spent'] += float(sale.total_amount)
            customer_purchases[sale.customer_id]['items_bought'] += sale.quantity
            
            # Update totals
            total_revenue += float(sale.total_amount)
            total_quantity += sale.quantity
        
        # Sort products by revenue (highest first)
        products_list = sorted(products_sold.values(), key=lambda x: x['revenue'], reverse=True)
        
        # Sort customers by total spent (highest first)
        customers_list = sorted(customer_purchases.values(), key=lambda x: x['total_spent'], reverse=True)
        
        return {
            'date': target_date.isoformat(),
            'has_sales': True,
            'sales_count': len(sales),
            'total_revenue': total_revenue,
            'products_sold': products_list,
            'customer_purchases': customers_list,
            'summary': {
                'unique_products': len(products_sold),
                'unique_customers': len(customer_purchases),
                'average_sale_amount': total_revenue / len(sales) if sales else 0,
                'total_quantity': total_quantity
            }
        }
    
    @staticmethod
    def get_monthly_calendar_data(year: int, month: int) -> Dict:
        """
        Get calendar data for a specific month
        
        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)
            
        Returns:
            Dictionary containing monthly calendar data
        """
        # Calculate month boundaries
        start_date = date(year, month, 1)
        
        # Get last day of month
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        end_date = next_month - timedelta(days=1)
        
        return CalendarService.get_calendar_data(start_date, end_date)
    
    @staticmethod
    def get_weekly_calendar_data(year: int, week: int) -> Dict:
        """
        Get calendar data for a specific week
        
        Args:
            year: Year (e.g., 2024)
            week: Week number (1-53)
            
        Returns:
            Dictionary containing weekly calendar data
        """
        # Calculate week boundaries
        jan_1 = date(year, 1, 1)
        start_date = jan_1 + timedelta(weeks=week-1)
        
        # Adjust to Monday (start of week)
        days_since_monday = start_date.weekday()
        start_date = start_date - timedelta(days=days_since_monday)
        
        end_date = start_date + timedelta(days=6)  # Sunday
        
        return CalendarService.get_calendar_data(start_date, end_date)
    
    @staticmethod
    def analyze_sales_patterns(days: int = 90) -> Dict:
        """
        Analyze sales patterns for calendar insights
        
        Args:
            days: Number of days to analyze (default: 90)
            
        Returns:
            Dictionary with sales pattern analysis
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get daily sales data
        daily_sales = CalendarService._get_daily_sales_aggregation(start_date, end_date)
        
        # Analyze patterns
        weekday_sales = {i: {'revenue': 0, 'count': 0, 'days': 0} for i in range(7)}  # 0=Monday, 6=Sunday
        monthly_trends = {}
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            weekday = current_date.weekday()
            month_key = current_date.strftime('%Y-%m')
            
            # Initialize monthly data
            if month_key not in monthly_trends:
                monthly_trends[month_key] = {'revenue': 0, 'sales_count': 0, 'days_with_sales': 0}
            
            if date_str in daily_sales:
                sales_data = daily_sales[date_str]
                
                # Weekday analysis
                weekday_sales[weekday]['revenue'] += sales_data['revenue']
                weekday_sales[weekday]['count'] += sales_data['sales_count']
                weekday_sales[weekday]['days'] += 1
                
                # Monthly analysis
                monthly_trends[month_key]['revenue'] += sales_data['revenue']
                monthly_trends[month_key]['sales_count'] += sales_data['sales_count']
                monthly_trends[month_key]['days_with_sales'] += 1
            else:
                weekday_sales[weekday]['days'] += 1
            
            current_date += timedelta(days=1)
        
        # Calculate averages and format results
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_analysis = []
        
        for i, name in enumerate(weekday_names):
            data = weekday_sales[i]
            avg_revenue = data['revenue'] / data['days'] if data['days'] > 0 else 0
            avg_sales = data['count'] / data['days'] if data['days'] > 0 else 0
            
            weekday_analysis.append({
                'weekday': name,
                'weekday_number': i,
                'average_revenue': avg_revenue,
                'average_sales_count': avg_sales,
                'total_revenue': data['revenue'],
                'total_sales': data['count'],
                'analysis_days': data['days']
            })
        
        # Sort weekdays by average revenue
        best_weekdays = sorted(weekday_analysis, key=lambda x: x['average_revenue'], reverse=True)
        
        return {
            'weekday_analysis': weekday_analysis,
            'best_performing_weekdays': best_weekdays[:3],
            'worst_performing_weekdays': best_weekdays[-3:],
            'monthly_trends': monthly_trends,
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_days': days
            }
        }
    
    # Private helper methods
    
    @staticmethod
    def _get_daily_sales_aggregation(start_date: date, end_date: date) -> Dict:
        """
        Get daily sales aggregation for the date range
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with daily sales data keyed by date string
        """
        # Convert dates to datetime for database query
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Query daily sales aggregation
        daily_data = db.session.query(
            func.date(Sale.sale_date).label('sale_date'),
            func.count(Sale.id).label('sales_count'),
            func.sum(Sale.total_amount).label('revenue'),
            func.sum(Sale.quantity).label('total_quantity')
        ).filter(
            and_(
                Sale.sale_date >= start_datetime,
                Sale.sale_date <= end_datetime
            )
        ).group_by(
            func.date(Sale.sale_date)
        ).all()
        
        # Process results into dictionary
        daily_sales = {}
        
        for row in daily_data:
            date_str = row.sale_date.isoformat()
            
            # Get top-selling product for this date
            top_product = CalendarService._get_top_product_for_date(row.sale_date)
            
            # Get unique products count for this date
            products_sold = CalendarService._get_products_count_for_date(row.sale_date)
            
            daily_sales[date_str] = {
                'sales_count': row.sales_count,
                'revenue': float(row.revenue),
                'total_quantity': row.total_quantity,
                'products_sold': products_sold,
                'top_product': top_product
            }
        
        return daily_sales
    
    @staticmethod
    def _get_color_coding(revenue: float) -> Dict:
        """
        Get color coding based on sales volume
        
        Args:
            revenue: Daily revenue amount
            
        Returns:
            Dictionary with color information
        """
        if revenue >= CalendarService.HIGH_SALES_THRESHOLD:
            return {
                'background_color': '#dc3545',  # Red for high sales
                'border_color': '#b02a37',
                'text_color': '#ffffff',
                'volume_level': 'high'
            }
        elif revenue >= CalendarService.MEDIUM_SALES_THRESHOLD:
            return {
                'background_color': '#ffc107',  # Yellow for medium sales
                'border_color': '#d39e00',
                'text_color': '#000000',
                'volume_level': 'medium'
            }
        elif revenue > 0:
            return {
                'background_color': '#28a745',  # Green for low sales
                'border_color': '#1e7e34',
                'text_color': '#ffffff',
                'volume_level': 'low'
            }
        else:
            return {
                'background_color': '#f8f9fa',  # Light gray for no sales
                'border_color': '#dee2e6',
                'text_color': '#6c757d',
                'volume_level': 'none'
            }
    
    @staticmethod
    def _get_top_product_for_date(target_date: date) -> Optional[Dict]:
        """
        Get the top-selling product for a specific date
        
        Args:
            target_date: Date to analyze
            
        Returns:
            Dictionary with top product info or None
        """
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        top_product = db.session.query(
            Sale.product_id,
            func.sum(Sale.quantity).label('total_quantity'),
            func.sum(Sale.total_amount).label('total_revenue')
        ).filter(
            and_(
                Sale.sale_date >= start_datetime,
                Sale.sale_date <= end_datetime
            )
        ).group_by(
            Sale.product_id
        ).order_by(
            func.sum(Sale.total_amount).desc()
        ).first()
        
        if top_product:
            product = Product.query.get(top_product.product_id)
            return {
                'product_id': top_product.product_id,
                'product_name': product.name if product else 'Unknown',
                'quantity_sold': top_product.total_quantity,
                'revenue': float(top_product.total_revenue)
            }
        
        return None
    
    @staticmethod
    def _get_products_count_for_date(target_date: date) -> int:
        """
        Get count of unique products sold on a specific date
        
        Args:
            target_date: Date to analyze
            
        Returns:
            Count of unique products sold
        """
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        return db.session.query(Sale.product_id).filter(
            and_(
                Sale.sale_date >= start_datetime,
                Sale.sale_date <= end_datetime
            )
        ).distinct().count()