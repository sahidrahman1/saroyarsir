#!/usr/bin/env python3
"""
Test teacher loading API
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_teacher_loading():
    """Test that teachers can be loaded"""
    session = requests.Session()
    
    print("🧪 Testing Teacher Loading API...")
    
    # Step 1: Login as super admin
    login_data = {
        "phoneNumber": "01712345678",
        "password": "admin123"
    }
    
    print(f"📋 Logging in as super admin...")
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return
    
    print(f"✅ Login successful")
    
    # Step 2: Test teachers endpoint
    print(f"👥 Loading teachers...")
    response = session.get(f"{BASE_URL}/api/users/teachers")
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            teachers = data.get('data', [])
            print(f"✅ Found {len(teachers)} teachers")
            for i, teacher in enumerate(teachers, 1):
                print(f"  {i}. {teacher.get('name')} ({teacher.get('phoneNumber')}) - SMS: {teacher.get('smsCount', 0)}")
        else:
            print(f"❌ API returned success=false: {data}")
    else:
        print(f"❌ Failed to load teachers: {response.status_code}")

if __name__ == "__main__":
    test_teacher_loading()