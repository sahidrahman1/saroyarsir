#!/bin/bash
# Fix the CORRECT database (in instance/ folder)

echo "=================================================="
echo "🔧 Fixing the CORRECT Database"
echo "=================================================="

# The ACTIVE database is in instance/ folder
DB_PATH="/var/www/saroyarsir/instance/smartgardenhub.db"

echo "📁 Using database: $DB_PATH"

# 1. Backup
echo ""
echo "📦 Creating backup..."
cp "$DB_PATH" "$DB_PATH.backup.$(date +%Y%m%d_%H%M%S)"
echo "✅ Backup created"

# 2. Check current schema
echo ""
echo "📋 Current fees table columns with 'exam' or 'others':"
sqlite3 "$DB_PATH" "PRAGMA table_info(fees);" | grep -E "exam|others"

# 3. Fix the fees table
echo ""
echo "🔧 Adding missing columns..."
sqlite3 "$DB_PATH" <<EOF
-- Add exam_fee if missing
ALTER TABLE fees ADD COLUMN exam_fee NUMERIC(10, 2) DEFAULT 0.00;
-- Add others_fee if missing
ALTER TABLE fees ADD COLUMN others_fee NUMERIC(10, 2) DEFAULT 0.00;
EOF

echo ""
echo "✅ Columns added (errors above are normal if columns already exist)"

# 4. Verify
echo ""
echo "📋 Updated fees table columns:"
sqlite3 "$DB_PATH" "PRAGMA table_info(fees);" | grep -E "exam|others"

# 5. Fix permissions
echo ""
echo "🔒 Fixing file permissions..."
chown www-data:www-data "$DB_PATH"
chmod 664 "$DB_PATH"
echo "✅ Permissions fixed"

echo ""
echo "=================================================="
echo "✅ Database fixed!"
echo "=================================================="
echo ""
echo "Now restart the service:"
echo "  sudo systemctl restart saro"
