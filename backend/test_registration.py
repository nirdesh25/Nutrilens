#!/usr/bin/env python3
"""
Test script to diagnose registration issues.
"""

import sys
import traceback

print("=" * 60)
print("Testing Registration Components")
print("=" * 60)

# Test 1: Import settings
print("\n1. Testing settings import...")
try:
    from app.config import get_settings
    settings = get_settings()
    print(f"   ✓ Settings loaded")
    print(f"   - DATABASE_URL: {settings.DATABASE_URL}")
    print(f"   - SECRET_KEY: {'*' * 20} (hidden)")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Import database
print("\n2. Testing database connection...")
try:
    from app.database import engine, SessionLocal, Base
    print(f"   ✓ Database engine created")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Import models
print("\n3. Testing model imports...")
try:
    from app.models import User, Grocery, ScanResult, WasteLog, HealthProfile, SensorData
    print(f"   ✓ All models imported")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Create tables
print("\n4. Testing table creation...")
try:
    Base.metadata.create_all(bind=engine)
    print(f"   ✓ Tables created/verified")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test password hashing
print("\n5. Testing password hashing...")
try:
    from app.utils.auth import get_password_hash, verify_password
    test_password = "testpassword123"
    hashed = get_password_hash(test_password)
    verified = verify_password(test_password, hashed)
    print(f"   ✓ Password hashing works")
    print(f"   - Hash length: {len(hashed)}")
    print(f"   - Verification: {verified}")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test user creation
print("\n6. Testing user creation in database...")
try:
    db = SessionLocal()
    
    # Check if test user exists
    test_email = "test@example.com"
    existing = db.query(User).filter(User.email == test_email).first()
    if existing:
        db.delete(existing)
        db.commit()
        print(f"   - Deleted existing test user")
    
    # Create test user
    test_user = User(
        name="Test User",
        email=test_email,
        password_hash=get_password_hash("password123"),
        age=25
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    print(f"   ✓ User created successfully")
    print(f"   - ID: {test_user.id}")
    print(f"   - Name: {test_user.name}")
    print(f"   - Email: {test_user.email}")
    
    # Clean up
    db.delete(test_user)
    db.commit()
    db.close()
    
except Exception as e:
    print(f"   ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 7: Test schemas
print("\n7. Testing Pydantic schemas...")
try:
    from app.schemas import UserCreate, UserResponse
    
    # Test UserCreate validation
    user_data = UserCreate(
        name="Test User",
        email="test@example.com",
        password="password123",
        age=25
    )
    print(f"   ✓ UserCreate schema works")
    print(f"   - Name: {user_data.name}")
    print(f"   - Email: {user_data.email}")
    
except Exception as e:
    print(f"   ✗ Failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All tests passed! Registration should work.")
print("=" * 60)
print("\nIf registration still fails, check:")
print("1. Backend console for detailed error messages")
print("2. Browser console for network errors")
print("3. Make sure both servers are running")
