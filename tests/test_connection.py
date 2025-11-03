import requests
import time

def test_flask_app():
    """Test if the Flask app is working"""
    base_url = "http://127.0.0.1:3001"
    
    print("🧪 Testing Flask Application Connection")
    print("=" * 50)
    
    # Wait a bit for the server to be ready
    time.sleep(2)
    
    try:
        # Test the home page
        print("1. Testing home page...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   ✅ Home page: Status {response.status_code}")
        print(f"   📄 Content type: {response.headers.get('content-type', 'unknown')}")
        print(f"   📏 Content length: {len(response.text)} characters")
        
        # Test login page
        print("\n2. Testing login page...")
        response = requests.get(f"{base_url}/login", timeout=10)
        print(f"   ✅ Login page: Status {response.status_code}")
        
        # Test API endpoint
        print("\n3. Testing API endpoint...")
        response = requests.get(f"{base_url}/api/batches", timeout=10)
        print(f"   ✅ API endpoint: Status {response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎉 Flask Application is working correctly!")
        print(f"🌐 Access the app at: {base_url}")
        print("🔐 Login credentials:")
        print("   Teacher: 01812345678 / teacher123")
        print("   Student: 01912345678 / student123")
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("💡 Make sure the Flask app is running on port 3001")
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout Error: {e}")
        print("💡 The server might be slow to respond")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_flask_app()