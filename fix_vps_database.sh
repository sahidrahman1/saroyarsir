#!/bin/bash
# ========================================
# Fix VPS Database - Run Migrations & Reset Student Passwords
# ========================================
# Run this script on your VPS to fix the database issues

set -e  # Exit on error

echo "========================================="
echo "Fixing VPS Database"
echo "========================================="
echo ""

# Navigate to app directory
cd /var/www/saroyarsir || cd /var/www/saro

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Run migrations
echo ""
echo "🗄️  Running database migrations..."
echo ""

echo "1️⃣  Adding archive fields..."
python3 migrate_add_archive_fields.py

echo ""
echo "2️⃣  Adding mother_name field..."
python3 migrate_add_mother_name.py

echo ""
echo "3️⃣  Adding documents table..."
python3 migrate_add_documents.py

echo ""
echo "🔐 Resetting student passwords to phone last 4 digits..."
python3 reset_all_student_passwords.py

echo ""
echo "========================================="
echo "✅ Database Fixed Successfully!"
echo "========================================="
echo ""
echo "📝 Students can now login with:"
echo "   Phone: their full phone number"
echo "   Password: last 4 digits of phone"
echo ""
echo "🔄 Restarting service..."
sudo systemctl restart saro

echo ""
echo "✅ Service restarted. Check status:"
sudo systemctl status saro --no-pager -l

echo ""
echo "========================================="
echo "All done! 🎉"
echo "========================================="
