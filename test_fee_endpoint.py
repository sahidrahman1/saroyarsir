#!/usr/bin/env python3
"""
Test fee endpoint directly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import db, User, UserRole
import json

def test_fee_endpoint():
    app = create_app()
    
    with app.test_client() as client:
        # First login as a teacher
        print("Step 1: Logging in as teacher...")
        teacher = None
        with app.app_context():
            teacher = User.query.filter_by(role=UserRole.TEACHER, is_active=True).first()
            if not teacher:
                print("❌ No active teacher found in database")
                return
            print(f"✓ Found teacher: {teacher.phone}")
        
        # Login
        login_response = client.post('/api/auth/login', 
            json={'phone': teacher.phone, 'password': 'password123'},
            content_type='application/json')
        
        print(f"Login status: {login_response.status_code}")
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.get_data(as_text=True)}")
            return
        
        print("✓ Login successful")
        
        # Now try to POST to monthly fees
        print("\nStep 2: Testing POST /api/fees/monthly...")
        payload = {
            'student_id': 1,
            'month': 1,
            'year': 2025,
            'amount': 500
        }
        
        fee_response = client.post('/api/fees/monthly',
            json=payload,
            content_type='application/json')
        
        print(f"Fee POST status: {fee_response.status_code}")
        print(f"Response: {fee_response.get_data(as_text=True)[:500]}")
        
        if fee_response.status_code == 200 or fee_response.status_code == 201:
            print("✓ Fee saved successfully!")
        else:
            print(f"❌ Fee save failed with status {fee_response.status_code}")
            
        # Test GET
        print("\nStep 3: Testing GET /api/fees/monthly...")
        get_response = client.get('/api/fees/monthly?batch_id=1&year=2025')
        print(f"GET status: {get_response.status_code}")
        if get_response.status_code == 200:
            data = json.loads(get_response.get_data(as_text=True))
            print(f"✓ GET successful, returned {len(data.get('data', []))} records")

if __name__ == '__main__':
    test_fee_endpoint()
