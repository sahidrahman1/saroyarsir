#!/usr/bin/env python3

import requests
import json

# Test the new teacher login via JSON API
login_data = {
    'phoneNumber': '01762602056',
    'password': 'sir@123@'
}

base_url = 'http://127.0.0.1:5000'

print("Testing teacher login via JSON API...")

try:
    response = requests.post(f'{base_url}/api/auth/login', json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print("❌ Login failed!")
        try:
            error_data = response.json()
            print(f"Error: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Error text: {response.text}")
            
except Exception as e:
    print(f"❌ Request failed: {e}")

print("\nTest completed!")