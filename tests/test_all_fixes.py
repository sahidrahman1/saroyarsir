#!/usr/bin/env python3
"""
Comprehensive test for all CRUD operations after fixes
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5001"

def wait_for_server():
    """Wait for server to be ready"""
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/login", timeout=5)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            print(f"⏳ Waiting for server... attempt {i+1}")
            time.sleep(2)
    return False

def login_as_teacher():
    """Login as teacher"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phoneNumber": "01812345678",
        "password": "teacher123"
    })
    return response

def test_student_operations():
    """Test student create, read, update, delete"""
    print("\n🧑‍🎓 TESTING STUDENT OPERATIONS")
    print("=" * 50)
    
    # Login
    login_response = login_as_teacher()
    if login_response.status_code != 200:
        print("❌ Login failed, skipping student tests")
        return False
    
    session = requests.Session()
    session.cookies.update(login_response.cookies)
    
    # Test CREATE student
    print("\n📝 Testing CREATE student...")
    student_data = {
        "firstName": "Test",
        "lastName": "Student Fix",
        "guardianName": "Test Parent Fix",
        "guardianPhone": "01999123456",  # Unique phone
        "school": "Test School",
        "isActive": True
    }
    
    create_response = session.post(f"{BASE_URL}/api/students", json=student_data)
    print(f"   Create Status: {create_response.status_code}")
    
    if create_response.status_code == 201:
        student_info = create_response.json()
        student_id = student_info['data']['id']
        print(f"   ✅ Student created with ID: {student_id}")
        
        # Check login credentials
        login_creds = student_info['data'].get('loginCredentials')
        if login_creds:
            print(f"   📱 Login: {login_creds['username']} / {login_creds['password']}")
        
        # Test READ students
        print("\n📖 Testing READ students...")
        read_response = session.get(f"{BASE_URL}/api/students")
        print(f"   Read Status: {read_response.status_code}")
        
        if read_response.status_code == 200:
            students_data = read_response.json()
            student_count = len(students_data.get('data', []))
            print(f"   ✅ Retrieved {student_count} students")
        
        # Test UPDATE student
        print("\n📝 Testing UPDATE student...")
        update_data = {
            "firstName": "Updated Test",
            "guardianName": "Updated Parent"
        }
        
        update_response = session.put(f"{BASE_URL}/api/students/{student_id}", json=update_data)
        print(f"   Update Status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            print("   ✅ Student updated successfully")
        
        # Test DELETE student
        print("\n🗑️ Testing DELETE student...")
        delete_response = session.delete(f"{BASE_URL}/api/students/{student_id}")
        print(f"   Delete Status: {delete_response.status_code}")
        
        if delete_response.status_code == 200:
            print("   ✅ Student deleted successfully")
            return True
        else:
            print(f"   ❌ Delete failed: {delete_response.text}")
    else:
        print(f"   ❌ Create failed: {create_response.text}")
    
    return False

def test_batch_operations():
    """Test batch create, read, update, delete"""
    print("\n📚 TESTING BATCH OPERATIONS")
    print("=" * 50)
    
    # Login
    login_response = login_as_teacher()
    if login_response.status_code != 200:
        print("❌ Login failed, skipping batch tests")
        return False
    
    session = requests.Session()
    session.cookies.update(login_response.cookies)
    
    # Test CREATE batch
    print("\n📝 Testing CREATE batch...")
    batch_data = {
        "name": "Test Batch Fix",
        "class": "Class 9",
        "subject": "Mathematics"
    }
    
    create_response = session.post(f"{BASE_URL}/api/batches", json=batch_data)
    print(f"   Create Status: {create_response.status_code}")
    
    if create_response.status_code == 201:
        batch_info = create_response.json()
        batch_id = batch_info['data']['batch']['id']
        print(f"   ✅ Batch created with ID: {batch_id}")
        
        # Test READ batches
        print("\n📖 Testing READ batches...")
        read_response = session.get(f"{BASE_URL}/api/batches")
        print(f"   Read Status: {read_response.status_code}")
        
        if read_response.status_code == 200:
            batches_data = read_response.json()
            batch_count = batches_data.get('data', {}).get('total', 0)
            print(f"   ✅ Retrieved {batch_count} batches")
        
        # Test UPDATE batch
        print("\n📝 Testing UPDATE batch...")
        update_data = {
            "name": "Updated Test Batch Fix",
            "subject": "Physics"
        }
        
        update_response = session.put(f"{BASE_URL}/api/batches/{batch_id}", json=update_data)
        print(f"   Update Status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            print("   ✅ Batch updated successfully")
        
        # Test DELETE batch
        print("\n🗑️ Testing DELETE batch...")
        delete_response = session.delete(f"{BASE_URL}/api/batches/{batch_id}")
        print(f"   Delete Status: {delete_response.status_code}")
        
        if delete_response.status_code == 200:
            print("   ✅ Batch deleted successfully")
            return True
        elif delete_response.status_code == 403:
            print("   ⚠️ Delete requires higher permissions (check role requirements)")
        else:
            print(f"   ❌ Delete failed: {delete_response.text}")
    else:
        print(f"   ❌ Create failed: {create_response.text}")
    
    return False

def main():
    print("🧪 COMPREHENSIVE CRUD FIXES TEST")
    print("=" * 60)
    
    if not wait_for_server():
        print("❌ Server not responding, cannot run tests")
        return
    
    student_success = test_student_operations()
    batch_success = test_batch_operations()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"   Students: {'✅ PASS' if student_success else '❌ FAIL'}")
    print(f"   Batches: {'✅ PASS' if batch_success else '❌ FAIL'}")
    
    if student_success and batch_success:
        print("\n🎉 ALL FIXES WORKING CORRECTLY!")
    else:
        print("\n⚠️ Some issues remain - check server logs")

if __name__ == "__main__":
    main()