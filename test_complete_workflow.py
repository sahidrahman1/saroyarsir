"""
Complete test for marks entry workflow
"""
import os
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
import requests
import json

app = create_app()

def test_complete_workflow():
    with app.app_context():
        print("🧪 Testing complete marks entry workflow...")
        
        # Create session
        session = requests.Session()
        session.headers.update({'Content-Type': 'application/json'})
        
        # Step 1: Login
        print("\n1️⃣ Testing login...")
        login_response = session.post('http://127.0.0.1:5001/api/auth/login', 
            json={'phoneNumber': '01812345678', 'password': 'teacher123'})
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
        print("✅ Login successful")
        
        # Step 2: Get batches
        print("\n2️⃣ Testing batches API...")
        batches_response = session.get('http://127.0.0.1:5001/api/batches')
        
        if batches_response.status_code != 200:
            print(f"❌ Batches API failed: {batches_response.text}")
            return False
        
        batches_data = batches_response.json()
        batches = batches_data.get('data', [])
        
        # Find the Class 10 Mathematics batch
        target_batch = None
        for batch in batches:
            if 'Class 10 Mathematics' in batch['name']:
                target_batch = batch
                break
        
        if not target_batch:
            print("❌ Target batch 'Class 10 Mathematics' not found")
            return False
        
        print(f"✅ Found target batch: {target_batch['name']} (ID: {target_batch['id']})")
        
        # Step 3: Get students from batch
        print("\n3️⃣ Testing batch students API...")
        students_response = session.get(f"http://127.0.0.1:5001/api/batches/{target_batch['id']}/students")
        
        if students_response.status_code != 200:
            print(f"❌ Students API failed: {students_response.text}")
            return False
        
        students_data = students_response.json()
        students = students_data.get('data', {}).get('students', [])
        
        if not students:
            print("❌ No students found in batch")
            return False
        
        print(f"✅ Found {len(students)} students in batch")
        for student in students[:3]:
            print(f"   - {student['full_name']} (ID: {student['id']})")
        
        # Step 4: Create a monthly exam
        print("\n4️⃣ Testing monthly exam creation...")
        monthly_exam_data = {
            'title': 'Test Monthly Exam - October 2025',
            'month': 10,
            'year': 2025,
            'batch_id': target_batch['id']
        }
        
        monthly_exam_response = session.post('http://127.0.0.1:5001/api/monthly-exams', 
            json=monthly_exam_data)
        
        if monthly_exam_response.status_code != 201:
            # Check if exam already exists
            if 'already exists' in monthly_exam_response.text:
                print("ℹ️  Monthly exam already exists, continuing...")
                # Get existing monthly exams
                existing_exams_response = session.get(f'http://127.0.0.1:5001/api/monthly-exams?batch_id={target_batch["id"]}&month=10&year=2025')
                if existing_exams_response.status_code == 200:
                    existing_data = existing_exams_response.json()
                    if existing_data.get('data'):
                        monthly_exam = existing_data['data'][0]
                        print(f"✅ Using existing monthly exam: {monthly_exam['title']} (ID: {monthly_exam['id']})")
                    else:
                        print("❌ Could not find existing monthly exam")
                        return False
                else:
                    print(f"❌ Could not get existing monthly exams: {existing_exams_response.text}")
                    return False
            else:
                print(f"❌ Monthly exam creation failed: {monthly_exam_response.text}")
                return False
        else:
            monthly_exam_data = monthly_exam_response.json()
            monthly_exam = monthly_exam_data['data']['monthly_exam']
            print(f"✅ Created monthly exam: {monthly_exam['title']} (ID: {monthly_exam['id']})")
        
        # Step 5: Create an individual exam
        print("\n5️⃣ Testing individual exam creation...")
        individual_exam_data = {
            'title': 'Algebra Test',
            'subject': 'Mathematics',
            'marks': 100
        }
        
        individual_exam_response = session.post(f'http://127.0.0.1:5001/api/monthly-exams/{monthly_exam["id"]}/individual-exams', 
            json=individual_exam_data)
        
        if individual_exam_response.status_code != 201:
            print(f"❌ Individual exam creation failed: {individual_exam_response.text}")
            return False
        
        individual_exam_data = individual_exam_response.json()
        individual_exam = individual_exam_data['data']['individual_exam']
        print(f"✅ Created individual exam: {individual_exam['title']} (ID: {individual_exam['id']})")
        
        # Step 6: Test marks submission
        print("\n6️⃣ Testing marks submission...")
        marks_data = {
            'students': [
                {'user_id': students[0]['id'], 'marks_obtained': 85},
                {'user_id': students[1]['id'], 'marks_obtained': 92},
                {'user_id': students[2]['id'], 'marks_obtained': 78}
            ]
        }
        
        marks_response = session.post(f'http://127.0.0.1:5001/api/monthly-exams/{monthly_exam["id"]}/individual-exams/{individual_exam["id"]}/marks', 
            json=marks_data)
        
        if marks_response.status_code != 200:
            print(f"❌ Marks submission failed: {marks_response.text}")
            return False
        
        marks_result = marks_response.json()
        print(f"✅ Marks saved successfully! {marks_result['data']['saved_count']} students updated")
        
        print(f"\n🎉 All tests passed! Marks entry workflow is working correctly.")
        print(f"📝 Use batch ID {target_batch['id']} for testing in the UI")
        print(f"📝 Monthly exam ID: {monthly_exam['id']}")
        print(f"📝 Individual exam ID: {individual_exam['id']}")
        
        return True

if __name__ == '__main__':
    test_complete_workflow()