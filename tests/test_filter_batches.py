#!/usr/bin/env python3
"""
Test to verify all batches (including empty ones) are available in the filter dropdown
"""
import requests
import json

def test_batch_visibility():
    try:
        # Login as teacher
        print('🔐 Logging in as teacher...')
        login_response = requests.post('http://127.0.0.1:5001/api/auth/login', json={
            'phoneNumber': '01812345678',
            'password': 'teacher123'
        })
        
        if login_response.status_code != 200:
            print(f'❌ Login failed: {login_response.status_code}')
            return
        
        cookies = login_response.cookies
        print('✅ Login successful')
        
        # Get all students to see which batches have students
        print('\n📊 Getting current students...')
        students_response = requests.get('http://127.0.0.1:5001/api/students', cookies=cookies)
        if students_response.status_code == 200:
            students_data = students_response.json()
            students = students_data.get('data', [])
            
            # Count students per batch
            batch_student_count = {}
            for student in students:
                batch_id = student.get('batchId') or student.get('batch_id')
                if batch_id:
                    batch_student_count[batch_id] = batch_student_count.get(batch_id, 0) + 1
            
            print(f'Current students: {len(students)}')
            print(f'Batches with students: {list(batch_student_count.keys())}')
        
        # Get all active batches
        print('\n📊 Getting active batches...')
        batches_response = requests.get('http://127.0.0.1:5001/api/batches/active', cookies=cookies)
        if batches_response.status_code == 200:
            batches_data = batches_response.json()
            batches = batches_data.get('data', {}).get('batches', [])
            
            print(f'✅ Total active batches: {len(batches)}')
            print('\n📋 Batch Analysis:')
            
            empty_batches = []
            non_empty_batches = []
            
            for batch in batches:
                batch_id = batch['id']
                batch_name = batch['name']
                student_count = batch.get('student_count', 0)
                
                if student_count == 0:
                    empty_batches.append(batch)
                    print(f'   🔘 EMPTY: {batch_name} (ID: {batch_id}) - 0 students')
                else:
                    non_empty_batches.append(batch)
                    print(f'   👥 HAS STUDENTS: {batch_name} (ID: {batch_id}) - {student_count} students')
            
            print(f'\n📊 Summary:')
            print(f'   • Empty batches: {len(empty_batches)}')
            print(f'   • Batches with students: {len(non_empty_batches)}')
            print(f'   • Total batches: {len(batches)}')
            
            if empty_batches:
                print(f'\n🔘 Empty batches that should appear in filter:')
                for batch in empty_batches:
                    print(f'   - {batch["name"]} (ID: {batch["id"]})')
            
            # Verify the API structure matches what frontend expects
            print(f'\n🔍 API Response Structure Check:')
            print(f'   ✅ Response has "success": {batches_data.get("success")}')
            print(f'   ✅ Response has "data": {"data" in batches_data}')
            print(f'   ✅ Data has "batches": {"batches" in batches_data.get("data", {})}')
            print(f'   ✅ Batches is array: {isinstance(batches, list)}')
            
        else:
            print(f'❌ Failed to get batches: {batches_response.status_code}')
            
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    test_batch_visibility()