"""
Local Password Manager for Students
Stores and verifies student passwords locally without database dependency
"""
import json
import os
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash

# Get the project root directory (where app.py is located)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASSWORD_FILE = os.path.join(PROJECT_ROOT, 'student_passwords.json')

def generate_student_password(length=8):
    """Generate a random password for student"""
    # Format: 2 uppercase + 4 digits + 2 lowercase (easy to remember)
    uppercase = ''.join(random.choices(string.ascii_uppercase, k=2))
    digits = ''.join(random.choices(string.digits, k=4))
    lowercase = ''.join(random.choices(string.ascii_lowercase, k=2))
    
    password = uppercase + digits + lowercase
    return password

def load_passwords():
    """Load passwords from local file"""
    try:
        if os.path.exists(PASSWORD_FILE):
            with open(PASSWORD_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading passwords: {e}")
        return {}

def save_passwords(passwords):
    """Save passwords to local file"""
    try:
        with open(PASSWORD_FILE, 'w') as f:
            json.dump(passwords, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving passwords: {e}")
        return False

def set_student_password(phone_number, password=None):
    """
    Set password for a student
    If password is None, generate a random one
    Returns the plain password (to show to teacher)
    """
    if password is None:
        password = generate_student_password()
    
    # Load existing passwords
    passwords = load_passwords()
    
    # Store hashed password
    passwords[phone_number] = {
        'password_hash': generate_password_hash(password),
        'plain': password  # Store plain text temporarily for teacher to see
    }
    
    # Save to file
    save_passwords(passwords)
    
    return password

def verify_student_password(phone_number, password):
    """Verify student password from local storage"""
    passwords = load_passwords()
    
    if phone_number not in passwords:
        return False
    
    stored = passwords[phone_number]
    
    # Check against hashed password
    if 'password_hash' in stored:
        return check_password_hash(stored['password_hash'], password)
    
    return False

def get_student_password(phone_number):
    """Get student's plain password (for teacher to see)"""
    passwords = load_passwords()
    
    if phone_number in passwords and 'plain' in passwords[phone_number]:
        return passwords[phone_number]['plain']
    
    return None

def remove_plain_password(phone_number):
    """Remove plain text password (after teacher has seen it)"""
    passwords = load_passwords()
    
    if phone_number in passwords and 'plain' in passwords[phone_number]:
        del passwords[phone_number]['plain']
        save_passwords(passwords)
        return True
    
    return False

def get_all_student_passwords():
    """Get all student passwords (for teacher dashboard)"""
    passwords = load_passwords()
    result = []
    
    for phone, data in passwords.items():
        result.append({
            'phoneNumber': phone,
            'password': data.get('plain', 'Password already collected'),
            'hasPassword': True
        })
    
    return result

def delete_student_password(phone_number):
    """Delete student password"""
    passwords = load_passwords()
    
    if phone_number in passwords:
        del passwords[phone_number]
        save_passwords(passwords)
        return True
    
    return False
