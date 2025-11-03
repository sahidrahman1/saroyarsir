import requests

# Test login and dashboard access
session = requests.Session()

# Login
login_response = session.post('http://localhost:3001/api/auth/login', 
    json={'phoneNumber': '01812345678', 'password': 'teacher123'})

print(f"Login status: {login_response.status_code}")
print(f"Login success: {login_response.json().get('success')}")

# Test auth/me endpoint
me_response = session.get('http://localhost:3001/api/auth/me')
print(f"Auth me status: {me_response.status_code}")
print(f"Auth me success: {me_response.json().get('success')}")

# Test teacher dashboard template route
dashboard_response = session.get('http://localhost:3001/teacher')
print(f"Teacher dashboard status: {dashboard_response.status_code}")
print(f"Dashboard response contains 'dashboard_teacher.html': {'dashboard_teacher.html' in dashboard_response.text}")
print(f"Dashboard response contains 'Teacher': {'Teacher' in dashboard_response.text}")

if dashboard_response.status_code == 200:
    print("SUCCESS: Teacher dashboard is now accessible after login!")
else:
    print(f"Dashboard response preview: {dashboard_response.text[:200]}...")