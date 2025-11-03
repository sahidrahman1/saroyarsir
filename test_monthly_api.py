#!/usr/bin/env python3
"""
Test monthly attendance API
"""
import os
import requests

# Set MySQL environment variables  
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import User, Batch

def test_monthly_api():
    app = create_app()
    with app.app_context():
        try:
            # Find HSC batch
            hsc_batch = Batch.query.filter_by(name='HSC Mathematics Batch A').first()
            if not hsc_batch:
                print('❌ HSC Mathematics Batch A not found')
                return
                
            print(f'📚 Found batch: {hsc_batch.name} (ID: {hsc_batch.id})')
            
            # Test the monthly attendance route directly
            from routes.attendance import get_monthly_attendance
            
            # Simulate request parameters
            class MockRequest:
                def __init__(self):
                    self.args = {
                        'batch_id': hsc_batch.id,
                        'month': 10,  # October
                        'year': 2025
                    }
                
                def get(self, key, default=None, type=None):
                    value = self.args.get(key, default)
                    if type and value is not None:
                        return type(value)
                    return value
            
            # Mock the request
            import routes.attendance as attendance_module
            original_request = attendance_module.request
            attendance_module.request = MockRequest()
            
            # Mock get_current_user to return a teacher
            teacher = User.query.filter_by(role='teacher').first()
            if not teacher:
                print('❌ No teacher found')
                return
                
            def mock_get_current_user():
                return teacher
                
            attendance_module.get_current_user = mock_get_current_user
            
            # Call the function
            result = get_monthly_attendance()
            
            print('🔍 API Result:')
            print(f'   Status: {result[1] if isinstance(result, tuple) else "200"}')
            
            if isinstance(result, tuple):
                response_data = result[0]
            else:
                response_data = result
                
            print(f'   Response: {response_data.get_data(as_text=True) if hasattr(response_data, "get_data") else response_data}')
            
            # Restore original request
            attendance_module.request = original_request
            
        except Exception as e:
            print(f'❌ Error: {e}')
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_monthly_api()