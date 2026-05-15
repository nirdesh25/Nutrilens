import sys
sys.path.insert(0, '.')

print("Testing imports...")
try:
    from app.config import get_settings
    print("✓ Config imported")
    settings = get_settings()
    print(f"✓ Settings loaded: {settings.DATABASE_URL}")
except Exception as e:
    print(f"✗ Config failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.database import Base, engine, SessionLocal
    print("✓ Database imported")
except Exception as e:
    print(f"✗ Database failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.models import User
    print("✓ User model imported")
except Exception as e:
    print(f"✗ User model failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.schemas import UserCreate
    print("✓ UserCreate schema imported")
except Exception as e:
    print(f"✗ UserCreate schema failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.utils.auth import get_password_hash
    print("✓ Auth utils imported")
    hashed = get_password_hash("test123")
    print(f"✓ Password hashing works: {len(hashed)} chars")
except Exception as e:
    print(f"✗ Auth utils failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting database operations...")
try:
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    db = SessionLocal()
    test_user = User(
        name="Test",
        email="test@test.com",
        password_hash=get_password_hash("test123"),
        age=25
    )
    db.add(test_user)
    db.commit()
    print(f"✓ User created with ID: {test_user.id}")
    
    db.delete(test_user)
    db.commit()
    db.close()
    print("✓ User deleted")
    
except Exception as e:
    print(f"✗ Database operation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
