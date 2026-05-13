#!/usr/bin/env python3
"""Direct test of registration endpoint"""

import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("Testing registration endpoint...")
print("=" * 60)

# Test data
test_data = {
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "age": 25
}

print(f"\nSending POST to /api/auth/register")
print(f"Data: {test_data}")

try:
    response = client.post("/api/auth/register", json=test_data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("\nâœ“âœ“âœ“ REGISTRATION SUCCESSFUL âœ“âœ“âœ“")
    else:
        print(f"\nâœ—âœ—âœ— REGISTRATION FAILED âœ—âœ—âœ—")
        
except Exception as e:
    print(f"\nâœ—âœ—âœ— ERROR: {e}")
    import traceback
    traceback.print_exc()
