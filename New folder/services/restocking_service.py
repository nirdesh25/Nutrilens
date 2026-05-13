"""
Restocking Service for Smart Inventory Management System
Provides intelligent restocking suggestions and inventory optimization
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from extensions import db
from models.product import Product
from models.sale import Sale
from models.ai_prediction import AIPrediction
from services.ai_prediction_service import AIPredictionService


class RestockingService:
    """Service for generating intelligent restocking suggestions"""
    
    def __init__(self):
        """Initialize restocking service"""
        self.ai_service = AIPredictionService()
    
    def generate_comprehensive_suggestions(self, 
                                         min_confidence: float = 0.6,
                                         include_seasonal: bool = True,
                                         budget_limit: Optional[float] = None) -> Dict:
        """
        Generate comprehensive restocking suggestions with business intelligence
        
        Args:
            min_confidence: Minimum AI confidence threshold
            include_seasonal: Whether to include seasonal analysis
            budget_limit: Optional budget constraint for suggestions
            
        Returns:
            Dictionary with comprehensive restocking analysis
        """
        # Get AI-powered suggestions
        ai_suggestions = self.ai_service.generate_restock_suggestions(min_confidence)
        
        # Enhance suggestions with business logic
        enhanced_suggestions = []
        total_cost = 0.0
        
        for suggestion in ai_suggestions:
            enhanced = self._enhance_suggestion(suggestion, include_seasonal)
            
            # Apply budget constraints if specified
            if budget_limit and total_cost + enhanced['cost_estimate'] > budget_limit:
                enhanced['budget_constrained'] = True
                enhanced['suggested_quantity'] = self._calculate_budget_constrained_quantity(
                    enhanced, budget_limit - total_cost
                )
                enhanced['cost_estimate'] = enhanced['suggested_quantity'] * enhanced['unit_cost']
            
            enhanced_suggestions.append(enhanced)
            total_cost += enhanced['cost_estimate']
        
        # Generate summary and insights
        summary = self._generate_suggestions_summary(enhanced_suggestions)
        
        # Add business insights
        insights = self._generate_business_insights(enhanced_suggestions)
        
        return {
            'suggestions': enhanced_suggestions,
            'summary': summary,
            'insights': insights,
            'total_investment': total_cost,
            'budget_limit': budget_limit,
            'generation_time': datetime.utcnow().isoformat(),
            'ai_model_version': self.ai_service.MODEL_VERSION
        }
    
    def get_critical_restocks(self) -> List[Dict]:
        """
        Get products that critically need restocking
        
        Returns:
            List of critical restock items
        """
        critical_products = []
        
        # Get out of stock products
        out_of_stock = Product.query.filter_by(quantity=0).all()
        
        # Get low stock products with recent sales
        low_stock = Product.query.filter(
            Product.quantity > 0,
            Product.quantity <= Product.low_stock_threshold
        ).all()
        
        for product in out_of_stock + low_stock:
            # Check recent sales activity
            recent_sales = Sale.query.filter(
                Sale.product_id == product.id,
                Sale.sale_date >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            if recent_sales > 0 or product.quantity == 0:
                critical_info = self._analyze_critical_product(product)
                if critical_info:
                    critical_products.append(critical_info)
        
        # Sort by urgency
        critical_products.sort(key=lambda x: x['urgency_score'], reverse=True)
        
        return critical_products
    
    def analyze_seasonal_restocking_needs(self, months_ahead: int = 3) -> Dict:
        """
        Analyze seasonal restocking needs for upcoming months
        
        Args:
            months_ahead: Number of months to analyze ahead
            
        Returns:
            Dictionary with seasonal restocking analysis
        """
        seasonal_analysis = {}
        current_date = datetime.now()
        
        # Get all products with sales history
        products_with_sales = db.session.query(Product.id).join(Sale).distinct().all()
        product_ids = [p.id for p in products_with_sales]
        
        for month_offset in range(1, months_ahead + 1):
            target_date = current_date + timedelta(days=30 * month_offset)
            target_month = target_date.month
            
            month_suggestions = []
            
            for product_id in product_ids:
                seasonal_data = self.ai_service.analyze_seasonal_trends(product_id)
                
                if seasonal_data and 'seasonal_factors' in seasonal_data:
                    seasonal_factor = seasonal_data['seasonal_factors'].get(target_month, 1.0)
                    
                    # If seasonal factor indicates higher demand
                    if seasonal_factor > 1.1:
                        product = Product.query.get(product_id)
                        if product:
                            suggestion = self._create_seasonal_suggestion(
                                product, seasonal_factor, target_date
                            )
                            if suggestion:
                                month_suggestions.append(suggestion)
            
            # Sort by seasonal impact
            month_suggestions.sort(key=lambda x: x['seasonal_impact'], reverse=True)
            
            seasonal_analysis[target_date.strftime('%Y-%m')] = {
                'month': target_date.strftime('%B %Y'),
                'suggestions': month_suggestions[:10],  # Top 10 suggestions
                'total_products': len(month_suggestions),
                'high_impact_count': len([s for s in month_suggestions if s['seasonal_impact'] > 1.3])
            }
        
        return {
            'seasonal_analysis': seasonal_analysis,
            'analysis_period': f"{months_ahead} months ahead",
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def calculate_optimal_order_quantities(self, product_ids: List[int], 
                                         budget_constraint: Optional[float] = None) -> Dict:
        """
        Calculate optimal order quantities using economic order quantity principles
        
        Args:
            product_ids: List of product IDs to analyze
            budget_constraint: Optional budget limit
            
        Returns:
            Dictionary with optimal order calculations
        """
        optimal_orders = []
        total_cost = 0.0
        
        for product_id in product_ids:
            product = Product.query.get(product_id)
            if not product:
                continue
            
            # Get demand data
            annual_demand = self._calculate_annual_demand(product_id)
            if annual_demand <= 0:
                continue
            
            # Calculate EOQ (Economic Order Quantity)
            eoq_data = self._calculate_eoq(product, annual_demand)
            
            # Get AI prediction for validation
            ai_prediction = self.ai_service.predict_demand(product_id, 'monthly')
            
            # Combine EOQ with AI insights
            optimal_quantity = self._optimize_quantity_with_ai(eoq_data, ai_prediction)
            
            order_info = {
                'product_id': product_id,
                'product_name': product.name,
                'current_stock': product.quantity,
                'annual_demand': annual_demand,
                'eoq_quantity': eoq_data['eoq'],
                'ai_suggested': ai_prediction['predicted_demand'] if ai_prediction else 0,
                'optimal_quantity': optimal_quantity,
                'order_cost': float(optimal_quantity * product.cost_price),
                'carrying_cost_annual': eoq_data['carrying_cost_annual'],
                'order_frequency': eoq_data['order_frequency'],
                'confidence_score': ai_prediction['confidence_score'] if ai_prediction else 0.5
            }
            
            optimal_orders.append(order_info)
            total_cost += order_info['order_cost']
        
        # Apply budget constraints if needed
        if budget_constraint and total_cost > budget_constraint:
            optimal_orders = self._apply_budget_optimization(optimal_orders, budget_constraint)
            total_cost = sum(order['order_cost'] for order in optimal_orders)
        
        return {
            'optimal_orders': optimal_orders,
            'total_investment': total_cost,
            'budget_constraint': budget_constraint,
            'budget_utilization': (total_cost / budget_constraint * 100) if budget_constraint else None,
            'analysis_method': 'EOQ + AI Hybrid',
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def get_supplier_optimization_suggestions(self) -> Dict:
        """
        Generate supplier optimization suggestions based on restocking needs
        
        Returns:
            Dictionary with supplier optimization insights
        """
        # Get current restocking needs
        suggestions = self.generate_comprehensive_suggestions()
        
        # Group by category for supplier analysis
        category_analysis = {}
        
        for suggestion in suggestions['suggestions']:
            category = suggestion['category']
            
            if category not in category_analysis:
                category_analysis[category] = {
                    'products': [],
                    'total_cost': 0.0,
                    'total_quantity': 0,
                    'urgency_levels': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
                }
            
            category_analysis[category]['products'].append(suggestion)
            category_analysis[category]['total_cost'] += suggestion['cost_estimate']
            category_analysis[category]['total_quantity'] += suggestion['suggested_quantity']
            category_analysis[category]['urgency_levels'][suggestion['urgency_level']] += 1
        
        # Generate optimization recommendations
        optimization_recommendations = []
        
        for category, data in category_analysis.items():
            if data['total_cost'] > 1000:  # Significant investment threshold
                recommendation = {
                    'category': category,
                    'total_investment': data['total_cost'],
                    'product_count': len(data['products']),
                    'bulk_order_potential': data['total_cost'] > 5000,
                    'urgent_items': data['urgency_levels']['critical'] + data['urgency_levels']['high'],
                    'recommendation': self._generate_supplier_recommendation(data)
                }
                optimization_recommendations.append(recommendation)
        
        return {
            'category_analysis': category_analysis,
            'optimization_recommendations': optimization_recommendations,
            'total_categories': len(category_analysis),
            'high_value_categories': len([c for c in category_analysis.values() if c['total_cost'] > 5000]),
            'generated_at': datetime.utcnow().isoformat()
        }
    
    # Private helper methods
    
    def _enhance_suggestion(self, suggestion: Dict, include_seasonal: bool) -> Dict:
        """Enhance AI suggestion with additional business logic"""
        product = Product.query.get(suggestion['product_id'])
        
        enhanced = suggestion.copy()
        enhanced.update({
            'unit_cost': float(product.cost_price),
            'unit_price': float(product.selling_price),
            'profit_margin': float((product.selling_price - product.cost_price) / product.selling_price * 100),
            'low_stock_threshold': product.low_stock_threshold,
            'stock_coverage_days': self._calculate_stock_coverage_days(product, suggestion['predicted_demand']),
            'reorder_point': self._calculate_reorder_point(product),
            'business_priority': self._calculate_business_priority(product, suggestion)
        })
        
        # Add seasonal analysis if requested
        if include_seasonal:
            seasonal_data = self.ai_service.analyze_seasonal_trends(suggestion['product_id'])
            enhanced['seasonal_analysis'] = seasonal_data
            
            # Adjust suggestion based on seasonal trends
            if seasonal_data and 'peak_months' in seasonal_data:
                current_month = datetime.now().month
                if current_month in seasonal_data.get('peak_months', []):
                    enhanced['seasonal_adjustment'] = 'increase'
                    enhanced['suggested_quantity'] = int(enhanced['suggested_quantity'] * 1.2)
                elif current_month in seasonal_data.get('low_months', []):
                    enhanced['seasonal_adjustment'] = 'decrease'
                    enhanced['suggested_quantity'] = int(enhanced['suggested_quantity'] * 0.8)
                else:
                    enhanced['seasonal_adjustment'] = 'none'
        
        return enhanced
    
    def _generate_suggestions_summary(self, suggestions: List[Dict]) -> Dict:
        """Generate summary statistics for suggestions"""
        if not suggestions:
            return {
                'total_suggestions': 0,
                'total_investment': 0.0,
                'urgency_breakdown': {},
                'category_breakdown': {}
            }
        
        urgency_counts = {}
        category_costs = {}
        
        for suggestion in suggestions:
            # Count urgency levels
            urgency = suggestion['urgency_level']
            urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
            
            # Sum costs by category
            category = suggestion['category']
            category_costs[category] = category_costs.get(category, 0.0) + suggestion['cost_estimate']
        
        return {
            'total_suggestions': len(suggestions),
            'total_investment': sum(s['cost_estimate'] for s in suggestions),
            'average_investment_per_item': sum(s['cost_estimate'] for s in suggestions) / len(suggestions),
            'urgency_breakdown': urgency_counts,
            'category_breakdown': category_costs,
            'high_confidence_count': len([s for s in suggestions if s['confidence_score'] > 0.8]),
            'critical_items': len([s for s in suggestions if s['urgency_level'] == 'critical'])
        }
    
    def _generate_business_insights(self, suggestions: List[Dict]) -> List[str]:
        """Generate business insights from suggestions"""
        insights = []
        
        if not suggestions:
            return ["No restocking suggestions available at this time."]
        
        # Critical stock insights
        critical_count = len([s for s in suggestions if s['urgency_level'] == 'critical'])
        if critical_count > 0:
            insights.append(f"{critical_count} products require immediate restocking to avoid stockouts.")
        
        # High-value opportunities
        high_value = [s for s in suggestions if s['revenue_potential'] > 1000]
        if high_value:
            total_revenue_potential = sum(s['revenue_potential'] for s in high_value)
            insights.append(f"High-value restocking opportunities could generate ${total_revenue_potential:,.2f} in potential revenue.")
        
        # Seasonal insights
        seasonal_adjustments = [s for s in suggestions if s.get('seasonal_adjustment') == 'increase']
        if seasonal_adjustments:
            insights.append(f"{len(seasonal_adjustments)} products show seasonal demand increases - consider prioritizing these orders.")
        
        # Budget insights
        total_cost = sum(s['cost_estimate'] for s in suggestions)
        if total_cost > 10000:
            insights.append(f"Total investment of ${total_cost:,.2f} required - consider phased restocking approach.")
        
        # Confidence insights
        low_confidence = [s for s in suggestions if s['confidence_score'] < 0.7]
        if low_confidence:
            insights.append(f"{len(low_confidence)} suggestions have lower confidence - monitor these products closely.")
        
        return insights
    
    def _calculate_budget_constrained_quantity(self, suggestion: Dict, remaining_budget: float) -> int:
        """Calculate quantity that fits within budget constraint"""
        unit_cost = suggestion['unit_cost']
        if unit_cost <= 0:
            return 0
        
        max_quantity = int(remaining_budget / unit_cost)
        return min(max_quantity, suggestion['suggested_quantity'])
    
    def _analyze_critical_product(self, product: Product) -> Optional[Dict]:
        """Analyze a critical product for restocking needs"""
        # Get recent sales data
        recent_sales = Sale.query.filter(
            Sale.product_id == product.id,
            Sale.sale_date >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        if not recent_sales and product.quantity > 0:
            return None  # Not critical if no recent sales and has stock
        
        # Calculate urgency metrics
        total_recent_sales = sum(s.quantity for s in recent_sales)
        days_of_data = min(30, len(set(s.sale_date.date() for s in recent_sales)))
        avg_daily_demand = total_recent_sales / days_of_data if days_of_data > 0 else 0
        
        # Calculate days until stockout
        days_until_stockout = product.quantity / avg_daily_demand if avg_daily_demand > 0 else float('inf')
        
        # Calculate urgency score
        urgency_score = 0.0
        if product.quantity == 0:
            urgency_score = 10.0
        elif days_until_stockout <= 3:
            urgency_score = 8.0
        elif days_until_stockout <= 7:
            urgency_score = 6.0
        elif product.quantity <= product.low_stock_threshold:
            urgency_score = 4.0
        
        if urgency_score > 0:
            return {
                'product_id': product.id,
                'product_name': product.name,
                'category': product.category,
                'current_stock': product.quantity,
                'avg_daily_demand': avg_daily_demand,
                'days_until_stockout': days_until_stockout,
                'urgency_score': urgency_score,
                'recent_sales_count': len(recent_sales),
                'suggested_immediate_order': max(int(avg_daily_demand * 14), product.low_stock_threshold * 2),
                'cost_estimate': float(max(int(avg_daily_demand * 14), product.low_stock_threshold * 2) * product.cost_price)
            }
        
        return None
    
    def _create_seasonal_suggestion(self, product: Product, seasonal_factor: float, target_date: datetime) -> Optional[Dict]:
        """Create seasonal restocking suggestion"""
        if seasonal_factor <= 1.1:
            return None
        
        # Get baseline demand
        recent_sales = Sale.query.filter(
            Sale.product_id == product.id,
            Sale.sale_date >= datetime.utcnow() - timedelta(days=90)
        ).all()
        
        if not recent_sales:
            return None
        
        avg_monthly_demand = sum(s.quantity for s in recent_sales) / 3  # 3 months of data
        seasonal_demand = int(avg_monthly_demand * seasonal_factor)
        
        return {
            'product_id': product.id,
            'product_name': product.name,
            'category': product.category,
            'current_stock': product.quantity,
            'baseline_demand': int(avg_monthly_demand),
            'seasonal_demand': seasonal_demand,
            'seasonal_factor': seasonal_factor,
            'seasonal_impact': seasonal_factor,
            'suggested_quantity': max(0, seasonal_demand - product.quantity),
            'target_month': target_date.strftime('%B %Y'),
            'preparation_time': (target_date - datetime.now()).days,
            'cost_estimate': float(max(0, seasonal_demand - product.quantity) * product.cost_price)
        }
    
    def _calculate_annual_demand(self, product_id: int) -> float:
        """Calculate annual demand for a product"""
        # Get sales from last 12 months
        sales = Sale.query.filter(
            Sale.product_id == product_id,
            Sale.sale_date >= datetime.utcnow() - timedelta(days=365)
        ).all()
        
        return sum(s.quantity for s in sales)
    
    def _calculate_eoq(self, product: Product, annual_demand: float) -> Dict:
        """Calculate Economic Order Quantity"""
        # Assumptions for EOQ calculation
        ordering_cost = 50.0  # Cost per order (can be configured)
        carrying_cost_rate = 0.2  # 20% of item cost per year
        
        item_cost = float(product.cost_price)
        carrying_cost_per_unit = item_cost * carrying_cost_rate
        
        if carrying_cost_per_unit <= 0 or annual_demand <= 0:
            return {
                'eoq': int(product.low_stock_threshold * 2),
                'carrying_cost_annual': 0.0,
                'order_frequency': 12
            }
        
        # EOQ formula: sqrt(2 * D * S / H)
        # D = annual demand, S = ordering cost, H = carrying cost per unit
        eoq = (2 * annual_demand * ordering_cost / carrying_cost_per_unit) ** 0.5
        
        # Calculate order frequency (times per year)
        order_frequency = annual_demand / eoq if eoq > 0 else 12
        
        return {
            'eoq': max(1, int(eoq)),
            'carrying_cost_annual': carrying_cost_per_unit * eoq / 2,
            'order_frequency': order_frequency
        }
    
    def _optimize_quantity_with_ai(self, eoq_data: Dict, ai_prediction: Optional[Dict]) -> int:
        """Combine EOQ with AI prediction for optimal quantity"""
        eoq_quantity = eoq_data['eoq']
        
        if not ai_prediction:
            return eoq_quantity
        
        ai_quantity = ai_prediction['predicted_demand']
        confidence = ai_prediction['confidence_score']
        
        # Weight the quantities based on AI confidence
        # High confidence: favor AI, Low confidence: favor EOQ
        ai_weight = confidence
        eoq_weight = 1 - confidence
        
        optimal_quantity = int(ai_quantity * ai_weight + eoq_quantity * eoq_weight)
        
        # Ensure minimum reasonable quantity
        return max(optimal_quantity, 1)
    
    def _apply_budget_optimization(self, orders: List[Dict], budget_limit: float) -> List[Dict]:
        """Apply budget optimization to order list"""
        # Sort by priority (combination of urgency and profitability)
        def priority_score(order):
            confidence = order['confidence_score']
            profit_potential = (order['optimal_quantity'] * 
                              (order.get('unit_price', order['order_cost'] * 1.5) - order['order_cost'] / order['optimal_quantity']))
            return confidence * profit_potential
        
        orders.sort(key=priority_score, reverse=True)
        
        # Select orders within budget
        selected_orders = []
        remaining_budget = budget_limit
        
        for order in orders:
            if order['order_cost'] <= remaining_budget:
                selected_orders.append(order)
                remaining_budget -= order['order_cost']
            else:
                # Try to fit a partial order
                max_quantity = int(remaining_budget / (order['order_cost'] / order['optimal_quantity']))
                if max_quantity > 0:
                    partial_order = order.copy()
                    partial_order['optimal_quantity'] = max_quantity
                    partial_order['order_cost'] = max_quantity * (order['order_cost'] / order['optimal_quantity'])
                    partial_order['budget_constrained'] = True
                    selected_orders.append(partial_order)
                    break
        
        return selected_orders
    
    def _calculate_stock_coverage_days(self, product: Product, predicted_demand: int) -> Optional[int]:
        """Calculate how many days current stock will last"""
        if predicted_demand <= 0:
            return None
        
        # Convert monthly prediction to daily
        daily_demand = predicted_demand / 30
        
        if daily_demand <= 0:
            return None
        
        return int(product.quantity / daily_demand)
    
    def _calculate_reorder_point(self, product: Product) -> int:
        """Calculate reorder point for product"""
        # Simple reorder point calculation
        # Can be enhanced with lead time and safety stock considerations
        return max(product.low_stock_threshold, int(product.low_stock_threshold * 1.5))
    
    def _calculate_business_priority(self, product: Product, suggestion: Dict) -> str:
        """Calculate business priority for restocking"""
        # Factors: profit margin, sales velocity, stock level
        profit_margin = float((product.selling_price - product.cost_price) / product.selling_price * 100)
        confidence = suggestion['confidence_score']
        urgency_score = suggestion['urgency_score']
        
        # Calculate composite priority score
        priority_score = (profit_margin / 100 * 0.3 + 
                         confidence * 0.4 + 
                         urgency_score / 2.0 * 0.3)
        
        if priority_score >= 0.8:
            return 'high'
        elif priority_score >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def _generate_supplier_recommendation(self, category_data: Dict) -> str:
        """Generate supplier optimization recommendation"""
        total_cost = category_data['total_cost']
        urgent_items = category_data['urgency_levels']['critical'] + category_data['urgency_levels']['high']
        
        if total_cost > 10000:
            return f"Consider negotiating bulk pricing for ${total_cost:,.2f} investment in this category"
        elif urgent_items > 3:
            return f"Expedited shipping recommended for {urgent_items} urgent items in this category"
        elif total_cost > 5000:
            return f"Good opportunity for supplier consolidation with ${total_cost:,.2f} total order value"
        else:
            return "Standard ordering process recommended for this category"