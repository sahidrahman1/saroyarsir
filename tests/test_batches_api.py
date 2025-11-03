#!/usr/bin/env python3
"""
Test Batches API endpoint
"""
import requests
import json

def test_batches_api():
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    try:
        # Login first
        print("🔐 Testing login...")
        login_response = session.post(f"{base_url}/api/auth/login", 
            json={'phoneNumber': '01812345678', 'password': 'teacher123'})
        
        print(f"Login Status: {login_response.status_code}")
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return
        
        print("✅ Login successful!")
        
        # Test batches API
        print("\n📚 Testing batches API...")
        batches_response = session.get(f"{base_url}/api/batches")
        print(f"Batches Status: {batches_response.status_code}")
        
        if batches_response.status_code == 200:
            batches_data = batches_response.json()
            print("✅ Batches API working!")
            print(f"Response structure: {json.dumps(batches_data, indent=2)}")
            
            # Check if data exists
            if 'data' in batches_data and batches_data['data']:
                print(f"📊 Found {len(batches_data['data'])} batches")
                for batch in batches_data['data']:
                    print(f"  - {batch.get('name', 'Unknown')} ({batch.get('subject', 'Unknown')})")
            else:
                print("📭 No batches found in database")
        else:
            print(f"❌ Batches API failed: {batches_response.text}")
        
        # Create a test batch
        print("\n➕ Testing batch creation...")
        create_response = session.post(f"{base_url}/api/batches", 
            json={'name': 'Test MySQL Batch', 'subject': 'math'})
        
        print(f"Create Status: {create_response.status_code}")
        if create_response.status_code == 201:
            print("✅ Batch created successfully!")
            print(f"Response: {create_response.json()}")
            
            # Test batches API again
            print("\n📚 Testing batches API after creation...")
            batches_response2 = session.get(f"{base_url}/api/batches")
            if batches_response2.status_code == 200:
                batches_data2 = batches_response2.json()
                if 'data' in batches_data2:
                    print(f"📊 Now found {len(batches_data2['data'])} batches")
                    for batch in batches_data2['data']:
                        print(f"  - {batch.get('name', 'Unknown')} ({batch.get('subject', 'Unknown')})")
        else:
            print(f"❌ Batch creation failed: {create_response.text}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_batches_api()