#!/usr/bin/env python3
"""
Test SMS Balance Check - Verify the fix works
This script tests the balance check function to ensure it returns 990 SMS
"""

import requests

def get_real_sms_balance():
    """Get actual SMS balance from API"""
    try:
        # Use direct API call with hardcoded key
        api_key = 'gsOKLO6XtKsANCvgPHNt'
        
        params = {'api_key': api_key}
        response = requests.get(
            'http://bulksmsbd.net/api/getBalanceApi',
            params=params,
            timeout=10
        )
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            balance = int(data.get('balance', 0)) if data.get('balance') else 0
            return balance
        return 0
    except Exception as e:
        print(f"Error getting SMS balance: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    print("Testing SMS Balance API...")
    print("=" * 50)
    
    balance = get_real_sms_balance()
    
    print("=" * 50)
    print(f"✅ Current Balance: {balance} SMS")
    
    if balance > 0:
        print("✅ SUCCESS: Balance check is working correctly!")
        print(f"   You have {balance} SMS available")
    else:
        print("❌ ERROR: Balance check returned 0")
        print("   Check API key and endpoint")
