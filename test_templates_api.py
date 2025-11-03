import requests

# Test the SMS templates API
try:
    # First login to get session
    login_response = requests.post('http://localhost:5001/api/auth/login', json={
        'phoneNumber': '01812345678',
        'password': 'teacher123'
    })
    
    if login_response.status_code == 200:
        print("✅ Login successful")
        
        # Get cookies for session
        cookies = login_response.cookies
        
        # Test templates endpoint
        templates_response = requests.get('http://localhost:5001/api/sms/templates', 
                                        cookies=cookies)
        
        print(f"Templates API Status: {templates_response.status_code}")
        print(f"Templates Response: {templates_response.text}")
        
    else:
        print(f"❌ Login failed: {login_response.text}")
        
except Exception as e:
    print(f"Error: {e}")