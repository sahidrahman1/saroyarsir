#!/usr/bin/env python3
"""
Test both student and fee endpoints directly
"""
import sys
import os
sys.path.append('/workspaces/saro')

from app import create_app
from models import db
import json

app = create_app()

def test_both_endpoints():
    with app.test_client() as client:
        with app.app_context():
            print("=== Testing Student Creation ===")
            
            student_data = {
                "firstName": "Test",
                "lastName": "Student", 
                "guardianPhone": "01777000010",
                "guardianName": "Test Guardian",
                "school": "Test School"
            }
            
            response = client.post('/api/students', 
                                 json=student_data,
                                 headers={'Content-Type': 'application/json'})
            
            print(f"Student creation status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                print("✅ Student creation WORKS!")
                print(f"Response: {response.get_json()}")
            else:
                print(f"❌ Student creation failed: {response.get_json()}")
            
            print("\n=== Testing Fee Save ===")
            
            fee_data = {
                "student_id": 1,
                "month": 1,
                "year": 2025,
                "amount": 100
            }
            
            response = client.post('/api/fees/monthly', 
                                 json=fee_data,
                                 headers={'Content-Type': 'application/json'})
            
            print(f"Fee save status: {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                print("✅ Fee save WORKS!")
                print(f"Response: {response.get_json()}")
            elif response.status_code == 404:
                print("❌ Fee endpoint returns 404 - route not found")
            else:
                print(f"❌ Fee save failed: {response.get_json()}")

if __name__ == "__main__":
    test_both_endpoints()