#!/usr/bin/env python3
"""
Simple test for monthly attendance API
"""
import requests

def test_monthly_api():
    try:
        # Login first
        login_data = {
            'phoneNumber': '01812345678',
            'password': 'password123'
        }
        
        session = requests.Session()
        
        # Login
        login_response = session.post('http://127.0.0.1:5001/api/auth/login', json=login_data)
        print(f'Login Status: {login_response.status_code}')
        
        if login_response.status_code == 200:
            # Try monthly API
            url = 'http://127.0.0.1:5001/api/attendance/monthly'
            params = {
                'batch_id': 11,
                'month': 10,
                'year': 2025
            }
            
            api_response = session.get(url, params=params)
            print(f'API Status: {api_response.status_code}')
            print(f'API Response: {api_response.text[:1000]}...')
            
            if api_response.status_code == 200:
                data = api_response.json()
                print(f'Response data keys: {list(data.keys())}')
                
                if data.get('success') and data.get('data'):
                    attendance_data = data['data']
                    students = attendance_data.get('students', [])
                    days = attendance_data.get('days', [])
                    print(f'Students: {len(students)}, Days: {len(days)}')
                    
                    if students:
                        print(f'First student: {students[0].get("name", "Unknown")}')
                        print(f'Student keys: {list(students[0].keys())}')
                else:
                    print('API returned success=false or no data')
            else:
                print(f'API Error: {api_response.text}')
        else:
            print(f'Login failed: {login_response.text}')
            
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    test_monthly_api()