#!/bin/bash
# Update service to use smartgardenhub.db database

echo "🔧 Updating service to use smartgardenhub.db..."

# Stop the service
sudo systemctl stop saro

# Create service file with DATABASE_URL (absolute path with 4 slashes)
sudo tee /etc/systemd/system/saro.service > /dev/null << 'EOF'
[Unit]
Description=Saro Student Management System
After=network.target

[Service]
Type=exec
User=root
WorkingDirectory=/var/www/saroyarsir
Environment="PATH=/var/www/saroyarsir/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="DATABASE_URL=sqlite:////var/www/saroyarsir/instance/smartgardenhub.db"
ExecStart=/var/www/saroyarsir/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8001 --timeout 120 --access-logfile - --error-logfile - wsgi:app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file updated with absolute DATABASE_URL"

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable saro

# Check if smartgardenhub.db exists, if not copy from saro.db
SMART_DB="/var/www/saroyarsir/instance/smartgardenhub.db"
SARO_DB="/var/www/saroyarsir/instance/saro.db"

mkdir -p /var/www/saroyarsir/instance

if [ ! -f "$SMART_DB" ] && [ -f "$SARO_DB" ]; then
    echo "📋 Copying saro.db to smartgardenhub.db..."
    cp "$SARO_DB" "$SMART_DB"
    echo "✅ Database copied"
elif [ -f "$SMART_DB" ]; then
    echo "✅ smartgardenhub.db already exists"
else
    echo "⚠️  No database found, will be created on first run"
fi

# Start service
echo "▶️  Starting service..."
sudo systemctl start saro

sleep 3

# Check status
sudo systemctl status saro --no-pager -l

echo ""
echo "=========================================="
echo "✅ Service updated to use smartgardenhub.db"
echo "📂 Database location: /var/www/saroyarsir/instance/smartgardenhub.db"
echo ""
echo "🌐 Site: https://gsteaching.com"
