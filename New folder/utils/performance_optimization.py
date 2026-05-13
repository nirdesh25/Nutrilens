"""
Performance Optimization Utilities for Smart Inventory Management System
Provides database indexing, caching, and performance monitoring
"""

import time
import functools
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from flask import current_app, g
from sqlalchemy import text, Index
from extensions import db


class DatabaseOptimizer:
    """Database performance optimization utilities"""
    
    @staticmethod
    def create_performance_indexes():
        """Create database indexes for improved query performance"""
        try:
            # List of index creation statements
            index_statements = [
                # User table indexes
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)",
                "CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)",
                
                # Product table indexes
                "CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)",
                "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
                "CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active)",
                "CREATE INDEX IF NOT EXISTS idx_products_quantity ON products(quantity)",
                "CREATE INDEX IF NOT EXISTS idx_products_low_stock ON products(low_stock_threshold)",
                "CREATE INDEX IF NOT EXISTS idx_products_category_active ON products(category, is_active)",
                "CREATE INDEX IF NOT EXISTS idx_products_stock_status ON products(quantity, low_stock_threshold)",
                
                # Purchase Request table indexes
                "CREATE INDEX IF NOT EXISTS idx_purchase_requests_customer ON purchase_requests(customer_id)",
                "CREATE INDEX IF NOT EXISTS idx_purchase_requests_product ON purchase_requests(product_id)",
                "CREATE INDEX IF NOT EXISTS idx_purchase_requests_status ON purchase_requests(status)",
                "CREATE INDEX IF NOT EXISTS idx_purchase_requests_date ON purchase_requests(requested_at)",
                "CREATE INDEX IF NOT EXISTS idx_purchase_requests_admin ON purchase_requests(admin_id)",
                "CREATE INDEX IF NOT EXISTS idx_purchase_requests_status_date ON purchase_requests(status, requested_at)",
                "CREATE INDEX IF NOT EXISTS idx_purchase_requests_customer_status ON purchase_requests(customer_id, status)",
                
                # Sales table indexes
                "CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id)",
                "CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id)",
                "CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)",
                "CREATE INDEX IF NOT EXISTS idx_sales_purchase_request ON sales(purchase_request_id)",
                "CREATE INDEX IF NOT EXISTS idx_sales_product_date ON sales(product_id, sale_date)",
                "CREATE INDEX IF NOT EXISTS idx_sales_customer_date ON sales(customer_id, sale_date)",
                "CREATE INDEX IF NOT EXISTS idx_sales_date_range ON sales(sale_date DESC)",
            ]
            
            # Execute each statement individually
            for statement in index_statements:
                try:
                    db.session.execute(text(statement))
                except Exception as e:
                    print(f"⚠️  Warning: Could not create index: {statement} - {str(e)}")
            
            # Try to create indexes for tables that might not exist yet
            optional_indexes = [
                # AI Predictions table indexes (might not exist)
                "CREATE INDEX IF NOT EXISTS idx_ai_predictions_product ON ai_predictions(product_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_predictions_date ON ai_predictions(prediction_date)",
                "CREATE INDEX IF NOT EXISTS idx_ai_predictions_period ON ai_predictions(prediction_period)",
                "CREATE INDEX IF NOT EXISTS idx_ai_predictions_confidence ON ai_predictions(confidence_score)",
                "CREATE INDEX IF NOT EXISTS idx_ai_predictions_product_date ON ai_predictions(product_id, prediction_date DESC)",
                
                # Alerts table indexes (might not exist)
                "CREATE INDEX IF NOT EXISTS idx_alerts_product ON alerts(product_id)",
                "CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type)",
                "CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(is_active)",
                "CREATE INDEX IF NOT EXISTS idx_alerts_date ON alerts(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_alerts_active_type ON alerts(is_active, alert_type)",
                
                # Notification Preferences table indexes (might not exist)
                "CREATE INDEX IF NOT EXISTS idx_notification_prefs_user ON notification_preferences(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_notification_prefs_type ON notification_preferences(notification_type)",
                "CREATE INDEX IF NOT EXISTS idx_notification_prefs_enabled ON notification_preferences(is_enabled)",
            ]
            
            for statement in optional_indexes:
                try:
                    db.session.execute(text(statement))
                except Exception:
                    # Silently skip if table doesn't exist
                    pass
            
            db.session.commit()
            print("✅ Database indexes created successfully")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating database indexes: {str(e)}")
            return False
    
    @staticmethod
    def analyze_query_performance():
        """Analyze database query performance"""
        try:
            # Enable query analysis (SQLite specific)
            if 'sqlite' in current_app.config['SQLALCHEMY_DATABASE_URI']:
                db.session.execute(text("PRAGMA optimize"))
                
                # Get table statistics
                stats = {}
                tables = ['users', 'products', 'purchase_requests', 'sales', 'ai_predictions', 'alerts']
                
                for table in tables:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                    stats[table] = result[0] if result else 0
                
                return {
                    'status': 'success',
                    'table_stats': stats,
                    'optimization_run': True
                }
            
            return {'status': 'success', 'message': 'Query optimization completed'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}


