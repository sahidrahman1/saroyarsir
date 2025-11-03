#!/usr/bin/env python3
"""
Simple test for basic CRUD operations
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5001"

def test_login():
    """Test login functionality"""
    print("Testing login...")
    
    # Test with phoneNumber (as expected by auth.py)
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phoneNumber": "01812345678",
        "password": "teacher123"
    })
    
    print(f"Login response status: {response.status_code}")
    if response.status_code != 200:
        print(f"Login response text: {response.text}")
        return None
    
    print("✅ Login successful!")
    return response.cookies

def test_basic_operations():
    """Test basic CRUD operations"""
    print("\n🧪 TESTING BASIC OPERATIONS")
    print("=" * 50)
    
    # Login first
    cookies = test_login()
    if not cookies:
        print("❌ Login failed, cannot continue")
        return
    
    session = requests.Session()
    session.cookies.update(cookies)
    
    # Test get students
    print("\n📖 Testing GET students...")
    students_response = session.get(f"{BASE_URL}/api/students")
    print(f"Students status: {students_response.status_code}")
    
    if students_response.status_code == 200:
        data = students_response.json()
        count = len(data.get('data', []))
        print(f"✅ Retrieved {count} students")
    else:
        print(f"❌ Students failed: {students_response.text}")
    
    # Test get batches
    print("\n📖 Testing GET batches...")
    batches_response = session.get(f"{BASE_URL}/api/batches")
    print(f"Batches status: {batches_response.status_code}")
    
    if batches_response.status_code == 200:
        data = batches_response.json()
        print(f"✅ Retrieved batches data: {data.get('message', 'N/A')}")
    else:
        print(f"❌ Batches failed: {batches_response.text}")
    
    # Test create student (simple)
    print("\n📝 Testing CREATE student...")
    student_data = {
        "firstName": "Simple",
        "lastName": "Test",
        "guardianName": "Test Guardian",
        "guardianPhone": "01988776655",  # Unique phone
        "school": "Test School"
    }
    
    create_response = session.post(f"{BASE_URL}/api/students", json=student_data)
    print(f"Create student status: {create_response.status_code}")
    
    if create_response.status_code == 201:
        student_info = create_response.json()
        student_id = student_info['data']['id']
        print(f"✅ Student created with ID: {student_id}")
        
        # Test delete this student
        print(f"\n🗑️ Testing DELETE student {student_id}...")
        delete_response = session.delete(f"{BASE_URL}/api/students/{student_id}")
        print(f"Delete student status: {delete_response.status_code}")
        
        if delete_response.status_code == 200:
            print("✅ Student deleted successfully")
        else:
            print(f"❌ Delete failed: {delete_response.text}")
    else:
        print(f"❌ Create failed: {create_response.text}")
    
    # Test create batch
    print("\n📝 Testing CREATE batch...")
    batch_data = {
        "name": "Simple Test Batch",
        "class": "Class 10",
        "subject": "Science"
    }
    
    create_batch_response = session.post(f"{BASE_URL}/api/batches", json=batch_data)
    print(f"Create batch status: {create_batch_response.status_code}")
    
    if create_batch_response.status_code == 201:
        batch_info = create_batch_response.json()
        batch_id = batch_info['data']['batch']['id']
        print(f"✅ Batch created with ID: {batch_id}")
        
        # Test delete this batch
        print(f"\n🗑️ Testing DELETE batch {batch_id}...")
        delete_batch_response = session.delete(f"{BASE_URL}/api/batches/{batch_id}")
        print(f"Delete batch status: {delete_batch_response.status_code}")
        
        if delete_batch_response.status_code == 200:
            print("✅ Batch deleted successfully")
        elif delete_batch_response.status_code == 403:
            print("❌ Batch delete forbidden - permission issue!")
        else:
            print(f"❌ Batch delete failed: {delete_batch_response.text}")
    else:
        print(f"❌ Batch create failed: {create_batch_response.text}")

if __name__ == "__main__":
    print("🧪 SIMPLE CRUD TEST")
    print("=" * 30)
    
    # Wait a moment for server
    time.sleep(1)
    
    test_basic_operations()
    
    print("\n✨ Test completed!")