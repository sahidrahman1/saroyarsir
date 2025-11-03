"""
Test SMS Templates and Character Counting
Tests the new template system with Bengali character support
"""
import requests
import json

BASE_URL = 'http://localhost:5001'

def login():
    """Login as teacher"""
    response = requests.post(f'{BASE_URL}/api/auth/login', json={
        'phoneNumber': '01812345678',
        'password': 'teacher123'
    })
    return response.cookies

def test_get_templates(cookies):
    """Test getting SMS templates"""
    print("\n" + "="*60)
    print("📋 Testing SMS Templates")
    print("="*60)
    
    response = requests.get(f'{BASE_URL}/api/sms/templates', cookies=cookies)
    data = response.json()
    
    if data['success']:
        print(f"✅ Templates loaded successfully")
        print(f"\n📊 Character Rules:")
        rules = data['data']['character_rules']
        print(f"  - English characters: {rules['english']} char each")
        print(f"  - Bangla characters: {rules['bangla']} chars each")
        print(f"  - Total limit: {rules['total_limit']} characters")
        
        print(f"\n📝 Available Templates:")
        for template in data['data']['templates']:
            print(f"\n  {template['id']}. {template['name']} ({template['category']})")
            print(f"     Message: {template['message']}")
            print(f"     Estimated chars: {template['char_count']}")
            print(f"     Variables: {', '.join(template['variables'])}")
            print(f"     Editable: {template['editable']}")
    else:
        print(f"❌ Failed: {data.get('message')}")

def test_validate_message(cookies):
    """Test message validation"""
    print("\n" + "="*60)
    print("🔍 Testing Message Validation")
    print("="*60)
    
    test_messages = [
        ("English only", "Hello, this is a test message with English characters only."),
        ("Mixed", "Dear Parent, আপনার সন্তান আজ উপস্থিত ছিল। Thank you."),
        ("Bangla", "প্রিয় অভিভাবক, আপনার সন্তান আজ স্কুলে উপস্থিত ছিল।"),
        ("Long message", "This is a very long message that should exceed the character limit of 130 characters when counting properly with English and Bengali text mixed together for testing purposes.")
    ]
    
    for name, message in test_messages:
        print(f"\n📝 Testing: {name}")
        print(f"   Message: {message[:50]}...")
        
        response = requests.post(
            f'{BASE_URL}/api/sms/validate-message',
            json={'message': message},
            cookies=cookies
        )
        data = response.json()
        
        if data['success']:
            result = data['data']
            status = "✅ Valid" if result['is_valid'] else "❌ Too long"
            print(f"   {status}")
            print(f"   Character count: {result['char_count']}/{result['max_characters']}")
            print(f"   Remaining: {result['remaining']} chars")
            print(f"   Estimated SMS: {result['estimated_sms']}")
            print(f"   Actual length: {result['message_length']} chars")
        else:
            print(f"   ❌ Failed: {data.get('message')}")

def test_attendance_template(cookies):
    """Test attendance template with variables"""
    print("\n" + "="*60)
    print("📧 Testing Attendance Template")
    print("="*60)
    
    # Simulate filling template
    template = "Dear Parent, {student_name} was PRESENT today in {batch_name} on {date}. Keep up the good work!"
    filled = template.format(
        student_name="Ahmed Hassan",
        batch_name="Class 10 - Science",
        date="11-10-2025"
    )
    
    print(f"\n📋 Template: {template}")
    print(f"✏️  Filled: {filled}")
    
    response = requests.post(
        f'{BASE_URL}/api/sms/validate-message',
        json={'message': filled},
        cookies=cookies
    )
    data = response.json()
    
    if data['success']:
        result = data['data']
        status = "✅ Valid" if result['is_valid'] else "❌ Too long"
        print(f"\n{status}")
        print(f"Character count: {result['char_count']}/{result['max_characters']}")
        print(f"Ready to send: {result['is_valid']}")

def test_exam_template(cookies):
    """Test exam result template"""
    print("\n" + "="*60)
    print("📊 Testing Exam Result Template")
    print("="*60)
    
    template = "{student_name}, {exam_name} Result: {marks}/{total} ({percentage}%). Position: {position}. {remark}"
    filled = template.format(
        student_name="Fatima",
        exam_name="Midterm Physics",
        marks="85",
        total="100",
        percentage="85",
        position="3rd",
        remark="Excellent!"
    )
    
    print(f"\n📋 Template: {template}")
    print(f"✏️  Filled: {filled}")
    
    response = requests.post(
        f'{BASE_URL}/api/sms/validate-message',
        json={'message': filled},
        cookies=cookies
    )
    data = response.json()
    
    if data['success']:
        result = data['data']
        status = "✅ Valid" if result['is_valid'] else "❌ Too long"
        print(f"\n{status}")
        print(f"Character count: {result['char_count']}/{result['max_characters']}")
        print(f"Ready to send: {result['is_valid']}")

def main():
    """Run all tests"""
    print("\n🚀 Starting SMS Template Tests")
    print("="*60)
    
    try:
        # Login
        cookies = login()
        print("✅ Logged in successfully")
        
        # Run tests
        test_get_templates(cookies)
        test_validate_message(cookies)
        test_attendance_template(cookies)
        test_exam_template(cookies)
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == '__main__':
    main()