class CacheManager:
    """In-memory caching for frequently accessed data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timestamps = {}
        self.default_ttl = 300  # 5 minutes default TTL
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        # Check if cache entry has expired
        if self._is_expired(key):
            self.delete(key)
            return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        self.cache[key] = value
        self.cache_timestamps[key] = {
            'created': datetime.utcnow(),
            'ttl': ttl or self.default_ttl
        }
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        self.cache.pop(key, None)
        self.cache_timestamps.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.cache_timestamps.clear()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry has expired"""
        if key not in self.cache_timestamps:
            return True
        
        timestamp_info = self.cache_timestamps[key]
        expiry_time = timestamp_info['created'] + timedelta(seconds=timestamp_info['ttl'])
        return datetime.utcnow() > expiry_time
    
    def cleanup_expired(self) -> int:
        """Remove expired cache entries"""
        expired_keys = [key for key in self.cache_timestamps.keys() if self._is_expired(key)]
        
        for key in expired_keys:
            self.delete(key)
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'memory_usage_estimate': sum(len(str(v)) for v in self.cache.values()),
            'oldest_entry': min(
                (info['created'] for info in self.cache_timestamps.values()),
                default=None
            ),
            'newest_entry': max(
                (info['created'] for info in self.cache_timestamps.values()),
                default=None
            )
        }


# Global cache instance
cache_manager = CacheManager()


def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


