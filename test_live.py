#!/usr/bin/env python3
"""
Test the actual running server instead of test client
"""
import requests
import time

def test_live_server():
    base_url = "http://127.0.0.1:5000"
    
    print("=== Testing Live Server Endpoints ===")
    
    # Test fee simple endpoint
    print("\n1. Testing fee simple endpoint...")
    try:
        response = requests.post(f"{base_url}/api/fees/monthly-simple", 
                               json={"test": "data"}, 
                               timeout=5)
        print(f"Simple fee endpoint: {response.status_code}")
        if response.status_code == 200:
            print("✅ Simple fee endpoint WORKS!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Simple fee failed: {response.text}")
    except Exception as e:
        print(f"❌ Simple fee error: {e}")
    
    # Test original fee endpoint
    print("\n2. Testing original fee endpoint...")
    try:
        fee_data = {
            "student_id": 1,
            "month": 1,
            "year": 2025,
            "amount": 100
        }
        response = requests.post(f"{base_url}/api/fees/monthly", 
                               json=fee_data, 
                               timeout=5)
        print(f"Original fee endpoint: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ Original fee endpoint WORKS!")
            print(f"Response: {response.json()}")
        elif response.status_code == 500:
            print(f"⚠️ Server error (but route found): {response.json()}")
        else:
            print(f"❌ Original fee failed: {response.text}")
    except Exception as e:
        print(f"❌ Original fee error: {e}")
    
    # Test student endpoint
    print("\n3. Testing student endpoint...")
    try:
        student_data = {
            "firstName": "Test",
            "lastName": "Student", 
            "guardianPhone": "01777000099",  # New unique number
            "guardianName": "Test Guardian",
            "school": "Test School"
        }
        response = requests.post(f"{base_url}/api/students", 
                               json=student_data, 
                               timeout=5)
        print(f"Student endpoint: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ Student endpoint WORKS!")
            print(f"Response: {response.json()}")
        elif response.status_code == 409:
            print("⚠️ Student phone exists (but endpoint works)")
        else:
            print(f"❌ Student failed: {response.text}")
    except Exception as e:
        print(f"❌ Student error: {e}")

if __name__ == "__main__":
    test_live_server()