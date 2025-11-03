import requests
import json

# Test all dashboard features
base_url = "http://127.0.0.1:3001"
session = requests.Session()

print("🧪 Testing SmartGardenHub Dashboard Features")
print("=" * 50)

# 1. Login first
print("1. Testing Login...")
login_response = session.post(f"{base_url}/api/auth/login", 
    json={'phoneNumber': '01812345678', 'password': 'teacher123'})

if login_response.status_code == 200:
    print("✅ Login successful")
    login_data = login_response.json()
    user_role = login_data.get('data', {}).get('user', {}).get('role')
    print(f"   User role: {user_role}")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    exit(1)

# 2. Test Dashboard Stats
print("\n2. Testing Dashboard Stats...")
stats_response = session.get(f"{base_url}/api/dashboard/stats")
if stats_response.status_code == 200:
    print("✅ Dashboard stats working")
    stats = stats_response.json().get('data', {})
    print(f"   Total students: {stats.get('total_students', 0)}")
    print(f"   Total teachers: {stats.get('total_teachers', 0)}")
    print(f"   Total batches: {stats.get('total_batches', 0)}")
else:
    print(f"❌ Dashboard stats failed: {stats_response.status_code}")

# 3. Test Students API
print("\n3. Testing Students API...")
students_response = session.get(f"{base_url}/api/users?role=student")
if students_response.status_code == 200:
    print("✅ Students API working")
    students_data = students_response.json()
    total = students_data.get('data', {}).get('total', 0)
    print(f"   Found {total} students")
else:
    print(f"❌ Students API failed: {students_response.status_code}")

# 4. Test Batches API
print("\n4. Testing Batches API...")
batches_response = session.get(f"{base_url}/api/batches")
if batches_response.status_code == 200:
    print("✅ Batches API working")
    batches_data = batches_response.json()
    total = batches_data.get('data', {}).get('total', 0)
    print(f"   Found {total} batches")
else:
    print(f"❌ Batches API failed: {batches_response.status_code}")

# 5. Test Settings API
print("\n5. Testing Settings API...")
settings_response = session.get(f"{base_url}/api/settings")
if settings_response.status_code == 200:
    print("✅ Settings API working")
    settings_data = settings_response.json()
    app_name = settings_data.get('data', {}).get('app_name', 'Unknown')
    print(f"   App name: {app_name}")
else:
    print(f"❌ Settings API failed: {settings_response.status_code}")

# 6. Test SMS API
print("\n6. Testing SMS API...")
sms_response = session.get(f"{base_url}/api/sms/templates")
if sms_response.status_code == 200:
    print("✅ SMS API working")
    sms_data = sms_response.json()
    total = sms_data.get('data', {}).get('total', 0)
    print(f"   Found {total} SMS templates")
else:
    print(f"❌ SMS API failed: {sms_response.status_code}")

# 7. Test Attendance API
print("\n7. Testing Attendance API...")
attendance_response = session.get(f"{base_url}/api/attendance")
if attendance_response.status_code == 200:
    print("✅ Attendance API working")
else:
    print(f"❌ Attendance API failed: {attendance_response.status_code}")

# 8. Test Fees API
print("\n8. Testing Fees API...")
fees_response = session.get(f"{base_url}/api/fees")
if fees_response.status_code == 200:
    print("✅ Fees API working")
else:
    print(f"❌ Fees API failed: {fees_response.status_code}")

# 9. Test Questions API
print("\n9. Testing Questions API...")
questions_response = session.get(f"{base_url}/api/questions")
if questions_response.status_code == 200:
    print("✅ Questions API working")
else:
    print(f"❌ Questions API failed: {questions_response.status_code}")

# 10. Test Exams API
print("\n10. Testing Exams API...")
exams_response = session.get(f"{base_url}/api/exams")
if exams_response.status_code == 200:
    print("✅ Exams API working")
else:
    print(f"❌ Exams API failed: {exams_response.status_code}")

print("\n" + "=" * 50)
print("🎉 Dashboard Feature Testing Complete!")
print("📍 Application running at: http://127.0.0.1:3333")
print("🔐 Login with teacher: 01812345678 / teacher123")
print("🔐 Login with student: 01912345678 / student123")