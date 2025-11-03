#!/usr/bin/env python3

import requests
import json
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test credentials
login_data = {
    'username': 'admin',
    'password': 'admin123'
}

base_url = 'http://127.0.0.1:5000'

# Create session to maintain cookies
session = requests.Session()

print("Testing SMS Templates API...")

# Step 1: Login
try:
    login_response = session.post(f'{base_url}/login', data=login_data, allow_redirects=False)
    if login_response.status_code in [200, 302]:
        print("✅ Login successful")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text[:200]}")
        exit(1)
except Exception as e:
    print(f"❌ Login error: {e}")
    exit(1)

# Step 2: Test Templates API
try:
    templates_response = session.get(f'{base_url}/api/sms/templates')
    print(f"Templates API Status: {templates_response.status_code}")
    
    if templates_response.status_code == 200:
        templates = templates_response.json()
        print("Templates Response:")
        print(json.dumps(templates, indent=2))
        
        print(f"\n✅ Found {len(templates)} templates")
        for template in templates:
            print(f"  - {template['name']}: {template['char_count']} chars")
    else:
        print(f"Templates Response: {templates_response.json()}")
        
except Exception as e:
    print(f"❌ Templates API error: {e}")

# Step 3: Test Balance API
try:
    balance_response = session.get(f'{base_url}/api/sms/balance')
    print(f"\nBalance API Status: {balance_response.status_code}")
    
    if balance_response.status_code == 200:
        balance = balance_response.json()
        print(f"Balance Response: {balance}")
    else:
        print(f"Balance Error: {balance_response.text}")
        
except Exception as e:
    print(f"❌ Balance API error: {e}")

print("\nTest completed!")