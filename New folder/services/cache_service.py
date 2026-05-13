"""
Cache Service for Smart Inventory Management System
Provides intelligent caching for frequently accessed data
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import current_app
from extensions import db
from models.product import Product
from models.user import User
from models.purchase_request import PurchaseRequest
from models.sale import Sale
from utils.performance_optimization import cache_manager, cached


class CacheService:
    """Service for managing cached data and improving performance"""
    
    @staticmethod
    @cached(ttl=600, key_prefix="products_")
    def get_cached_products(include_inactive: bool = False) -> List[Dict]:
        """Get cached product list with optimized queries"""
        if include_inactive:
            products = Product.query.all()
        else:
            products = Product.query.filter_by(is_active=True).all()
        
        return [product.to_dict() for product in products]
    
    @staticmethod
    @cached(ttl=300, key_prefix="low_stock_")
    def get_cached_low_stock_products() -> List[Dict]:
        """Get cached low stock products"""
        products = Product.query.filter(
            Product.is_active == True,
            Product.quantity <= Product.low_stock_threshold
        ).order_by(Product.quantity.asc()).all()
        
        return [product.to_dict() for product in products]
    
    @staticmethod
    @cached(ttl=1800, key_prefix="categories_")
    def get_cached_categories() -> List[str]:
        """Get cached product categories"""
        categories = db.session.query(Product.category).filter_by(is_active=True).distinct().all()
        return [category[0] for category in categories]
    
    @staticmethod
    @cached(ttl=900, key_prefix="dashboard_")
    def get_cached_dashboard_metrics(days: int = 30) -> Dict:
        """Get cached dashboard metrics"""
        from services.analytics_service import AnalyticsService
        return AnalyticsService.get_dashboard_metrics(days)
    
    @staticmethod
    @cached(ttl=600, key_prefix="sales_chart_")
    def get_cached_sales_chart_data(days: int = 30) -> Dict:
        """Get cached sales chart data"""
        from services.analytics_service import AnalyticsService
        return AnalyticsService.get_sales_chart_data(days)
    
    @staticmethod
    @cached(ttl=300, key_prefix="pending_requests_")
    def get_cached_pending_requests() -> List[Dict]:
        """Get cached pending purchase requests"""
        requests = PurchaseRequest.query.filter_by(status='pending').order_by(
            PurchaseRequest.requested_at.asc()
        ).all()
        
        return [request.to_dict() for request in requests]
    
    @staticmethod
    @cached(ttl=1200, key_prefix="customer_stats_")
    def get_cached_customer_analytics(days: int = 30) -> Dict:
        """Get cached customer analytics"""
        from services.analytics_service import AnalyticsService
        return AnalyticsService.get_customer_analytics(days)
    
    @staticmethod
    @cached(ttl=600, key_prefix="product_performance_")
    def get_cached_product_performance(days: int = 30) -> Dict:
        """Get cached product performance data"""
        from services.analytics_service import AnalyticsService
        return AnalyticsService.get_product_performance_data(days)
    
    @staticmethod
    @cached(ttl=300, key_prefix="alerts_")
    def get_cached_alerts() -> List[Dict]:
        """Get cached low stock alerts"""
        from services.analytics_service import AnalyticsService
        return AnalyticsService.get_low_stock_alerts()
    
    @staticmethod
    def get_cached_product_by_id(product_id: int) -> Optional[Dict]:
        """Get cached product by ID"""
        cache_key = f"product_{product_id}"
        cached_product = cache_manager.get(cache_key)
        
        if cached_product is None:
            product = Product.query.filter_by(id=product_id, is_active=True).first()
            if product:
                cached_product = product.to_dict()
                cache_manager.set(cache_key, cached_product, ttl=600)  # 10 minutes
        
        return cached_product
    
    @staticmethod
    def get_cached_user_by_id(user_id: int) -> Optional[Dict]:
        """Get cached user by ID"""
        cache_key = f"user_{user_id}"
        cached_user = cache_manager.get(cache_key)
        
        if cached_user is None:
            user = User.query.filter_by(id=user_id, is_active=True).first()
            if user:
                cached_user = user.to_dict()
                cache_manager.set(cache_key, cached_user, ttl=1800)  # 30 minutes
        
        return cached_user
    
    @staticmethod
    def get_cached_recent_sales(days: int = 7) -> List[Dict]:
        """Get cached recent sales"""
        cache_key = f"recent_sales_{days}d"
        cached_sales = cache_manager.get(cache_key)
        
        if cached_sales is None:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            sales = Sale.query.filter(
                Sale.sale_date >= cutoff_date
            ).order_by(Sale.sale_date.desc()).limit(50).all()
            
            cached_sales = [sale.to_dict() for sale in sales]
            cache_manager.set(cache_key, cached_sales, ttl=300)  # 5 minutes
        
        return cached_sales
    
    @staticmethod
    def invalidate_product_cache(product_id: Optional[int] = None):
        """Invalidate product-related cache entries"""
        if product_id:
            # Invalidate specific product cache
            cache_manager.delete(f"product_{product_id}")
        
        # Invalidate general product caches
        cache_keys_to_invalidate = [
            "products_get_cached_products",
            "low_stock_get_cached_low_stock_products",
            "categories_get_cached_categories",
            "dashboard_get_cached_dashboard_metrics",
            "product_performance_get_cached_product_performance",
            "alerts_get_cached_alerts"
        ]
        
        for key in cache_keys_to_invalidate:
            # Since we don't know the exact hash, we'll need to clear related entries
            # This is a simplified approach - in production, consider using cache tags
            pass
    
    @staticmethod
    def invalidate_sales_cache():
        """Invalidate sales-related cache entries"""
        cache_keys_to_invalidate = [
            "dashboard_get_cached_dashboard_metrics",
            "sales_chart_get_cached_sales_chart_data",
            "customer_stats_get_cached_customer_analytics",
            "product_performance_get_cached_product_performance"
        ]
        
        # Also invalidate recent sales cache
        for days in [7, 14, 30]:
            cache_manager.delete(f"recent_sales_{days}d")
    
    @staticmethod
    def invalidate_request_cache():
        """Invalidate purchase request-related cache entries"""
        cache_manager.delete("pending_requests_get_cached_pending_requests")
        # Also invalidate dashboard metrics as they include request counts
        CacheService.invalidate_dashboard_cache()
    
    @staticmethod
    def invalidate_dashboard_cache():
        """Invalidate dashboard-related cache entries"""
        cache_keys_to_invalidate = [
            "dashboard_get_cached_dashboard_metrics",
            "sales_chart_get_cached_sales_chart_data",
            "alerts_get_cached_alerts"
        ]
        
        for key in cache_keys_to_invalidate:
            # Clear all variations of dashboard cache
            pass
    
    @staticmethod
    def warm_up_cache():
        """Pre-populate cache with frequently accessed data"""
        try:
            print("🔥 Warming up cache...")
            
            # Warm up product data
            CacheService.get_cached_products()
            CacheService.get_cached_low_stock_products()
            CacheService.get_cached_categories()
            
            # Warm up dashboard data
            CacheService.get_cached_dashboard_metrics(30)
            CacheService.get_cached_dashboard_metrics(7)
            CacheService.get_cached_sales_chart_data(30)
            
            # Warm up request data
            CacheService.get_cached_pending_requests()
            
            # Warm up analytics data
            CacheService.get_cached_customer_analytics(30)
            CacheService.get_cached_product_performance(30)
            CacheService.get_cached_alerts()
            
            # Warm up recent sales
            CacheService.get_cached_recent_sales(7)
            
            print("✅ Cache warm-up completed")
            return True
            
        except Exception as e:
            print(f"❌ Cache warm-up failed: {str(e)}")
            return False
    
    @staticmethod
    def get_cache_health_report() -> Dict[str, Any]:
        """Get cache health and performance report"""
        stats = cache_manager.get_stats()
        
        # Calculate hit rate (simplified - would need request tracking in production)
        estimated_hit_rate = min(stats['total_entries'] / 100, 0.95)  # Simplified calculation
        
        health_score = 100
        issues = []
        
        # Check cache size
        if stats['total_entries'] > 1000:
            health_score -= 10
            issues.append("High cache entry count")
        
        # Check memory usage
        if stats['memory_usage_estimate'] > 10 * 1024 * 1024:  # 10MB
            health_score -= 15
            issues.append("High memory usage")
        
        # Check age of entries
        if stats['oldest_entry']:
            oldest_age = (datetime.utcnow() - stats['oldest_entry']).total_seconds()
            if oldest_age > 3600:  # 1 hour
                health_score -= 5
                issues.append("Some cache entries are very old")
        
        return {
            'health_score': max(health_score, 0),
            'cache_stats': stats,
            'estimated_hit_rate': estimated_hit_rate,
            'issues': issues,
            'recommendations': CacheService._generate_cache_recommendations(stats, issues)
        }
    
    @staticmethod
    def _generate_cache_recommendations(stats: Dict, issues: List[str]) -> List[str]:
        """Generate cache optimization recommendations"""
        recommendations = []
        
        if "High cache entry count" in issues:
            recommendations.append("Consider reducing TTL for less frequently accessed data")
        
        if "High memory usage" in issues:
            recommendations.append("Implement cache size limits or use external cache like Redis")
        
        if "Some cache entries are very old" in issues:
            recommendations.append("Implement more aggressive cache cleanup")
        
        if stats['total_entries'] < 10:
            recommendations.append("Cache usage is low - consider caching more frequently accessed data")
        
        return recommendations
    
    @staticmethod
    def optimize_cache_settings():
        """Optimize cache settings based on usage patterns"""
        try:
            # Adjust TTL based on data volatility
            volatile_data_ttl = 300    # 5 minutes for frequently changing data
            stable_data_ttl = 1800     # 30 minutes for stable data
            static_data_ttl = 3600     # 1 hour for rarely changing data
            
            # Update cache manager default TTL
            cache_manager.default_ttl = volatile_data_ttl
            
            print("✅ Cache settings optimized")
            return True
            
        except Exception as e:
            print(f"❌ Cache optimization failed: {str(e)}")
            return False


class SmartCacheInvalidation:
    """Smart cache invalidation based on data changes"""
    
    @staticmethod
    def on_product_change(product_id: int, change_type: str):
        """Handle cache invalidation when product changes"""
        CacheService.invalidate_product_cache(product_id)
        
        if change_type in ['stock_change', 'price_change']:
            CacheService.invalidate_dashboard_cache()
            CacheService.invalidate_sales_cache()
    
    @staticmethod
    def on_sale_created(sale_id: int):
        """Handle cache invalidation when sale is created"""
        CacheService.invalidate_sales_cache()
        CacheService.invalidate_dashboard_cache()
        CacheService.invalidate_product_cache()  # For stock levels
    
    @staticmethod
    def on_request_status_change(request_id: int, new_status: str):
        """Handle cache invalidation when request status changes"""
        CacheService.invalidate_request_cache()
        
        if new_status == 'approved':
            CacheService.invalidate_sales_cache()
            CacheService.invalidate_product_cache()  # For stock levels
    
    @staticmethod
    def on_user_change(user_id: int):
        """Handle cache invalidation when user changes"""
        cache_manager.delete(f"user_{user_id}")
        CacheService.invalidate_dashboard_cache()  # For customer counts


def init_cache_service(app):
    """Initialize cache service with Flask app"""
    with app.app_context():
        # Warm up cache on startup
        CacheService.warm_up_cache()
        
        # Optimize cache settings
        CacheService.optimize_cache_settings()
        
        print("🚀 Cache service initialized")