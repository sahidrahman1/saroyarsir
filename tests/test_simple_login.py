#!/usr/bin/env python3
"""
Test login API with simple request
"""
import requests
import json

def test_simple_login():
    """Test login with minimal data"""
    url = "http://localhost:5001/api/auth/login"
    data = {
        "phoneNumber": "01712345678",
        "password": "admin123"
    }
    
    print("🔐 Testing Simple Login")
    print(f"URL: {url}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful!")
            print(f"User role: {result['data']['user']['role']}")
        else:
            print("❌ Login failed")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server might be down")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_login()