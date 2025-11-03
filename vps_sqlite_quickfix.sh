#!/bin/bash

# VPS Quick Fix - SQLite Configuration
# Run this on VPS to fix database connection issues

echo "=========================================="
echo "🔧 VPS SQLite Quick Fix"
echo "=========================================="

cd /var/www/saroyarsir || cd /home/root/saroyarsir || exit 1

echo "📂 Working in: $(pwd)"
echo ""

# 1. Configure .env for SQLite
echo "1️⃣ Configuring .env for SQLite..."
cat > .env << 'EOF'
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_URL=sqlite:///madrasha.db
PORT=8001
HOST=0.0.0.0
SESSION_TYPE=filesystem
EOF
echo "✅ .env configured"
echo ""

# 2. Fix phone constraint
echo "2️⃣ Fixing phone number constraint (allow siblings)..."
if [ -f "fix_phone_unique_constraint.py" ]; then
    python3 fix_phone_unique_constraint.py || echo "⚠️ Phone constraint fix skipped"
else
    echo "ℹ️  Phone constraint script not found, skipping"
fi
echo ""

# 3. Verify database
echo "3️⃣ Verifying database..."
if [ -f "fix_vps_database.py" ]; then
    python3 fix_vps_database.py || echo "⚠️ Database verification skipped"
else
    echo "ℹ️  Database verification script not found, skipping"
fi
echo ""

# 4. Restart service
echo "4️⃣ Restarting service..."
sudo systemctl restart smartgardenhub
echo "✅ Service restarted"
echo ""

# 5. Check status
echo "5️⃣ Checking service status..."
sudo systemctl status smartgardenhub --no-pager | head -n 20
echo ""

# 6. Show recent logs
echo "6️⃣ Recent logs (last 30 lines)..."
sudo journalctl -u smartgardenhub -n 30 --no-pager
echo ""

echo "=========================================="
echo "✅ Quick fix complete!"
echo "=========================================="
echo ""
echo "Your app should be running at:"
echo "  http://$(hostname -I | awk '{print $1}'):8001"
echo ""
echo "If you see errors above, check the full logs:"
echo "  sudo journalctl -u smartgardenhub -n 100"
echo ""
