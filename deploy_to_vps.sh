#!/bin/bash

# Deployment script for GS Student Nursing Center
# This script pulls latest code and restarts the Flask service

echo "════════════════════════════════════════════════════════════"
echo "  🚀 DEPLOYING TO VPS - GS Student Nursing Center"
echo "════════════════════════════════════════════════════════════"
echo ""

# Instructions for VPS deployment
cat <<'INSTRUCTIONS'

📋 COPY THESE COMMANDS TO RUN ON YOUR VPS:

1. Connect to VPS via SSH:
   ─────────────────────────────────────────────────────────────
   ssh your_username@gsteaching.com
   (or use the IP address)

2. Navigate to project directory:
   ─────────────────────────────────────────────────────────────
   cd /home/your_username/saro
   (or wherever your project is located)

3. Pull latest changes from GitHub:
   ─────────────────────────────────────────────────────────────
   git pull origin main

4. Restart the Flask/Gunicorn service:
   ─────────────────────────────────────────────────────────────
   Option A - If using systemd service:
   sudo systemctl restart saro
   sudo systemctl status saro

   Option B - If using supervisor:
   sudo supervisorctl restart saro
   sudo supervisorctl status saro

   Option C - If running manually:
   pkill -f gunicorn
   gunicorn --config gunicorn.conf.py app:app --daemon

5. Check logs if service doesn't start:
   ─────────────────────────────────────────────────────────────
   Option A - systemd logs:
   sudo journalctl -u saro -n 50 -f

   Option B - supervisor logs:
   tail -f /var/log/supervisor/saro-stdout.log

   Option C - application logs:
   tail -f /path/to/saro/logs/app.log

6. Clear browser cache on all devices:
   ─────────────────────────────────────────────────────────────
   • Press Ctrl+Shift+Delete (Windows/Linux)
   • Press Cmd+Shift+Delete (Mac)
   • Select "Cached images and files"
   • Click "Clear data"
   • Hard refresh: Ctrl+Shift+R or Cmd+Shift+R

7. Test the features:
   ─────────────────────────────────────────────────────────────
   • Open https://gsteaching.com
   • Login as student (phone: 01732345678, password: 5678)
   • Click "Monthly Exams" - should load exam list immediately
   • Click "Online Resources" - should load documents immediately
   • Open browser DevTools (F12) → Console tab
   • Check for console messages:
     ✓ "Showing section: monthly-exams"
     ✓ "Monthly Exams section activated"
     ✓ "Loading documents..."

════════════════════════════════════════════════════════════════

🔍 TROUBLESHOOTING:

Problem: Service won't start
──────────────────────────────────────────────────────────────
• Check logs: sudo journalctl -u saro -n 50
• Check Python errors: python app.py (to test manually)
• Check port conflicts: sudo lsof -i :5000

Problem: Still showing old version
──────────────────────────────────────────────────────────────
• Verify deployment: git log --oneline -1
  Should show: 567bf81 Fix student dashboard
• Clear browser cache completely (all data, not just cache)
• Try in Incognito/Private browsing mode
• Check if service restarted: sudo systemctl status saro

Problem: Features still not loading
──────────────────────────────────────────────────────────────
• Open DevTools Console (F12)
• Look for JavaScript errors (red messages)
• Check if showing: "studentMonthlyExams is not defined"
  → This means old cached JavaScript is loaded
  → Clear ALL browser data, not just cache
• Check if showing: "Failed to fetch"
  → Check VPS API routes are working
  → Test: curl http://localhost:5000/api/students/me/batches

════════════════════════════════════════════════════════════════

✅ COMMITS TO BE DEPLOYED:

567bf81 - Fix student dashboard: Add explicit section loading triggers
f04247b - Fix student dashboard: Improve Monthly Exams loading
e7864f2 - Implement full read-only monthly exam details view
b12131b - Fix: Allow students to enroll in multiple batches
e39096b - Fix Excel export: Phone numbers and headers
291bb29 - Update homepage: Teacher experience and developer credit

ALL COMMITS READY ON GITHUB!

════════════════════════════════════════════════════════════════

INSTRUCTIONS

echo "✅ All changes are committed and pushed to GitHub"
echo "📦 Ready for VPS deployment"
echo ""
echo "⚠️  IMPORTANT: You must deploy to VPS for changes to take effect!"
echo "    The gsteaching.com site won't update until you pull on the server"
echo ""
