"""
Password generation utilities for students
Creates unique, memorable passwords for each student
"""
import hashlib
import random
import string
from datetime import datetime

def generate_unique_student_password(first_name, last_name, guardian_phone, student_id=None):
    """
    Generate a unique password for a student based on their information
    
    Format: FirstName + Last4DigitsOfGuardianPhone + RandomNumber
    Example: "John1234567" -> "John4567R8"
    
    Args:
        first_name: Student's first name
        last_name: Student's last name  
        guardian_phone: Guardian's phone number
        student_id: Optional student ID for extra uniqueness
        
    Returns:
        str: Unique password (8-12 characters)
    """
    # Clean and capitalize first name (max 4 chars)
    clean_first_name = first_name.strip().replace(' ', '').capitalize()[:4]
    
    # Get last 4 digits of guardian phone
    phone_digits = ''.join(filter(str.isdigit, guardian_phone))[-4:]
    
    # Generate a random letter and number for uniqueness
    random_letter = random.choice(string.ascii_uppercase)
    random_digit = random.randint(1, 9)
    
    # Create password: FirstName + PhoneDigits + RandomLetter + RandomDigit
    password = f"{clean_first_name}{phone_digits}{random_letter}{random_digit}"
    
    return password

def generate_secure_student_password(first_name, guardian_phone):
    """
    Generate a more secure but still memorable password
    
    Format: First3CharsOfName + Last3DigitsOfPhone + Year + RandomChar
    Example: "Joh345246A" (John, phone ending 345, 2024, random A)
    
    Args:
        first_name: Student's first name
        guardian_phone: Guardian's phone number
        
    Returns:
        str: Secure password (8-10 characters)
    """
    # Clean first name (first 3 chars, capitalized)
    clean_name = first_name.strip().replace(' ', '').capitalize()[:3]
    
    # Get last 3 digits of guardian phone
    phone_digits = ''.join(filter(str.isdigit, guardian_phone))[-3:]
    
    # Current year (last 2 digits)
    current_year = str(datetime.now().year)[-2:]
    
    # Random uppercase letter
    random_char = random.choice(string.ascii_uppercase)
    
    # Create password
    password = f"{clean_name}{phone_digits}{current_year}{random_char}"
    
    return password

def generate_simple_unique_password(first_name, guardian_phone):
    """
    Generate a simple but unique password for students
    
    Format: FirstName + Last4DigitsOfPhone
    Example: "John1234" (simpler for younger students)
    
    Args:
        first_name: Student's first name
        guardian_phone: Guardian's phone number
        
    Returns:
        str: Simple unique password
    """
    # Clean first name (max 6 chars)
    clean_name = first_name.strip().replace(' ', '').capitalize()[:6]
    
    # Get last 4 digits of guardian phone
    phone_digits = ''.join(filter(str.isdigit, guardian_phone))[-4:]
    
    # Create simple password
    password = f"{clean_name}{phone_digits}"
    
    return password

def validate_student_password_strength(password):
    """
    Validate if a student password meets basic requirements
    
    Args:
        password: Password to validate
        
    Returns:
        tuple: (is_valid, message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if len(password) > 15:
        return False, "Password should not exceed 15 characters"
    
    # Check for at least one letter and one number
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not (has_letter and has_number):
        return False, "Password must contain both letters and numbers"
    
    return True, "Password is valid"

# Example usage and testing
if __name__ == "__main__":
    # Test password generation
    test_cases = [
        ("Ahmed", "Rahman", "01712345678"),
        ("Fatima", "Khatun", "01812345679"),
        ("Mohammad", "Ali", "01912345680"),
        ("Rashida", "Begum", "01612345681"),
    ]
    
    print("🔐 STUDENT PASSWORD GENERATION TEST")
    print("=" * 50)
    
    for first, last, phone in test_cases:
        unique_pass = generate_unique_student_password(first, last, phone)
        secure_pass = generate_secure_student_password(first, phone)
        simple_pass = generate_simple_unique_password(first, phone)
        
        print(f"\nStudent: {first} {last}")
        print(f"Guardian Phone: {phone}")
        print(f"Unique Password: {unique_pass}")
        print(f"Secure Password: {secure_pass}")
        print(f"Simple Password: {simple_pass}")
        
        # Validate passwords
        for pass_type, password in [("Unique", unique_pass), ("Secure", secure_pass), ("Simple", simple_pass)]:
            is_valid, message = validate_student_password_strength(password)
            print(f"  {pass_type} Validation: {'✅' if is_valid else '❌'} {message}")