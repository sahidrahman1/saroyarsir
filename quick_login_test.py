"""
Quick test for student login with new random passwords
"""
import requests
import sys

def test_login(phone, password, name):
    """Test a single login"""
    try:
        print(f"Testing login for: {name}")
        print(f"Phone: {phone}")
        print(f"Password: {password}")
        
        response = requests.post(
            'http://127.0.0.1:5001/api/auth/login',
            json={'phone': phone, 'password': password},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            user = data.get('user', {})
            print(f"✅ SUCCESS! Login successful")
            print(f"   Name: {user.get('full_name', 'N/A')}")
            print(f"   Role: {user.get('role', 'N/A')}")
            print(f"   Token: {data.get('token', 'N/A')[:30]}...")
            return True
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Quick Student Login Test")
    print("=" * 40)
    
    # Test one student from our updated passwords
    success = test_login("01901234567", "g9m7r2t0", "রহিম আহমেদ")
    
    if success:
        print("\n🎉 Student login system is working!")
        print("Students can now login with:")
        print("• Their own phone number")
        print("• Their unique random password")
    else:
        print("\n⚠️ Student login needs attention")