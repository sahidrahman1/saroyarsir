#!/usr/bin/env python3
"""
Test script to create batches and verify they appear in the dropdown
"""
import requests
import json

def main():
    try:
        # Login as teacher
        print('🔐 Logging in as teacher...')
        login_response = requests.post('http://127.0.0.1:5001/api/auth/login', json={
            'phoneNumber': '01812345678',
            'password': 'teacher123'
        })
        
        if login_response.status_code != 200:
            print(f'❌ Login failed: {login_response.status_code}')
            print(f'Response: {login_response.text}')
            return
        
        cookies = login_response.cookies
        print('✅ Login successful')
        
        # Create test batches
        test_batches = [
            {
                'name': 'HSC Mathematics Batch A',
                'class': 'HSC 1st Year',
                'subject': 'Higher Mathematics'
            },
            {
                'name': 'Class 10 Physics Batch B', 
                'class': 'Class 10',
                'subject': 'Physics'
            },
            {
                'name': 'HSC Chemistry Batch C',
                'class': 'HSC 2nd Year', 
                'subject': 'Chemistry'
            }
        ]
        
        print('\n📚 Creating test batches...')
        for batch_data in test_batches:
            response = requests.post('http://127.0.0.1:5001/api/batches', 
                                   json=batch_data, 
                                   cookies=cookies)
            
            if response.status_code == 201:
                result = response.json()
                print(f'✅ Created: {batch_data["name"]}')
            else:
                print(f'❌ Failed to create {batch_data["name"]}: {response.status_code}')
                print(f'   Error: {response.text[:200]}')
        
        # Test active batches API
        print('\n🔍 Testing active batches API...')
        batches_response = requests.get('http://127.0.0.1:5001/api/batches/active', 
                                      cookies=cookies)
        
        if batches_response.status_code == 200:
            data = batches_response.json()
            print(f'✅ API Response Status: {batches_response.status_code}')
            print(f'✅ Response Success: {data.get("success")}')
            print(f'✅ Response Message: {data.get("message")}')
            
            if data.get('success') and data.get('data'):
                batches = data['data']
                print(f'📊 Found {len(batches)} active batches:')
                
                for i, batch in enumerate(batches, 1):
                    print(f'   {i}. {batch.get("name")} (ID: {batch.get("id")})')
                    print(f'      Description: {batch.get("description")}')
                    print(f'      Students: {batch.get("student_count", 0)}')
                    print()
            else:
                print(f'❌ Unexpected response structure: {data}')
        else:
            print(f'❌ Failed to get active batches: {batches_response.status_code}')
            print(f'   Error: {batches_response.text[:200]}')
        
        print('\n🎯 Testing batch dropdown compatibility...')
        print('Frontend should now be able to load batches in the dropdown!')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    main()