class PerformanceMonitor:
    """Performance monitoring utilities"""
    
    @staticmethod
    def time_function(func: Callable) -> Callable:
        """Decorator to time function execution"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log slow queries (> 1 second)
            if execution_time > 1.0:
                print(f"⚠️  Slow function detected: {func.__name__} took {execution_time:.2f}s")
            
            return result
        return wrapper
    
    @staticmethod
    def get_database_stats() -> Dict[str, Any]:
        """Get database performance statistics"""
        try:
            stats = {}
            
            # Table row counts
            tables = ['users', 'products', 'purchase_requests', 'sales', 'ai_predictions', 'alerts']
            for table in tables:
                try:
                    result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()
                    stats[f"{table}_count"] = result[0] if result else 0
                except:
                    stats[f"{table}_count"] = 0
            
            # Database size (SQLite specific)
            if 'sqlite' in current_app.config.get('SQLALCHEMY_DATABASE_URI', ''):
                try:
                    result = db.session.execute(text("PRAGMA page_count")).fetchone()
                    page_count = result[0] if result else 0
                    
                    result = db.session.execute(text("PRAGMA page_size")).fetchone()
                    page_size = result[0] if result else 0
                    
                    stats['database_size_bytes'] = page_count * page_size
                    stats['database_size_mb'] = (page_count * page_size) / (1024 * 1024)
                except:
                    stats['database_size_bytes'] = 0
                    stats['database_size_mb'] = 0
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}


class QueryOptimizer:
    """Query optimization utilities"""
    
    @staticmethod
    def optimize_product_queries():
        """Optimize common product queries"""
        # Pre-load frequently accessed product data
        try:
            # Cache low stock products
            low_stock_products = db.session.query(
                db.text("""
                    SELECT id, name, category, quantity, low_stock_threshold
                    FROM products 
                    WHERE is_active = 1 AND quantity <= low_stock_threshold
                    ORDER BY quantity ASC
                """)
            ).fetchall()
            
            cache_manager.set('low_stock_products', low_stock_products, ttl=600)  # 10 minutes
            
            # Cache product categories
            categories = db.session.query(
                db.text("SELECT DISTINCT category FROM products WHERE is_active = 1")
            ).fetchall()
            
            cache_manager.set('product_categories', [cat[0] for cat in categories], ttl=1800)  # 30 minutes
            
            return True
            
        except Exception as e:
            print(f"Error optimizing product queries: {str(e)}")
            return False
    
    @staticmethod
    def optimize_analytics_queries():
        """Optimize analytics queries by pre-computing common metrics"""
        try:
            # Cache dashboard metrics
            from services.analytics_service import AnalyticsService
            
            # Pre-compute 30-day metrics
            metrics_30d = AnalyticsService.get_dashboard_metrics(30)
            cache_manager.set('dashboard_metrics_30d', metrics_30d, ttl=900)  # 15 minutes
            
            # Pre-compute 7-day metrics
            metrics_7d = AnalyticsService.get_dashboard_metrics(7)
            cache_manager.set('dashboard_metrics_7d', metrics_7d, ttl=300)  # 5 minutes
            
            # Cache sales chart data
            chart_data = AnalyticsService.get_sales_chart_data(30)
            cache_manager.set('sales_chart_data_30d', chart_data, ttl=600)  # 10 minutes
            
            return True
            
        except Exception as e:
            print(f"Error optimizing analytics queries: {str(e)}")
            return False


def init_performance_optimizations(app):
    """Initialize performance optimizations"""
    with app.app_context():
        # Create database indexes
        DatabaseOptimizer.create_performance_indexes()
        
        # Optimize common queries
        QueryOptimizer.optimize_product_queries()
        QueryOptimizer.optimize_analytics_queries()
        
        # Set up periodic cache cleanup
        @app.before_request
        def cleanup_cache():
            # Cleanup expired cache entries every 100 requests (approximately)
            if hasattr(g, 'request_count'):
                g.request_count += 1
            else:
                g.request_count = 1
            
            if g.request_count % 100 == 0:
                expired_count = cache_manager.cleanup_expired()
                if expired_count > 0:
                    print(f"🧹 Cleaned up {expired_count} expired cache entries")
        
        print("🚀 Performance optimizations initialized")


def get_performance_report() -> Dict[str, Any]:
    """Generate comprehensive performance report"""
    return {
        'database_stats': PerformanceMonitor.get_database_stats(),
        'cache_stats': cache_manager.get_stats(),
        'optimization_status': {
            'indexes_created': True,
            'caching_enabled': True,
            'query_optimization': True
        },
        'recommendations': _generate_performance_recommendations()
    }


def _generate_performance_recommendations() -> list:
    """Generate performance optimization recommendations"""
    recommendations = []
    
    # Check database size
    db_stats = PerformanceMonitor.get_database_stats()
    if db_stats.get('database_size_mb', 0) > 100:
        recommendations.append({
            'type': 'database',
            'priority': 'medium',
            'message': 'Database size is growing large. Consider archiving old data.',
            'action': 'Archive sales data older than 2 years'
        })
    
    # Check cache efficiency
    cache_stats = cache_manager.get_stats()
    if cache_stats['total_entries'] > 1000:
        recommendations.append({
            'type': 'cache',
            'priority': 'low',
            'message': 'Cache has many entries. Consider reducing TTL for some cached data.',
            'action': 'Review cache TTL settings'
        })
    
    # Check table sizes
    large_tables = []
    for key, value in db_stats.items():
        if key.endswith('_count') and value > 10000:
            table_name = key.replace('_count', '')
            large_tables.append(table_name)
    
    if large_tables:
        recommendations.append({
            'type': 'database',
            'priority': 'medium',
            'message': f'Large tables detected: {", ".join(large_tables)}',
            'action': 'Consider partitioning or archiving strategies'
        })
    
    return recommendations