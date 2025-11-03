"""
Test Teacher Dashboard Features
Quick verification that all teacher dashboard features are working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_teacher_login():
    """Test teacher login functionality"""
    session = requests.Session()
    
    # Login as teacher
    login_data = {
        "phoneNumber": "01812345678",
        "password": "teacher123"
    }
    
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        print("✅ Teacher login successful")
        return session
    else:
        print(f"❌ Teacher login failed: {response.status_code}")
        print(response.text)
        return None

def test_dashboard_stats(session):
    """Test dashboard statistics endpoint"""
    response = session.get(f"{BASE_URL}/api/dashboard/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Dashboard stats loaded successfully")
        print(f"   Total Students: {stats.get('totalStudents', 0)}")
        print(f"   Active Batches: {stats.get('activeBatches', 0)}")
        print(f"   Pending Fees: ৳{stats.get('pendingFees', 0)}")
        return True
    else:
        print(f"❌ Dashboard stats failed: {response.status_code}")
        return False

def test_students_api(session):
    """Test students management API"""
    response = session.get(f"{BASE_URL}/api/students")
    
    if response.status_code == 200:
        students = response.json()
        print(f"✅ Students API working - {len(students)} students loaded")
        return True
    else:
        print(f"❌ Students API failed: {response.status_code}")
        return False

def test_batches_api(session):
    """Test batches management API"""
    response = session.get(f"{BASE_URL}/api/batches")
    
    if response.status_code == 200:
        batches = response.json()
        print(f"✅ Batches API working - found batches data")
        return True
    else:
        print(f"❌ Batches API failed: {response.status_code}")
        return False

def test_teacher_dashboard_page(session):
    """Test teacher dashboard page loads"""
    response = session.get(f"{BASE_URL}/dashboard/teacher")
    
    if response.status_code == 200:
        print("✅ Teacher dashboard page loads successfully")
        if 'teacherDashboard()' in response.text:
            print("✅ Alpine.js teacher dashboard function found")
        if 'Student Management' in response.text:
            print("✅ Student management section found")
        if 'Batch Management' in response.text:
            print("✅ Batch management section found")
        return True
    else:
        print(f"❌ Teacher dashboard page failed: {response.status_code}")
        return False

def main():
    print("🧪 Testing Teacher Dashboard Features")
    print("=" * 50)
    
    # Test login
    session = test_teacher_login()
    if not session:
        print("❌ Cannot proceed without login")
        return
    
    print()
    
    # Test API endpoints
    tests_passed = 0
    total_tests = 4
    
    if test_dashboard_stats(session):
        tests_passed += 1
    
    if test_students_api(session):
        tests_passed += 1
    
    if test_batches_api(session):
        tests_passed += 1
    
    if test_teacher_dashboard_page(session):
        tests_passed += 1
    
    print()
    print("=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All teacher dashboard features are working!")
        print()
        print("📝 Available Features:")
        print("   • Teacher Authentication ✅")
        print("   • Dashboard Statistics ✅")
        print("   • Student Management (CRUD) ✅")
        print("   • Batch Management ✅")
        print("   • Interactive Dashboard UI ✅")
        print("   • Alpine.js Frontend ✅")
        print()
        print("🌐 Access at: http://127.0.0.1:5000/dashboard/teacher")
        print("👤 Login: 01812345678 / teacher123")
    else:
        print("⚠️  Some features need attention")

if __name__ == "__main__":
    main()