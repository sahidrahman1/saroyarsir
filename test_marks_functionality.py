"""
Test marks saving functionality
"""
import os
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
import requests

app = create_app()

with app.app_context():
    # Start the app in test mode
    print("🔬 Testing marks saving functionality...")
    
    # Test 1: Check if server is responding
    try:
        response = requests.get('http://127.0.0.1:5001/api/debug/check-data')
        print(f"✅ Server responding: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Found {data['data']['total_students']} students and {len(data['data']['batches'])} batches")
        else:
            print(f"❌ Server error: {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 2: Test login
    try:
        session = requests.Session()
        login_response = session.post('http://127.0.0.1:5001/api/auth/login', 
            json={'phoneNumber': '01812345678', 'password': 'teacher123'})
        
        print(f"🔐 Login status: {login_response.status_code}")
        if login_response.status_code == 200:
            print("✅ Login successful")
            
            # Test 3: Check if we can access protected routes
            auth_check = session.get('http://127.0.0.1:5001/api/auth/me')
            print(f"🛡️  Auth check: {auth_check.status_code}")
            
            if auth_check.status_code == 200:
                user_data = auth_check.json()
                print(f"👤 Logged in as: {user_data['data']['user']['full_name']}")
                
                # Test 4: Try to get batches
                batches_response = session.get('http://127.0.0.1:5001/api/batches')
                print(f"📚 Batches API: {batches_response.status_code}")
                
                if batches_response.status_code == 200:
                    batches_data = batches_response.json()
                    batches = batches_data.get('data', [])
                    if batches:
                        batch = batches[0]
                        print(f"📝 Testing with batch: {batch['name']} (ID: {batch['id']})")
                        
                        # Test 5: Try to get students from batch
                        students_response = session.get(f"http://127.0.0.1:5001/api/batches/{batch['id']}/students")
                        print(f"👥 Students API: {students_response.status_code}")
                        
                        if students_response.status_code == 200:
                            students_data = students_response.json()
                            students = students_data.get('data', {}).get('students', [])
                            print(f"✅ Found {len(students)} students in batch")
                            
                            if students:
                                print("🎯 Students list:")
                                for student in students[:3]:  # Show first 3
                                    print(f"   - {student['full_name']} (ID: {student['id']})")
                            else:
                                print("❌ No students found in batch")
                        else:
                            print(f"❌ Students API error: {students_response.text}")
                    else:
                        print("❌ No batches found")
                else:
                    print(f"❌ Batches API error: {batches_response.text}")
            else:
                print(f"❌ Auth check failed: {auth_check.text}")
        else:
            print(f"❌ Login failed: {login_response.text}")
    except Exception as e:
        print(f"❌ Login test error: {e}")