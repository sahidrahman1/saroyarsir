#!/usr/bin/env python3
"""
Test script to debug marks saving issue
"""
import requests
import json

# Test data
test_data = {
    "students": [
        {
            "user_id": 1,
            "marks_obtained": 85
        }
    ]
}

url = "http://127.0.0.1:5000/api/monthly-exams/1/individual-exams/1/marks"

# Test without authentication
print("Testing without authentication...")
response = requests.post(url, json=test_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print()

# Test database connection endpoint
print("Testing database connection...")
db_test_url = "http://127.0.0.1:5000/api/monthly-exams/test-db"
db_response = requests.get(db_test_url)
print(f"Status: {db_response.status_code}")
print(f"Response: {db_response.text}")
print()

# Test with a session (if we can establish one)
session = requests.Session()

# First try to login (assuming there's a login endpoint)
login_data = {
    "phoneNumber": "01762602056",  # Based on file I saw earlier
    "password": "123456"  # Common test password
}

login_url = "http://127.0.0.1:5000/api/auth/login"
print("Testing login...")
login_response = session.post(login_url, json=login_data)
print(f"Login Status: {login_response.status_code}")
print(f"Login Response: {login_response.text}")
print()

if login_response.status_code == 200:
    print("Testing marks saving with authenticated session...")
    marks_response = session.post(url, json=test_data)
    print(f"Marks Status: {marks_response.status_code}")
    print(f"Marks Response: {marks_response.text}")
    print()
    
    print("Testing database connection with authenticated session...")
    db_auth_response = session.get(db_test_url)
    print(f"DB Test Status: {db_auth_response.status_code}")
    print(f"DB Test Response: {db_auth_response.text}")