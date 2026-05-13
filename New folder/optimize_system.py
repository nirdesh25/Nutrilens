#!/usr/bin/env python3
"""
System Optimization Script for Smart Inventory Management System
Applies all performance optimizations and improvements
"""

import os
import sys
import time
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n[{step}] {description}")
    print("-" * 40)

def run_optimization():
    """Run all system optimizations"""
    print_header("SMART INVENTORY SYSTEM - PERFORMANCE OPTIMIZATION")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import Flask app
        from app import create_app
        from extensions import db
        
        app = create_app()
        
        with app.app_context():
            print_step("1", "Database Optimization")
            
            # Create performance indexes
            from utils.performance_optimization import DatabaseOptimizer
            if DatabaseOptimizer.create_performance_indexes():
                print("✅ Database indexes created successfully")
            else:
                print("❌ Failed to create database indexes")
            
            # Analyze query performance
            result = DatabaseOptimizer.analyze_query_performance()
            if result['status'] == 'success':
                print("✅ Database query analysis completed")
                if 'table_stats' in result:
                    print("📊 Table Statistics:")
                    for table, count in result['table_stats'].items():
                        print(f"   - {table}: {count:,} records")
            else:
                print(f"❌ Database analysis failed: {result.get('message', 'Unknown error')}")
            
            print_step("2", "Cache Optimization")
            
            # Initialize and warm up cache
            from services.cache_service import CacheService
            if CacheService.warm_up_cache():
                print("✅ Cache warmed up successfully")
            else:
                print("❌ Cache warm-up failed")
            
            # Optimize cache settings
            if CacheService.optimize_cache_settings():
                print("✅ Cache settings optimized")
            else:
                print("❌ Cache optimization failed")
            
            print_step("3", "Query Optimization")
            
            # Optimize product queries
            from utils.performance_optimization import QueryOptimizer
            if QueryOptimizer.optimize_product_queries():
                print("✅ Product queries optimized")
            else:
                print("❌ Product query optimization failed")
            
            # Optimize analytics queries
            if QueryOptimizer.optimize_analytics_queries():
                print("✅ Analytics queries optimized")
            else:
                print("❌ Analytics query optimization failed")
            
            print_step("4", "Performance Report")
            
            # Generate performance report
            from utils.performance_optimization import get_performance_report
            report = get_performance_report()
            
            print("📈 Performance Metrics:")
            db_stats = report.get('database_stats', {})
            for key, value in db_stats.items():
                if not key.startswith('error'):
                    if 'size_mb' in key:
                        print(f"   - {key.replace('_', ' ').title()}: {value:.1f} MB")
                    elif 'count' in key:
                        print(f"   - {key.replace('_', ' ').title()}: {value:,}")
                    else:
                        print(f"   - {key.replace('_', ' ').title()}: {value}")
            
            # Cache health report
            cache_health = CacheService.get_cache_health_report()
            print(f"\n🧠 Cache Health Score: {cache_health['health_score']}/100")
            print(f"   - Total Entries: {cache_health['cache_stats']['total_entries']:,}")
            print(f"   - Memory Usage: {cache_health['cache_stats']['memory_usage_estimate'] / 1024 / 1024:.1f} MB")
            print(f"   - Estimated Hit Rate: {cache_health['estimated_hit_rate'] * 100:.1f}%")
            
            if cache_health['issues']:
                print("\n⚠️  Cache Issues:")
                for issue in cache_health['issues']:
                    print(f"   - {issue}")
            
            if report.get('recommendations'):
                print("\n💡 Recommendations:")
                for rec in report['recommendations']:
                    priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
                    print(f"   {priority_icon} {rec['message']}")
                    if rec.get('action'):
                        print(f"      Action: {rec['action']}")
            
            print_step("5", "System Health Check")
            
            # Check system resources
            try:
                import psutil
                
                # Memory usage
                memory = psutil.virtual_memory()
                print(f"💾 Memory Usage: {memory.percent}% ({memory.used / 1024**3:.1f}GB / {memory.total / 1024**3:.1f}GB)")
                
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                print(f"🖥️  CPU Usage: {cpu_percent}%")
                
                # Disk usage
                disk = psutil.disk_usage('/')
                print(f"💿 Disk Usage: {disk.percent}% ({disk.used / 1024**3:.1f}GB / {disk.total / 1024**3:.1f}GB)")
                
                # Process info
                process = psutil.Process()
                print(f"🔧 Process Memory: {process.memory_info().rss / 1024**2:.1f} MB")
                
            except ImportError:
                print("⚠️  psutil not available - install with: pip install psutil")
            except Exception as e:
                print(f"⚠️  System health check failed: {str(e)}")
            
            print_step("6", "Final Validation")
            
            # Validate optimizations
            optimization_status = report.get('optimization_status', {})
            all_optimized = True
            
            for feature, enabled in optimization_status.items():
                status_icon = "✅" if enabled else "❌"
                print(f"   {status_icon} {feature.replace('_', ' ').title()}: {'Enabled' if enabled else 'Disabled'}")
                if not enabled:
                    all_optimized = False
            
            print_header("OPTIMIZATION COMPLETE")
            
            if all_optimized:
                print("🎉 All optimizations applied successfully!")
                print("🚀 Your Smart Inventory System is now running at peak performance!")
            else:
                print("⚠️  Some optimizations could not be applied.")
                print("📋 Check the recommendations above for manual steps.")
            
            print(f"\n⏱️  Total optimization time: {time.time() - start_time:.2f} seconds")
            print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Save optimization report
            report_file = f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            try:
                with open(report_file, 'w') as f:
                    f.write(f"Smart Inventory System - Optimization Report\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"Database Statistics:\n")
                    for key, value in db_stats.items():
                        f.write(f"  {key}: {value}\n")
                    f.write(f"\nCache Health Score: {cache_health['health_score']}/100\n")
                    f.write(f"Cache Entries: {cache_health['cache_stats']['total_entries']}\n")
                    f.write(f"Memory Usage: {cache_health['cache_stats']['memory_usage_estimate'] / 1024 / 1024:.1f} MB\n")
                    
                print(f"\n📄 Optimization report saved to: {report_file}")
            except Exception as e:
                print(f"⚠️  Could not save report: {str(e)}")
            
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("💡 Make sure you're in the correct directory and all dependencies are installed")
        print("   Run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Optimization failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    start_time = time.time()
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found!")
        print("💡 Please run this script from the Smart Inventory System root directory")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    run_optimization()