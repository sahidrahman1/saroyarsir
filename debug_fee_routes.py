#!/usr/bin/env python3
"""
Comprehensive test to debug the fee save 404 issue
"""
import sys
sys.path.append('/workspaces/saro')

from app import create_app
import json

app = create_app()

def test_routes():
    with app.test_client() as client:
        print("=== Route Registration Test ===")
        
        # Test if routes are registered
        with app.app_context():
            routes = []
            for rule in app.url_map.iter_rules():
                if 'fees' in str(rule.rule) and 'monthly' in str(rule.rule):
                    routes.append(f"{list(rule.methods)} {rule.rule}")
            
            print("Fee monthly routes registered:")
            for route in routes:
                print(f"  {route}")
        
        print("\n=== Direct Route Test ===")
        
        # Test original route
        response = client.post('/api/fees/monthly', 
                             json={'student_id': 1, 'month': 1, 'year': 2025, 'amount': 100})
        print(f"POST /api/fees/monthly: {response.status_code}")
        if response.status_code != 404:
            print(f"  Response: {response.get_json()}")
        else:
            print("  ERROR: 404 Not Found - route not working")
        
        # Test new route
        response = client.post('/api/fees/monthly-save', 
                             json={'student_id': 1, 'month': 1, 'year': 2025, 'amount': 100})
        print(f"POST /api/fees/monthly-save: {response.status_code}")
        if response.status_code != 404:
            print(f"  Response: {response.get_json()}")
        else:
            print("  ERROR: 404 Not Found - route not working")
        
        print("\n=== Session Test ===")
        
        # Test with session (simulate login)
        with client.session_transaction() as sess:
            sess['user_id'] = 1  # Simulate logged in user
        
        response = client.post('/api/fees/monthly', 
                             json={'student_id': 1, 'month': 1, 'year': 2025, 'amount': 100})
        print(f"POST /api/fees/monthly (with session): {response.status_code}")
        print(f"  Response: {response.get_json()}")

if __name__ == "__main__":
    test_routes()