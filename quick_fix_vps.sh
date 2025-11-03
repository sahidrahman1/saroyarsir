#!/bin/bash
# Quick fix for VPS database issues

echo "=================================================="
echo "VPS Database Fix Script"
echo "=================================================="

# Check if database exists
if [ ! -f "instance/app.db" ]; then
    echo "❌ Database file not found at instance/app.db"
    exit 1
fi

echo "✅ Database file found"

# Backup database first
echo "📦 Creating backup..."
cp instance/app.db instance/app.db.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"

# Check fees table schema
echo ""
echo "📋 Checking fees table schema..."
sqlite3 instance/app.db "PRAGMA table_info(fees);" | grep -E "exam|others"

# Check if 'exam' column exists (without '_fee' suffix)
HAS_EXAM=$(sqlite3 instance/app.db "PRAGMA table_info(fees);" | grep -c "exam|")
HAS_EXAM_FEE=$(sqlite3 instance/app.db "PRAGMA table_info(fees);" | grep -c "exam_fee|")

echo ""
echo "Diagnosis:"
echo "  - 'exam' column exists: $([ $HAS_EXAM -gt $HAS_EXAM_FEE ] && echo 'YES ⚠️' || echo 'NO ✅')"
echo "  - 'exam_fee' column exists: $([ $HAS_EXAM_FEE -gt 0 ] && echo 'YES ✅' || echo 'NO ⚠️')"

# Run Python fix script
echo ""
echo "🔧 Running Python fix script..."
python3 fix_vps_issues.py

# Restart application
echo ""
echo "🔄 To apply changes, restart your application:"
echo "   sudo systemctl restart your-app-service"
echo "   OR"
echo "   pkill -f gunicorn && gunicorn ..."

echo ""
echo "=================================================="
echo "✅ Fix script completed!"
echo "=================================================="
