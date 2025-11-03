#!/usr/bin/env python3
"""
Quick server connectivity test
"""
import requests
import time

def test_server():
    base_url = "http://127.0.0.1:5001"
    
    print("🔍 Testing server connectivity...")
    
    # Wait for server to start
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/login", timeout=5)
            if response.status_code == 200:
                print(f"✅ Server is running! Status: {response.status_code}")
                return True
        except requests.exceptions.ConnectionError:
            print(f"⏳ Waiting for server... attempt {i+1}/10")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("❌ Server not responding after 20 seconds")
    return False

def quick_api_test():
    """Test basic API endpoints"""
    base_url = "http://127.0.0.1:5001"
    
    if not test_server():
        return
    
    print("\n🧪 Testing API endpoints...")
    
    # Test login
    try:
        login_response = requests.post(f"{base_url}/api/auth/login", json={
            "phoneNumber": "01812345678",
            "password": "teacher123"
        })
        print(f"📱 Login test: {login_response.status_code}")
        
        if login_response.status_code == 200:
            # Test students API
            session = requests.Session()
            session.cookies.update(login_response.cookies)
            
            students_response = session.get(f"{base_url}/api/students")
            print(f"👥 Students API: {students_response.status_code}")
            
            batches_response = session.get(f"{base_url}/api/batches")
            print(f"📚 Batches API: {batches_response.status_code}")
            
            if students_response.status_code == 200 and batches_response.status_code == 200:
                print("✅ All basic APIs working!")
            else:
                print("⚠️ Some APIs have issues")
        else:
            print("❌ Login failed, can't test other APIs")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    quick_api_test()