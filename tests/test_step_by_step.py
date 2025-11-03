#!/usr/bin/env python3
"""
Test super admin routing step by step
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_super_admin_step_by_step():
    """Test super admin login and routing step by step"""
    session = requests.Session()
    
    print("🔧 Testing Super Admin Routing Step by Step")
    print("=" * 50)
    
    # Step 1: Login
    print("1️⃣ Testing Login...")
    login_data = {
        "phoneNumber": "01712345678",
        "password": "admin123"
    }
    
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    login_result = response.json()
    print(f"✅ Login Success")
    print(f"User Role: {login_result['data']['user']['role']}")
    
    # Step 2: Check /api/auth/me endpoint
    print("\n2️⃣ Testing Session Check...")
    response = session.get(f"{BASE_URL}/api/auth/me")
    print(f"Session Check Status: {response.status_code}")
    
    if response.status_code == 200:
        me_result = response.json()
        print(f"✅ Session Valid")
        print(f"Current Role: {me_result['data']['role']}")
    else:
        print(f"❌ Session Invalid: {response.text}")
        return
    
    # Step 3: Test root route
    print("\n3️⃣ Testing Root Route...")
    response = session.get(f"{BASE_URL}/")
    print(f"Root Route Status: {response.status_code}")
    
    if response.status_code == 200:
        # Check what dashboard we got
        content = response.text
        if "Super Admin Dashboard" in content:
            print("✅ Got Super Admin Dashboard")
        elif "Teacher Dashboard" in content:
            print("❌ Got Teacher Dashboard (WRONG!)")
            # Check the page title to confirm
            import re
            title_match = re.search(r'<title>(.*?)</title>', content)
            if title_match:
                print(f"Page Title: {title_match.group(1)}")
        elif "Student Dashboard" in content:
            print("❌ Got Student Dashboard (WRONG!)")
        elif "Smart Garden Hub" in content or "Login" in content:
            print("❌ Got Login Page (Session not working)")
        else:
            print("❓ Got Unknown Page")
            print("First 300 chars:")
            print(content[:300])
    else:
        print(f"❌ Root route failed: {response.status_code}")
    
    # Step 4: Test direct super admin route
    print("\n4️⃣ Testing Direct Super Admin Route...")
    response = session.get(f"{BASE_URL}/super")
    print(f"Super Route Status: {response.status_code}")
    
    if response.status_code == 200:
        if "Super Admin Dashboard" in response.text:
            print("✅ Direct super admin route works")
        else:
            print("❌ Direct super admin route wrong content")
    else:
        print(f"❌ Direct super admin route failed")

if __name__ == "__main__":
    test_super_admin_step_by_step()