#!/usr/bin/env python3
"""
Initialize database with tables.
Run this script to create all database tables.
"""

from app.database import Base, engine
from app.models import User, Grocery, ScanResult, WasteLog, HealthProfile, SensorData

def init_database():
    """Create all database tables."""
    print("Creating database tables...")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully!")
        print("\nCreated tables:")
        print("  - users")
        print("  - groceries")
        print("  - scan_results")
        print("  - waste_logs")
        print("  - health_profiles")
        print("  - sensor_data")
        
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("NutriLens AI - Database Initialization")
    print("=" * 60)
    print()
    
    success = init_database()
    
    if success:
        print("\n✓ Database is ready!")
        print("\nNext steps:")
        print("1. Run the backend: python main.py")
        print("2. Visit API docs: http://localhost:8000/docs")
        print("3. Register a user and start using the API")
    else:
        print("\n✗ Database initialization failed")
        print("Check your DATABASE_URL in .env file")
