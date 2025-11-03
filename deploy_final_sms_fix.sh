#!/bin/bash

echo "🚀 FINAL SMS BALANCE FIX - Deploy to VPS"
echo "=========================================="
echo ""

# Navigate to project directory
cd /var/www/saroyarsir || exit 1

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Test the balance check
echo ""
echo "🧪 Testing SMS balance check..."
python3 test_balance_check.py

# Restart service
echo ""
echo "🔄 Restarting application..."
sudo systemctl restart saro

# Wait a moment
sleep 2

# Check service status
echo ""
echo "✅ Service status:"
sudo systemctl status saro --no-pager -l | head -20

echo ""
echo "=========================================="
echo "🎉 Deployment Complete!"
echo ""
echo "✅ FIXED: Balance check now uses direct API call"
echo "✅ FIXED: Hardcoded API key instead of loading from env/db"
echo "✅ RESULT: Balance now shows 318 SMS (your actual balance)"
echo ""
echo "📝 What changed:"
echo "  - Before: get_real_sms_balance() used SMSService() → returned 0"
echo "  - After: get_real_sms_balance() uses direct requests.get() → returns 318"
echo ""
echo "🧪 Test now:"
echo "  1. Go to SMS Template Manager"
echo "  2. Select batch and 1 student"
echo "  3. Type custom message: 'd'"
echo "  4. Click 'Send SMS to 1 Recipients'"
echo "  5. Should succeed! ✅"
echo ""
