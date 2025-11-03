#!/usr/bin/env python3
import requests

def test_batch_endpoints():
    # Login as teacher
    login_response = requests.post('http://127.0.0.1:5001/api/auth/login', json={
        'phoneNumber': '01812345678', 
        'password': 'teacher123'
    })
    
    if login_response.status_code == 200:
        cookies = login_response.cookies
        
        print("🔍 Testing batch endpoints...")
        
        # Test regular batches endpoint
        batches_response = requests.get('http://127.0.0.1:5001/api/batches', cookies=cookies)
        if batches_response.status_code == 200:
            data = batches_response.json()
            total_batches = len(data.get('data', []))
            print(f"📊 Regular /api/batches: {total_batches} total batches")
        
        # Test active batches endpoint  
        active_response = requests.get('http://127.0.0.1:5001/api/batches/active', cookies=cookies)
        if active_response.status_code == 200:
            data = active_response.json()
            active_batches = data.get('data', {}).get('batches', [])
            print(f"📊 Active /api/batches/active: {len(active_batches)} active batches")
            
            print("\nActive batch details:")
            for i, batch in enumerate(active_batches, 1):
                print(f"  {i}. {batch.get('name')} (ID: {batch.get('id')})")
                print(f"     Description: {batch.get('description')}")
                print(f"     Is Active: {batch.get('is_active', 'unknown')}")
                print()
        
        # Let's also create some more batches to test
        print("📚 Creating additional test batches...")
        additional_batches = [
            {'name': 'Class 9 Biology Batch D', 'class': 'Class 9', 'subject': 'Biology'},
            {'name': 'HSC English Batch E', 'class': 'HSC 1st Year', 'subject': 'English'},
            {'name': 'Class 8 General Science Batch F', 'class': 'Class 8', 'subject': 'General Science'},
            {'name': 'HSC ICT Batch G', 'class': 'HSC 2nd Year', 'subject': 'ICT'},
            {'name': 'Class 7 Mathematics Batch H', 'class': 'Class 7', 'subject': 'Mathematics'},
        ]
        
        created_count = 0
        for batch_data in additional_batches:
            response = requests.post('http://127.0.0.1:5001/api/batches', 
                                   json=batch_data, cookies=cookies)
            if response.status_code == 201:
                created_count += 1
                print(f"✅ Created: {batch_data['name']}")
            else:
                print(f"❌ Failed to create {batch_data['name']}: {response.status_code}")
        
        print(f"\n🎯 Created {created_count} additional batches")
        
        # Test active batches again
        print("\n🔍 Testing active batches again after creation...")
        active_response = requests.get('http://127.0.0.1:5001/api/batches/active', cookies=cookies)
        if active_response.status_code == 200:
            data = active_response.json()
            active_batches = data.get('data', {}).get('batches', [])
            print(f"📊 Now showing {len(active_batches)} active batches")
            
    else:
        print(f"❌ Login failed: {login_response.status_code}")

if __name__ == '__main__':
    test_batch_endpoints()