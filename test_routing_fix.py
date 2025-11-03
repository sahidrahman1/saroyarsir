#!/usr/bin/env python3
"""
Test routing fix for super admin vs teacher dashboard
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_super_admin_routing():
    """Test that super admin gets correct dashboard after login"""
    session = requests.Session()
    
    print("🧪 Testing Super Admin Routing...")
    
    # Step 1: Login as super admin
    login_data = {
        "phoneNumber": "01712345678",
        "password": "admin123"
    }
    
    print(f"📋 Logging in with super admin credentials...")
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return False
    
    login_result = response.json()
    print(f"✅ Login successful: {login_result.get('message', 'No message')}")
    print(f"📊 User role: {login_result['data']['user']['role']}")
    
    # Step 2: Access root route (should redirect to super admin dashboard)
    print(f"🏠 Accessing root route...")
    response = session.get(f"{BASE_URL}/")
    
    if response.status_code != 200:
        print(f"❌ Root route failed: {response.status_code}")
        return False
    
    # Check if we got the super admin dashboard
    if "Super Admin Dashboard" in response.text or "super_admin_sms" in response.text:
        print("✅ Super admin correctly gets super admin dashboard")
    else:
        print("❌ Super admin still getting wrong dashboard")
        print("First 500 chars of response:")
        print(response.text[:500])
        return False
    
    # Step 3: Try accessing teacher route (should redirect back to super admin)
    print(f"🏫 Trying to access teacher route...")
    response = session.get(f"{BASE_URL}/teacher")
    
    if response.status_code == 302:  # Redirect
        print("✅ Super admin correctly redirected from teacher route")
    elif "Super Admin Dashboard" in response.text:
        print("✅ Super admin correctly gets super admin dashboard on teacher route")
    else:
        print("⚠️  Unexpected response for teacher route access")
    
    return True

def test_teacher_routing():
    """Test that teacher gets correct dashboard after login"""
    session = requests.Session()
    
    print("\n🧪 Testing Teacher Routing...")
    
    # Step 1: Login as teacher
    login_data = {
        "phoneNumber": "01887654321",
        "password": "teacher123"
    }
    
    print(f"📋 Logging in with teacher credentials...")
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Teacher login failed: {response.status_code} - {response.text}")
        return False
    
    login_result = response.json()
    print(f"✅ Teacher login successful: {login_result.get('message', 'No message')}")
    print(f"📊 User role: {login_result['data']['user']['role']}")
    
    # Step 2: Access root route (should redirect to teacher dashboard)
    print(f"🏠 Accessing root route...")
    response = session.get(f"{BASE_URL}/")
    
    if response.status_code != 200:
        print(f"❌ Root route failed: {response.status_code}")
        return False
    
    # Check if we got the teacher dashboard
    if "Teacher Dashboard" in response.text and "super_admin_sms" not in response.text:
        print("✅ Teacher correctly gets teacher dashboard")
    else:
        print("❌ Teacher getting wrong dashboard")
        print("First 500 chars of response:")
        print(response.text[:500])
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Testing Routing Fix for Super Admin vs Teacher Dashboard")
    print("=" * 60)
    
    try:
        # Test super admin routing
        super_admin_ok = test_super_admin_routing()
        
        # Test teacher routing
        teacher_ok = test_teacher_routing()
        
        print("\n" + "=" * 60)
        print("📋 Test Results Summary:")
        print(f"Super Admin Routing: {'✅ PASS' if super_admin_ok else '❌ FAIL'}")
        print(f"Teacher Routing: {'✅ PASS' if teacher_ok else '❌ FAIL'}")
        
        if super_admin_ok and teacher_ok:
            print("🎉 ALL TESTS PASSED - Routing is working correctly!")
        else:
            print("❌ Some tests failed - Check the routing logic")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()