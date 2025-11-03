#!/bin/bash
# Copy madrasha database and fix permissions

echo "🔄 Copying Database from Madrasha"
echo "=================================="

SOURCE_DB="/var/www/madrasha/smartgardenhub.db"
DEST_DB="/var/www/saroyarsir/instance/smartgardenhub.db"
BACKUP_DIR="/var/www/saroyarsir/backups"

# Create directories
mkdir -p /var/www/saroyarsir/instance
mkdir -p "$BACKUP_DIR"

# Backup current if exists
if [ -f "$DEST_DB" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp "$DEST_DB" "$BACKUP_DIR/smartgardenhub_backup_$TIMESTAMP.db"
    echo "✅ Current database backed up"
fi

# Check source
if [ -f "$SOURCE_DB" ]; then
    echo "📋 Copying from: $SOURCE_DB"
    echo "📋 Copying to: $DEST_DB"
    
    # Stop service
    sudo systemctl stop saro
    
    # Copy database
    cp "$SOURCE_DB" "$DEST_DB"
    
    # Fix permissions - CRITICAL!
    chown root:root "$DEST_DB"
    chmod 664 "$DEST_DB"
    
    # Fix instance directory permissions
    chown -R root:root /var/www/saroyarsir/instance
    chmod 775 /var/www/saroyarsir/instance
    
    echo "✅ Database copied"
    echo "✅ Permissions fixed"
    
    # Check database
    echo ""
    echo "📊 Database info:"
    ls -lh "$DEST_DB"
    
    # Initialize SMS balance
    echo ""
    echo "🔧 Initializing SMS balance..."
    cd /var/www/saroyarsir
    source venv/bin/activate
    echo "y" | python3 init_sms_balance.py 2>&1 | tail -5
    
    # Start service
    echo ""
    echo "▶️  Starting service..."
    sudo systemctl start saro
    sleep 3
    
    echo ""
    echo "=================================="
    echo "✅ Database restored successfully!"
    echo ""
    echo "📂 Database: $DEST_DB"
    echo "🌐 Site: https://gsteaching.com"
    echo ""
    
    # Check status
    sudo systemctl status saro --no-pager -l | grep -A 5 "Active:"
    
else
    echo "❌ Source not found: $SOURCE_DB"
    echo ""
    echo "Available databases:"
    find /var/www -name "*.db" 2>/dev/null
fi
