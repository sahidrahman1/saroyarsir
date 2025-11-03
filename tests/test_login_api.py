"""
Test login API directly
"""
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app import create_app
import json

app = create_app()

# Test the login API endpoint directly
with app.test_client() as client:
    try:
        # Test login request
        response = client.post('/api/auth/login', 
            json={'phoneNumber': '01812345678', 'password': 'teacher123'},
            content_type='application/json'
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.get_data(as_text=True)}")
        
        if response.status_code == 500:
            print("❌ Internal Server Error - checking app logs...")
        
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        import traceback
        traceback.print_exc()