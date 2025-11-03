#!/usr/bin/env python3
"""
Test fee save with proper authentication flow
"""
import sys
sys.path.append('/workspaces/saro')

from app import create_app
import json

app = create_app()

def test_with_auth():
    with app.test_client() as client:
        print("=== Testing with proper authentication ===")
        
        # First, try to login as a teacher
        # Check if there are any teachers in the system
        with app.app_context():
            from models import User, UserRole
            teacher = User.query.filter_by(role=UserRole.TEACHER, is_active=True).first()
            if not teacher:
                print("No active teachers found. Creating one...")
                from utils.auth import generate_password_hash
                teacher = User(
                    phoneNumber="01777777777",
                    first_name="Test",
                    last_name="Teacher", 
                    role=UserRole.TEACHER,
                    password_hash=generate_password_hash("password123"),
                    is_active=True
                )
                from models import db
                db.session.add(teacher)
                db.session.commit()
                print(f"Created teacher with ID: {teacher.id}")
            else:
                print(f"Using existing teacher: {teacher.first_name} {teacher.last_name}")
        
        # Login as the teacher
        login_data = {
            'phoneNumber': teacher.phoneNumber,
            'password': 'password123'
        }
        
        login_response = client.post('/api/auth/login', json=login_data)
        print(f"Login status: {login_response.status_code}")
        if login_response.status_code == 200:
            print("✅ Login successful")
            
            # Now test the fee endpoint
            fee_data = {'student_id': 1, 'month': 1, 'year': 2025, 'amount': 100}
            fee_response = client.post('/api/fees/monthly', json=fee_data)
            print(f"Fee save status: {fee_response.status_code}")
            
            if fee_response.status_code == 404:
                print("❌ Still getting 404 even with authentication")
                # Check the 404 log
                try:
                    with open('/tmp/last_404.log', 'r') as f:
                        log_content = f.read()
                        if log_content:
                            print("Recent 404 log entries:")
                            print(log_content[-500:])  # Last 500 chars
                        else:
                            print("No entries in 404 log")
                except FileNotFoundError:
                    print("No 404 log file found")
            else:
                print(f"✅ Fee endpoint responded: {fee_response.get_json()}")
        else:
            print(f"❌ Login failed: {login_response.get_json()}")

if __name__ == "__main__":
    test_with_auth()