"""
Quick script to add test students to a batch for fee management testing
"""
from app import create_app
from models import db, User, Batch, UserRole
from flask_bcrypt import Bcrypt

app = create_app()
bcrypt = Bcrypt()

with app.app_context():
    # Get the first batch
    batch = Batch.query.first()
    
    if not batch:
        print("❌ No batches found! Please create a batch first.")
        exit(1)
    
    print(f"✅ Found batch: {batch.name} (ID: {batch.id})")
    print(f"   Current students: {len(batch.students)}")
    
    # Create or find test students
    students_to_add = []
    test_students = [
        {"first_name": "Rahul", "last_name": "Ahmed", "phone": "01711111111"},
        {"first_name": "Fatima", "last_name": "Khan", "phone": "01722222222"},
        {"first_name": "Hassan", "last_name": "Rahman", "phone": "01733333333"},
        {"first_name": "Ayesha", "last_name": "Begum", "phone": "01744444444"},
        {"first_name": "Imran", "last_name": "Hossain", "phone": "01755555555"},
    ]
    
    for student_data in test_students:
        # Check if student exists
        student = User.query.filter_by(phoneNumber=student_data["phone"]).first()
        
        if not student:
            # Create new student
            student = User(
                phoneNumber=student_data["phone"],
                password=bcrypt.generate_password_hash("student123").decode('utf-8'),
                first_name=student_data["first_name"],
                last_name=student_data["last_name"],
                role=UserRole.STUDENT,
                is_active=True
            )
            db.session.add(student)
            db.session.flush()
            print(f"   ➕ Created student: {student.full_name}")
        else:
            print(f"   ✓ Found existing student: {student.full_name}")
        
        students_to_add.append(student)
    
    # Add students to batch
    for student in students_to_add:
        if student not in batch.students:
            batch.students.append(student)
            print(f"   ✅ Added {student.full_name} to batch")
        else:
            print(f"   ⚠️  {student.full_name} already in batch")
    
    db.session.commit()
    
    print(f"\n✅ Batch '{batch.name}' now has {len(batch.students)} students")
    print("\nStudents in batch:")
    for s in batch.students:
        print(f"   - {s.full_name} (ID: {s.id}, Phone: {s.phoneNumber})")
    
    print(f"\n🎉 Done! You can now test fee management with batch ID: {batch.id}")
    print(f"   Batch name: {batch.name}")
