#!/usr/bin/env python3
"""
Simple test to check login response and routing
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_login_response():
    """Test login response structure"""
    session = requests.Session()
    
    print("🧪 Testing Login Response Structure...")
    
    # Login as super admin
    login_data = {
        "phoneNumber": "01712345678",
        "password": "admin123"
    }
    
    print(f"📋 Logging in with super admin credentials...")
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response keys: {list(result.keys())}")
        if 'data' in result:
            print(f"Data keys: {list(result['data'].keys())}")
            if 'user' in result['data']:
                print(f"User role: {result['data']['user']['role']}")

if __name__ == "__main__":
    test_login_response()