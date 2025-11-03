#!/bin/bash
# Restore previous SQLite database

echo "🔄 Database Restoration Script"
echo "=============================="

DB_PATH="/var/www/saroyarsir/instance/saro.db"
BACKUP_DIR="/var/www/saroyarsir/backups"

# Create backups directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo ""
echo "Current database location: $DB_PATH"
echo ""

# Check if database exists
if [ -f "$DB_PATH" ]; then
    # Backup current database
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/saro_backup_$TIMESTAMP.db"
    
    echo "📦 Backing up current database to: $BACKUP_FILE"
    cp "$DB_PATH" "$BACKUP_FILE"
    echo "✅ Current database backed up"
else
    echo "⚠️  No existing database found at $DB_PATH"
fi

echo ""
echo "Available options:"
echo "1. Restore from madrasha database (if exists)"
echo "2. Restore from a specific backup file"
echo "3. Initialize fresh database with SMS balance"
echo ""

# Check if madrasha database exists
MADRASHA_DB="/var/www/madrasha/instance/saro.db"
if [ -f "$MADRASHA_DB" ]; then
    echo "✅ Found previous database at: $MADRASHA_DB"
    echo ""
    read -p "Do you want to copy from madrasha database? (y/n): " choice
    
    if [ "$choice" == "y" ] || [ "$choice" == "Y" ]; then
        echo "📋 Copying database from madrasha..."
        
        # Stop the service
        sudo systemctl stop saro
        
        # Copy the database
        cp "$MADRASHA_DB" "$DB_PATH"
        
        # Set proper permissions
        chown root:root "$DB_PATH"
        chmod 644 "$DB_PATH"
        
        echo "✅ Database copied successfully"
        
        # Initialize SMS balance in the restored database
        echo ""
        echo "🔧 Initializing SMS balance in restored database..."
        cd /var/www/saroyarsir
        source venv/bin/activate
        python3 init_sms_balance.py <<EOF
y
EOF
        
        # Start the service
        sudo systemctl start saro
        sleep 2
        sudo systemctl status saro --no-pager -l
        
        echo ""
        echo "=============================="
        echo "✅ Database restoration complete!"
        echo "🌐 Visit: https://gsteaching.com"
    else
        echo "❌ Restoration cancelled"
    fi
else
    echo "⚠️  Madrasha database not found at: $MADRASHA_DB"
    echo ""
    echo "📝 Manual restoration steps:"
    echo "1. Find your old database file (saro.db)"
    echo "2. Copy it to: $DB_PATH"
    echo "3. Run: sudo systemctl restart saro"
fi

echo ""
echo "📂 Available backups:"
ls -lh "$BACKUP_DIR/" 2>/dev/null || echo "No backups found"
