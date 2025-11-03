#!/usr/bin/env python3

import requests
import json
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test credentials for the new teacher
login_data = {
    'username': '01762602056',
    'password': 'sir@123@'
}

base_url = 'http://127.0.0.1:5000'

# Create session to maintain cookies
session = requests.Session()

print("Testing new teacher login...")

# Step 1: Login
try:
    login_response = session.post(f'{base_url}/login', data=login_data, allow_redirects=False)
    if login_response.status_code in [200, 302]:
        print("✅ Teacher login successful")
        print(f"   Response status: {login_response.status_code}")
        
        # Check if redirected to dashboard
        if login_response.status_code == 302:
            location = login_response.headers.get('Location', '')
            print(f"   Redirected to: {location}")
            
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text[:200]}")
        exit(1)
except Exception as e:
    print(f"❌ Login error: {e}")
    exit(1)

# Step 2: Test SMS Templates API
try:
    templates_response = session.get(f'{base_url}/api/sms/templates')
    print(f"\nSMS Templates API Status: {templates_response.status_code}")
    
    if templates_response.status_code == 200:
        templates = templates_response.json()
        print(f"✅ Teacher can access SMS templates: {len(templates)} templates found")
    else:
        print(f"❌ Template access failed: {templates_response.json()}")
        
except Exception as e:
    print(f"❌ Templates API error: {e}")

# Step 3: Test Balance API
try:
    balance_response = session.get(f'{base_url}/api/sms/balance')
    print(f"\nSMS Balance API Status: {balance_response.status_code}")
    
    if balance_response.status_code == 200:
        balance = balance_response.json()
        print(f"✅ Teacher SMS balance: {balance.get('balance', 0)}")
    else:
        print(f"❌ Balance API failed: {balance_response.text}")
        
except Exception as e:
    print(f"❌ Balance API error: {e}")

print(f"\n🎯 Teacher Login Summary:")
print(f"   📱 Phone: 01762602056")
print(f"   🔑 Password: sir@123@")
print(f"   🌐 Login URL: {base_url}/login")
print(f"   📋 Dashboard: {base_url}/teacher/dashboard")
print("\nTest completed!")