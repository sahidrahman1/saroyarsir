#!/usr/bin/env python3
"""
Test unique password generation for students
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5001"

def test_unique_password_creation():
    """Test that new students get unique passwords"""
    print("🔐 TESTING UNIQUE PASSWORD GENERATION")
    print("=" * 50)
    
    # Login as teacher first
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phoneNumber": "01812345678",
        "password": "teacher123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        print(f"Response: {login_response.text}")
        return False
    
    print("✅ Teacher login successful")
    
    session = requests.Session()
    session.cookies.update(login_response.cookies)
    
    # Test creating multiple students with unique passwords
    test_students = [
        {
            "firstName": "Ahmed",
            "lastName": "Rahman", 
            "guardianName": "Rahman Saheb",
            "guardianPhone": "01755123456",
            "school": "Test School 1"
        },
        {
            "firstName": "Fatima",
            "lastName": "Khatun",
            "guardianName": "Khatun Begum", 
            "guardianPhone": "01855234567",
            "school": "Test School 2"
        },
        {
            "firstName": "Mohammad",
            "lastName": "Ali",
            "guardianName": "Ali Miah",
            "guardianPhone": "01955345678", 
            "school": "Test School 3"
        }
    ]
    
    created_students = []
    
    for i, student_data in enumerate(test_students, 1):
        print(f"\n📝 Creating Student {i}: {student_data['firstName']} {student_data['lastName']}")
        
        create_response = session.post(f"{BASE_URL}/api/students", json=student_data)
        
        if create_response.status_code == 201:
            response_data = create_response.json()
            student_info = response_data['data']
            credentials = student_info.get('loginCredentials', {})
            
            print(f"   ✅ Student created successfully!")
            print(f"   📱 Login Username: {credentials.get('username', 'N/A')}")
            print(f"   🔐 Generated Password: {credentials.get('password', 'N/A')}")
            print(f"   📋 Note: {credentials.get('note', 'N/A')}")
            
            created_students.append({
                'id': student_info['id'],
                'name': f"{student_data['firstName']} {student_data['lastName']}",
                'username': credentials.get('username'),
                'password': credentials.get('password')
            })
        else:
            print(f"   ❌ Student creation failed: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
    
    # Test that all passwords are unique
    print(f"\n🔍 VERIFYING PASSWORD UNIQUENESS")
    print("=" * 50)
    
    passwords = [student['password'] for student in created_students if student['password']]
    unique_passwords = set(passwords)
    
    print(f"Total students created: {len(created_students)}")
    print(f"Total passwords: {len(passwords)}")
    print(f"Unique passwords: {len(unique_passwords)}")
    
    if len(passwords) == len(unique_passwords):
        print("✅ All passwords are unique!")
    else:
        print("❌ Some passwords are duplicated!")
        
    # Show all generated passwords
    print(f"\n📋 GENERATED PASSWORDS:")
    for student in created_students:
        if student['password']:
            print(f"   {student['name']}: {student['username']} / {student['password']}")
    
    # Test login with new unique passwords
    print(f"\n🔐 TESTING LOGIN WITH UNIQUE PASSWORDS")
    print("=" * 50)
    
    for student in created_students:
        if student['username'] and student['password']:
            print(f"\n🧪 Testing login for {student['name']}")
            
            # Logout current session
            session.post(f"{BASE_URL}/api/auth/logout")
            
            # Try login with unique password
            test_login = requests.post(f"{BASE_URL}/api/auth/login", json={
                "phoneNumber": student['username'],
                "password": student['password']
            })
            
            if test_login.status_code == 200:
                print(f"   ✅ Login successful with unique password!")
            else:
                print(f"   ❌ Login failed: {test_login.status_code}")
                print(f"   Response: {test_login.text}")
    
    # Cleanup - delete test students
    print(f"\n🧹 CLEANING UP TEST STUDENTS")
    print("=" * 50)
    
    # Re-login as teacher for cleanup
    teacher_login = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phoneNumber": "01812345678", 
        "password": "teacher123"
    })
    
    if teacher_login.status_code == 200:
        cleanup_session = requests.Session()
        cleanup_session.cookies.update(teacher_login.cookies)
        
        for student in created_students:
            delete_response = cleanup_session.delete(f"{BASE_URL}/api/students/{student['id']}")
            if delete_response.status_code == 200:
                print(f"   ✅ Deleted {student['name']}")
            else:
                print(f"   ⚠️ Could not delete {student['name']}: {delete_response.status_code}")
    
    return True

if __name__ == "__main__":
    print("🧪 UNIQUE PASSWORD SYSTEM TEST")
    print("=" * 60)
    
    # Wait for server
    print("⏳ Waiting for server...")
    time.sleep(2)
    
    try:
        test_unique_password_creation()
        print("\n🎉 UNIQUE PASSWORD TEST COMPLETED!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")