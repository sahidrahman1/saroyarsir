#!/usr/bin/env python3
"""Create or update the 'sir' super user account in SQLite.

Phone: 01762602056
Password: sir@123@
Role: super_user
"""
import os
from app import create_app
from models import db, User, UserRole
from werkzeug.security import generate_password_hash

PHONE = '01762602056'
PASSWORD = 'sir@123@'
FIRST_NAME = 'Golam'
LAST_NAME = 'Sarowar'
NEW_ROLE = UserRole.TEACHER

def main():
    # Force production config if desired or default to development (both SQLite now)
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)
    with app.app_context():
        db.create_all()
        user = User.query.filter_by(phoneNumber=PHONE).first()
        if user:
            print(f"Updating existing user {PHONE}")
            user.first_name = FIRST_NAME
            user.last_name = LAST_NAME
            user.role = NEW_ROLE
        else:
            print(f"Creating new super user {PHONE}")
            user = User(
                phoneNumber=PHONE,
                first_name=FIRST_NAME,
                last_name=LAST_NAME,
                role=NEW_ROLE,
                is_active=True
            )
            db.session.add(user)
        user.password_hash = generate_password_hash(PASSWORD)
        db.session.commit()
        print("✅ Sir account ready (phone=01762602056, password=sir@123@)")

if __name__ == '__main__':
    main()