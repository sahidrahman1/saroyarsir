#!/usr/bin/env python3
"""
Quick check to see what batches exist and how many students are in each batch
"""
import os
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_PASSWORD'] = 'sahidx@12'
os.environ['MYSQL_DATABASE'] = 'smartgardenhub'

from app import create_app
from models import db, User, Batch, UserRole

app = create_app()

with app.app_context():
    try:
        print("📊 Checking batch and student data...")
        print("=" * 50)
        
        # Get all batches
        batches = Batch.query.filter_by(is_active=True).all()
        print(f"🎓 Found {len(batches)} active batches:")
        
        for batch in batches:
            student_count = len([s for s in batch.students if s.is_active])
            print(f"   - {batch.name} (ID: {batch.id}) - {student_count} students")
            
            # Show first few students in this batch
            active_students = [s for s in batch.students if s.is_active][:3]
            for student in active_students:
                print(f"     * {student.full_name} (ID: {student.id}, Phone: {student.phoneNumber})")
            
            if len(active_students) > 3:
                print(f"     ... and {len([s for s in batch.students if s.is_active]) - 3} more")
        
        print("\n👥 All Students Summary:")
        all_students = User.query.filter_by(role=UserRole.STUDENT, is_active=True).all()
        print(f"   Total active students: {len(all_students)}")
        
        students_with_batches = [s for s in all_students if len(s.batches) > 0]
        students_without_batches = [s for s in all_students if len(s.batches) == 0]
        
        print(f"   Students enrolled in batches: {len(students_with_batches)}")
        print(f"   Students NOT enrolled in any batch: {len(students_without_batches)}")
        
        if students_without_batches:
            print("\n   Students without batches:")
            for student in students_without_batches[:5]:
                print(f"     - {student.full_name} (ID: {student.id})")
        
        # Test API endpoint directly
        print("\n🔗 Testing API endpoint...")
        if batches:
            first_batch = batches[0]
            print(f"   Testing /api/batches/{first_batch.id}/students")
            
            from routes.batches import get_batch_students
            from unittest.mock import MagicMock
            
            # Mock the authentication decorators
            import routes.batches
            original_login_required = routes.batches.login_required
            original_require_role = routes.batches.require_role
            
            routes.batches.login_required = lambda f: f
            routes.batches.require_role = lambda *args: lambda f: f
            
            try:
                result = get_batch_students(first_batch.id)
                print(f"   API Response: {result}")
            except Exception as e:
                print(f"   API Error: {e}")
            finally:
                # Restore decorators
                routes.batches.login_required = original_login_required
                routes.batches.require_role = original_require_role
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()