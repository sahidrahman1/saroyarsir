from app import create_app
from models import User

app = create_app()

# Test login and session creation
with app.test_client() as client:
    with app.app_context():
        # Test login API
        response = client.post('/api/auth/login', 
            json={'phoneNumber': '01812345678', 'password': 'teacher123'},
            follow_redirects=True)
        
        print(f"Login response status: {response.status_code}")
        print(f"Login response data: {response.get_json()}")
        
        # Check session after login
        with client.session_transaction() as sess:
            print(f"Session data: {dict(sess)}")
            print(f"Session has 'user': {'user' in sess}")
            print(f"Session has 'user_id': {'user_id' in sess}")
            if 'user' in sess:
                print(f"Session user data: {sess['user']}")
                print(f"Session user type: {type(sess['user'])}")
        
        # Test auth/me endpoint
        me_response = client.get('/api/auth/me')
        print(f"Auth me response status: {me_response.status_code}")
        print(f"Auth me response data: {me_response.get_json()}")