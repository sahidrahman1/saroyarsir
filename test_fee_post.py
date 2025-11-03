"""Test POST to /api/fees/monthly with proper authentication"""
import requests
from requests.cookies import RequestsCookieJar

# First, login as a teacher
login_url = 'http://127.0.0.1:5000/api/auth/login'
login_data = {
    'phone': '01762602056',  # Teacher phone from earlier
    'password': '123456'
}

session = requests.Session()

print("1. Logging in as teacher...")
login_response = session.post(login_url, json=login_data)
print(f"   Login status: {login_response.status_code}")

if login_response.status_code == 200:
    print(f"   Login response: {login_response.json()}")
    
    # Now test the fee POST
    fee_url = 'http://127.0.0.1:5000/api/fees/monthly'
    fee_data = {
        'student_id': 1,
        'month': 1,
        'year': 2025,
        'amount': 500
    }
    
    print("\n2. POSTing to /api/fees/monthly...")
    fee_response = session.post(fee_url, json=fee_data)
    print(f"   Fee POST status: {fee_response.status_code}")
    print(f"   Fee POST response: {fee_response.text[:500]}")
    
    if fee_response.status_code == 404:
        print("\n3. ERROR: Got 404! Checking registered routes...")
        # Try to get flask routes
        try:
            import sys
            sys.path.insert(0, '/workspaces/saro')
            from app import create_app
            app = create_app()
            print("\n   Registered /api/fees routes:")
            with app.app_context():
                for rule in app.url_map.iter_rules():
                    if '/fees' in rule.rule:
                        print(f"   {rule.methods} {rule.rule}")
        except Exception as e:
            print(f"   Could not list routes: {e}")
else:
    print(f"   Login failed: {login_response.text}")
