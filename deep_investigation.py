#!/usr/bin/env python3
"""
Deep investigation of both backend and frontend
"""
import requests
import json
import time

def test_server_connectivity():
    """Test basic server connectivity"""
    print("=== 1. SERVER CONNECTIVITY TEST ===")
    
    try:
        # Test basic health
        response = requests.get('http://127.0.0.1:5000/', timeout=5)
        print(f"✅ Server root accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Server root failed: {e}")
        return False
    
    try:
        # Test API endpoint
        response = requests.get('http://127.0.0.1:5000/api/dashboard/stats', timeout=5)
        print(f"✅ Dashboard API accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard API failed: {e}")
        return False
    
    return True

def test_fee_routes():
    """Test all fee-related routes"""
    print("\n=== 2. FEE ROUTES TEST ===")
    
    base_url = "http://127.0.0.1:5000/api/fees"
    
    # Test GET /api/fees/monthly (this works according to logs)
    try:
        response = requests.get(f"{base_url}/monthly?batch_id=1&year=2025", timeout=5)
        print(f"✅ GET /api/fees/monthly: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response size: {len(response.text)} chars")
    except Exception as e:
        print(f"❌ GET /api/fees/monthly failed: {e}")
    
    # Test POST /api/fees/monthly (this fails)
    try:
        fee_data = {
            "student_id": 1,
            "month": 1,
            "year": 2025,
            "amount": 100
        }
        response = requests.post(f"{base_url}/monthly", 
                               json=fee_data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=5)
        print(f"✅ POST /api/fees/monthly: {response.status_code}")
        if response.status_code != 404:
            print(f"   Response: {response.text[:200]}")
        else:
            print(f"   ❌ Still getting 404!")
    except Exception as e:
        print(f"❌ POST /api/fees/monthly failed: {e}")
    
    # Test the simple route
    try:
        response = requests.post(f"{base_url}/monthly-simple", 
                               json={"test": "data"}, 
                               headers={'Content-Type': 'application/json'},
                               timeout=5)
        print(f"✅ POST /api/fees/monthly-simple: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ POST /api/fees/monthly-simple failed: {e}")

def test_student_routes():
    """Test student routes"""
    print("\n=== 3. STUDENT ROUTES TEST ===")
    
    try:
        # Test GET students
        response = requests.get('http://127.0.0.1:5000/api/students', timeout=5)
        print(f"✅ GET /api/students: {response.status_code}")
    except Exception as e:
        print(f"❌ GET /api/students failed: {e}")
    
    try:
        # Test POST students with unique phone
        import random
        unique_phone = f"0177700{random.randint(1000, 9999)}"
        student_data = {
            "firstName": "Test",
            "lastName": "Deep", 
            "guardianPhone": unique_phone,
            "guardianName": "Test Guardian",
            "school": "Test School"
        }
        response = requests.post('http://127.0.0.1:5000/api/students', 
                               json=student_data, 
                               headers={'Content-Type': 'application/json'},
                               timeout=5)
        print(f"✅ POST /api/students: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"   ✅ Student creation works!")
        elif response.status_code == 409:
            print(f"   ⚠️ Phone exists (endpoint works)")
        else:
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ POST /api/students failed: {e}")

def check_frontend_code():
    """Check frontend fee management code"""
    print("\n=== 4. FRONTEND CODE ANALYSIS ===")
    
    try:
        with open('/workspaces/saro/templates/templates/partials/fee_management.html', 'r') as f:
            content = f.read()
            
        # Look for the POST request
        if 'POST' in content and '/api/fees/monthly' in content:
            print("✅ Frontend has POST to /api/fees/monthly")
            
            # Extract the fetch call
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '/api/fees/monthly' in line and 'POST' in lines[max(0, i-5):i+5]:
                    print(f"   Found at line {i+1}: {line.strip()}")
                    # Show context
                    for j in range(max(0, i-3), min(len(lines), i+4)):
                        marker = ">>>" if j == i else "   "
                        print(f"   {marker} {j+1:3d}: {lines[j].strip()[:100]}")
                    break
        else:
            print("❌ Frontend POST call not found")
            
    except Exception as e:
        print(f"❌ Failed to read frontend: {e}")

def main():
    print("🔍 DEEP BACKEND & FRONTEND INVESTIGATION")
    print("=" * 50)
    
    if not test_server_connectivity():
        print("❌ Server not accessible - stopping investigation")
        return
    
    test_fee_routes()
    test_student_routes() 
    check_frontend_code()
    
    print("\n" + "=" * 50)
    print("📋 INVESTIGATION COMPLETE")

if __name__ == "__main__":
    main()