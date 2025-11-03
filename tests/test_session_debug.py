#!/usr/bin/env python3
"""
Test session and routing
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_session_and_routing():
    """Test session creation and routing"""
    session = requests.Session()
    
    print("🧪 Testing Session and Routing...")
    
    # Step 1: Login as super admin
    login_data = {
        "phoneNumber": "01712345678",
        "password": "admin123"
    }
    
    print(f"📋 Logging in with super admin credentials...")
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return
    
    print(f"✅ Login successful")
    
    # Step 2: Check session
    print(f"🔍 Checking session...")
    response = session.get(f"{BASE_URL}/api/auth/me")
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"📊 Current user role: {user_data['data']['role']}")
    else:
        print(f"❌ Session check failed: {response.status_code}")
    
    # Step 3: Access root route with debug info
    print(f"🏠 Accessing root route...")
    response = session.get(f"{BASE_URL}/")
    
    print(f"Response status: {response.status_code}")
    
    # Look for specific dashboard indicators
    if "Super Admin Dashboard" in response.text:
        print("✅ Got Super Admin Dashboard")
    elif "Teacher Dashboard" in response.text:
        print("❌ Got Teacher Dashboard instead")
        print("Checking for session debug...")
        # Look for any debug info in the response
        if "dashboard_teacher.html" in response.text:
            print("❌ Confirmed: Rendering teacher template")
    else:
        print("❓ Got unknown dashboard")
        print("First 200 chars:")
        print(response.text[:200])

if __name__ == "__main__":
    test_session_and_routing()