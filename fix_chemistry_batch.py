#!/usr/bin/env python3
"""
Add students to HSC Chemistry Batch C so we can test fee management
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
        print("👥 Adding students to HSC Chemistry Batch C...")
        
        # Find HSC Chemistry Batch C
        chemistry_batch = Batch.query.filter_by(name="HSC Chemistry Batch C").first()
        if not chemistry_batch:
            print("❌ HSC Chemistry Batch C not found!")
            exit(1)
        
        print(f"📚 Found batch: {chemistry_batch.name} (ID: {chemistry_batch.id})")
        
        # Get some students to add to this batch
        available_students = User.query.filter_by(role=UserRole.STUDENT, is_active=True).all()
        
        print(f"👥 Found {len(available_students)} active students")
        
        # Add first 3 students to chemistry batch if they're not already in it
        added_count = 0
        for student in available_students[:3]:
            if chemistry_batch not in student.batches:
                student.batches.append(chemistry_batch)
                added_count += 1
                print(f"   ✅ Added {student.full_name} to chemistry batch")
            else:
                print(f"   ⚠️  {student.full_name} already in chemistry batch")
        
        db.session.commit()
        
        # Verify the changes
        chemistry_batch = Batch.query.filter_by(name="HSC Chemistry Batch C").first()
        student_count = len([s for s in chemistry_batch.students if s.is_active])
        
        print(f"\n🎉 Success! HSC Chemistry Batch C now has {student_count} students:")
        for student in chemistry_batch.students:
            if student.is_active:
                print(f"   - {student.full_name} (ID: {student.id})")
        
        print("\n🔄 Now try refreshing the fee management page and selecting HSC Chemistry Batch C!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()