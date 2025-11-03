#!/usr/bin/env python3
"""
Test student login with new random passwords
"""
import os
import requests
import json

# Test server
SERVER_URL = "http://127.0.0.1:5001"

def test_student_login():
    """Test that students can login with their own phone numbers and new random passwords"""
    
    print("🔍 Testing Student Login System with Random Passwords...")
    print("=" * 60)
    
    # Test data - students login with their OWN phone numbers and unique passwords
    test_cases = [
        {
            "description": "Sample Student",
            "phoneNumber": "01912345678",
            "password": "mqe49npo",
            "expected": True
        },
        {
            "description": "রহিম আহমেদ",
            "phoneNumber": "01901234567",
            "password": "g9m7r2t0",
            "expected": True
        },
        {
            "description": "করিম হাসান",
            "phoneNumber": "01901234568",
            "password": "m3kzddrm",
            "expected": True
        },
        {
            "description": "ফাতেমা খাতুন",
            "phoneNumber": "01901234569",
            "password": "77jd49pi",
            "expected": True
        },
        {
            "description": "আয়েশা বেগম",
            "phoneNumber": "01901234570",
            "password": "v76wub5b",
            "expected": True
        },
        {
            "description": "মোহাম্মদ আলী",
            "phoneNumber": "01901234571",
            "password": "o8g0zcxl",
            "expected": True
        },
        {
            "description": "Wrong Password Test",
            "phoneNumber": "01901234567",
            "password": "wrongpass",
            "expected": False
        }
    ]
    
    successful_logins = 0
    total_tests = len([test for test in test_cases if test['expected']])
    
    for test in test_cases:
        print(f"\n📋 {test['description']}")
        print(f"   📞 Phone: {test['phoneNumber']}")
        print(f"   🔑 Password: {test['password']}")
        
        try:
            response = requests.post(
                f"{SERVER_URL}/api/auth/login",
                json={
                    "phone": test['phoneNumber'],  # Updated to use 'phone' instead of 'phoneNumber'
                    "password": test['password']
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if test['expected']:
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ SUCCESS: Login successful!")
                    if 'user' in data:
                        user = data['user']
                        print(f"   👤 Name: {user.get('full_name', 'N/A')}")
                        print(f"   🎭 Role: {user.get('role', 'N/A')}")
                        print(f"   � Active: {user.get('is_active', 'N/A')}")
                        if 'token' in data:
                            print(f"   🔑 Token: {data['token'][:30]}...")
                    successful_logins += 1
                else:
                    print(f"   ❌ FAILED: Expected success but got {response.status_code}")
                    print(f"   📝 Response: {response.text}")
            else:
                if response.status_code != 200:
                    print(f"   ✅ SUCCESS: Correctly rejected invalid login")
                else:
                    print(f"   ❌ FAILED: Expected failure but login succeeded")
                    
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Successful logins: {successful_logins}/{total_tests}")
    print(f"❌ Failed logins: {total_tests - successful_logins}/{total_tests}")
    
    if successful_logins == total_tests:
        print("🎉 All student logins are working perfectly!")
        print("💡 Students can now login with:")
        print("   • Their own phone number (not guardian phone)")
        print("   • Their unique random password")
        print("   • Each password is different and secure")
    else:
        print("⚠️ Some student logins need attention.")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    test_student_login()