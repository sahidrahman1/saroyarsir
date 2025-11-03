#!/usr/bin/env python3
"""
Test batch delete functionality
"""
import requests
import json

def test_batch_delete():
    """Test that teachers can delete batches"""
    
    base_url = "http://127.0.0.1:5001"
    
    print("🧪 Testing Batch Delete Functionality")
    print("=" * 50)
    
    # Login as teacher
    print("\n📱 Logging in as teacher...")
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "phoneNumber": "01812345678",
        "password": "teacher123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    print("✅ Teacher login successful")
    
    # Create a session to maintain cookies
    session = requests.Session()
    session.cookies.update(login_response.cookies)
    
    # First, create a test batch to delete
    print("\n📚 Creating a test batch...")
    batch_data = {
        "name": "Test Delete Batch",
        "class": "Class 9",
        "subject": "Mathematics"
    }
    
    create_response = session.post(f"{base_url}/api/batches", json=batch_data)
    
    if create_response.status_code == 201:
        created_batch = create_response.json()
        batch_id = created_batch['data']['batch']['id']
        print(f"✅ Test batch created with ID: {batch_id}")
        
        # Now test deleting the batch
        print(f"\n🗑️ Testing batch delete for ID: {batch_id}...")
        delete_response = session.delete(f"{base_url}/api/batches/{batch_id}")
        
        print(f"Delete response status: {delete_response.status_code}")
        
        if delete_response.status_code == 200:
            print("✅ Batch delete successful!")
            response_data = delete_response.json()
            print(f"Response: {response_data.get('message', 'Success')}")
        elif delete_response.status_code == 403:
            print("❌ Still getting 403 Forbidden - permission issue")
        elif delete_response.status_code == 400:
            print("⚠️ Can't delete - batch may have active students")
            print(f"Response: {delete_response.text}")
        else:
            print(f"❌ Delete failed with status {delete_response.status_code}")
            print(f"Response: {delete_response.text}")
    
    elif create_response.status_code == 409:
        print("⚠️ Batch with that name already exists, trying to find and delete it...")
        
        # Get all batches and find one we can delete
        batches_response = session.get(f"{base_url}/api/batches")
        if batches_response.status_code == 200:
            batches_data = batches_response.json()
            batches = batches_data.get('data', {}).get('batches', [])
            
            # Find a batch without students
            for batch in batches:
                if batch.get('currentStudents', 0) == 0:
                    batch_id = batch['id']
                    print(f"🎯 Found empty batch to test delete: {batch['name']} (ID: {batch_id})")
                    
                    delete_response = session.delete(f"{base_url}/api/batches/{batch_id}")
                    print(f"Delete response status: {delete_response.status_code}")
                    
                    if delete_response.status_code == 200:
                        print("✅ Batch delete successful!")
                    elif delete_response.status_code == 403:
                        print("❌ Still getting 403 Forbidden - need to check server restart")
                    else:
                        print(f"Response: {delete_response.text}")
                    break
            else:
                print("⚠️ No empty batches found to test deletion")
    else:
        print(f"❌ Failed to create test batch: {create_response.text}")

if __name__ == "__main__":
    test_batch_delete()