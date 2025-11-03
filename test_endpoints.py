#!/usr/bin/env python3
"""
Quick test script to verify both student and fee endpoints work
"""
import sys
import os
sys.path.append('/workspaces/saro')

from app import create_app
from models import db
import json

app = create_app()

def test_endpoints():
    with app.test_client() as client:
        with app.app_context():
            print("Testing student creation endpoint...")
            
            # Test student creation
            student_data = {
                "firstName": "Test",
                "lastName": "Student", 
                "guardianPhone": "01777000002",
                "guardianName": "Test Guardian",
                "school": "Test School"
            }
            
            response = client.post('/api/students', 
                                 json=student_data,
                                 headers={'Content-Type': 'application/json'})
            
            print(f"Student creation status: {response.status_code}")
            if response.status_code == 401:
                print("✓ Student endpoint working (needs authentication)")
            elif response.status_code == 400:
                print(f"✗ Student validation error: {response.get_json()}")
            elif response.status_code in [200, 201]:
                print("✓ Student created successfully")
            else:
                print(f"Student response: {response.get_json()}")
            
            print("\nTesting fee save endpoint...")
            
            # Test fee save
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
            if response.status_code == 401:
                print("✓ Fee endpoint working (needs authentication)")
            elif response.status_code == 404:
                print("✗ Fee endpoint not found - route registration issue")
            elif response.status_code in [200, 201]:
                print("✓ Fee saved successfully")
            else:
                print(f"Fee response: {response.get_json()}")

if __name__ == "__main__":
    test_endpoints()