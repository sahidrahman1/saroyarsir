#!/usr/bin/env python3
"""
Test CRUD operations for students and batches
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def login_as_teacher():
    """Login as teacher to get session"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phoneNumber": "01812345678",
        "password": "teacher123"
    })
    return response

def test_student_crud():
    """Test student create, read, update, delete operations"""
    print("🧑‍🎓 TESTING STUDENT CRUD OPERATIONS")
    print("=" * 50)
    
    # Login first
    login_response = login_as_teacher()
    if login_response.status_code != 200:
        print("❌ Login failed, can't test CRUD operations")
        return
    
    session = requests.Session()
    session.cookies.update(login_response.cookies)
    
    # Test CREATE student
    print("\n📝 Testing CREATE student...")
    student_data = {
        "firstName": "Test",
        "lastName": "Student",
        "guardianName": "Test Parent",
        "guardianPhone": "01999888777",
        "school": "Test School",
        "isActive": True
    }
    
    create_response = session.post(f"{BASE_URL}/api/students", json=student_data)
    print(f"   Status: {create_response.status_code}")
    
    if create_response.status_code == 201:
        created_student = create_response.json()
        student_id = created_student['data']['id']
        print(f"   ✅ Student created with ID: {student_id}")
        print(f"   Login credentials: {created_student['data'].get('loginCredentials', 'Not provided')}")
        
        # Test UPDATE student
        print("\n📝 Testing UPDATE student...")
        update_data = {
            "firstName": "Updated Test",
            "guardianName": "Updated Parent"
        }
        
        update_response = session.put(f"{BASE_URL}/api/students/{student_id}", json=update_data)
        print(f"   Status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            print("   ✅ Student updated successfully")
        else:
            print(f"   ❌ Update failed: {update_response.text}")
        
        # Test DELETE student
        print("\n📝 Testing DELETE student...")
        delete_response = session.delete(f"{BASE_URL}/api/students/{student_id}")
        print(f"   Status: {delete_response.status_code}")
        
        if delete_response.status_code == 200:
            print("   ✅ Student deleted successfully")
        else:
            print(f"   ❌ Delete failed: {delete_response.text}")
            
    else:
        print(f"   ❌ Create failed: {create_response.text}")

def test_batch_crud():
    """Test batch create, read, update, delete operations"""
    print("\n📚 TESTING BATCH CRUD OPERATIONS")
    print("=" * 50)
    
    # Login first
    login_response = login_as_teacher()
    if login_response.status_code != 200:
        print("❌ Login failed, can't test CRUD operations")
        return
    
    session = requests.Session()
    session.cookies.update(login_response.cookies)
    
    # Test CREATE batch
    print("\n📝 Testing CREATE batch...")
    batch_data = {
        "name": "Test Batch 2025",
        "class": "Class 9",
        "subject": "Mathematics"
    }
    
    create_response = session.post(f"{BASE_URL}/api/batches", json=batch_data)
    print(f"   Status: {create_response.status_code}")
    
    if create_response.status_code == 201:
        created_batch = create_response.json()
        batch_id = created_batch['data']['batch']['id']
        print(f"   ✅ Batch created with ID: {batch_id}")
        
        # Test UPDATE batch
        print("\n📝 Testing UPDATE batch...")
        update_data = {
            "name": "Updated Test Batch 2025",
            "subject": "Physics"
        }
        
        update_response = session.put(f"{BASE_URL}/api/batches/{batch_id}", json=update_data)
        print(f"   Status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            print("   ✅ Batch updated successfully")
        else:
            print(f"   ❌ Update failed: {update_response.text}")
        
        # Test DELETE batch (note: requires SUPER_USER, so this might fail)
        print("\n📝 Testing DELETE batch...")
        delete_response = session.delete(f"{BASE_URL}/api/batches/{batch_id}")
        print(f"   Status: {delete_response.status_code}")
        
        if delete_response.status_code == 200:
            print("   ✅ Batch deleted successfully")
        elif delete_response.status_code == 403:
            print("   ⚠️ Delete requires SUPER_USER role (expected for teacher account)")
        else:
            print(f"   ❌ Delete failed: {delete_response.text}")
            
    else:
        print(f"   ❌ Create failed: {create_response.text}")

def test_read_operations():
    """Test read operations for students and batches"""
    print("\n📖 TESTING READ OPERATIONS")
    print("=" * 50)
    
    # Login first
    login_response = login_as_teacher()
    if login_response.status_code != 200:
        print("❌ Login failed, can't test read operations")
        return
    
    session = requests.Session()
    session.cookies.update(login_response.cookies)
    
    # Test GET students
    print("\n📝 Testing GET students...")
    students_response = session.get(f"{BASE_URL}/api/students")
    print(f"   Status: {students_response.status_code}")
    
    if students_response.status_code == 200:
        students_data = students_response.json()
        student_count = len(students_data.get('data', []))
        print(f"   ✅ Retrieved {student_count} students")
    else:
        print(f"   ❌ Failed to get students: {students_response.text}")
    
    # Test GET batches
    print("\n📝 Testing GET batches...")
    batches_response = session.get(f"{BASE_URL}/api/batches")
    print(f"   Status: {batches_response.status_code}")
    
    if batches_response.status_code == 200:
        batches_data = batches_response.json()
        batch_count = batches_data.get('data', {}).get('total', 0)
        print(f"   ✅ Retrieved {batch_count} batches")
    else:
        print(f"   ❌ Failed to get batches: {batches_response.text}")

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE CRUD TESTING")
    print("=" * 60)
    
    try:
        test_read_operations()
        test_student_crud()
        test_batch_crud()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("Check the output above for any issues.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")