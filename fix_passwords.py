from models import db, User, UserRole
from flask import Flask
from config import DevelopmentConfig
from flask_bcrypt import Bcrypt, generate_password_hash

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
db.init_app(app)
bcrypt = Bcrypt(app)

with app.app_context():
    print("Fixing password hashes for all users...")
    
    # Get all users and update their password hashes
    users = User.query.all()
    
    for user in users:
        if user.role == UserRole.SUPER_USER:
            # Super admin gets admin123
            new_hash = generate_password_hash("admin123")
            user.password_hash = new_hash
            print(f"Updated super user {user.phoneNumber} with admin123")
            
        elif user.role == UserRole.TEACHER:
            # Teachers get teacher123 
            new_hash = generate_password_hash("teacher123")
            user.password_hash = new_hash
            print(f"Updated teacher {user.phoneNumber} with teacher123")
            
        elif user.role == UserRole.STUDENT:
            # Students get student123 (but we'll keep backward compatibility in auth)
            new_hash = generate_password_hash("student123")
            user.password_hash = new_hash
            print(f"Updated student {user.phoneNumber} with student123")
    
    # Commit all changes
    db.session.commit()
    print("\nAll password hashes updated successfully!")
    
    # Test the new hashes
    print("\nTesting new password hashes:")
    from flask_bcrypt import check_password_hash
    
    for user in users:
        test_password = "admin123" if user.role == UserRole.SUPER_USER else \
                       "teacher123" if user.role == UserRole.TEACHER else "student123"
        
        result = check_password_hash(user.password_hash, test_password)
        print(f"{user.phoneNumber} ({user.role.value}): Password '{test_password}' - {result}")