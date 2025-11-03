"""
Password generation utilities for students
Creates unique, memorable passwords for each student
"""
import random
import string
from datetime import datetime

def generate_unique_student_password(first_name, last_name, guardian_phone, student_id=None):
    """Generate a unique password for a student based on their information"""
    clean_first_name = first_name.strip().replace(' ', '').capitalize()[:4]
    phone_digits = ''.join(filter(str.isdigit, guardian_phone))[-4:]
    random_letter = random.choice(string.ascii_uppercase)
    random_digit = random.randint(1, 9)
    password = f"{clean_first_name}{phone_digits}{random_letter}{random_digit}"
    return password

def generate_secure_student_password(first_name, guardian_phone):
    """Generate a more secure but still memorable password"""
    clean_name = first_name.strip().replace(' ', '').capitalize()[:3]
    phone_digits = ''.join(filter(str.isdigit, guardian_phone))[-3:]
    current_year = str(datetime.now().year)[-2:]
    random_char = random.choice(string.ascii_uppercase)
    password = f"{clean_name}{phone_digits}{current_year}{random_char}"
    return password

def generate_simple_unique_password(first_name, guardian_phone):
    """Generate a simple but unique password for students"""
    clean_name = first_name.strip().replace(' ', '').capitalize()[:6]
    phone_digits = ''.join(filter(str.isdigit, guardian_phone))[-4:]
    password = f"{clean_name}{phone_digits}"
    return password

def validate_student_password_strength(password):
    """Validate if a student password meets basic requirements"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    if len(password) > 15:
        return False, "Password should not exceed 15 characters"
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    if not (has_letter and has_number):
        return False, "Password must contain both letters and numbers"
    return True, "Password is valid"
