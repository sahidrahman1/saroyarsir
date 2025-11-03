from models import db, User, UserRole
from flask import Flask
from config import DevelopmentConfig
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
db.init_app(app)
bcrypt = Bcrypt(app)

with app.app_context():
    users = User.query.all()
    print(f"Found {len(users)} users:")
    
    for u in users:
        print(f"\nUser: {u.phoneNumber}")
        print(f"Role: {u.role.value}")
        print(f"First Name: {u.first_name}")
        print(f"Has password_hash: {bool(u.password_hash)}")
        if u.password_hash:
            print(f"Password hash length: {len(u.password_hash)}")
            print(f"Hash starts with: {u.password_hash[:20]}...")
            
            # Test password check
            try:
                from flask_bcrypt import check_password_hash
                test_result = check_password_hash(u.password_hash, "admin123")
                print(f"Password 'admin123' check: {test_result}")
            except Exception as e:
                print(f"Password check error: {e}")
        else:
            print("No password hash stored")
        print("-" * 50)