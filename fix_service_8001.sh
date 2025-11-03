#!/bin/bash
# Fix service to run on port 8001

echo "🔧 Configuring service for port 8001..."

# Stop the service
sudo systemctl stop saro 2>/dev/null || true

# Kill any processes on port 8001
sudo fuser -k 8001/tcp 2>/dev/null || true
sudo pkill -9 gunicorn 2>/dev/null || true

# Reload systemd daemon
sudo systemctl daemon-reload

# Create service file for port 8001
sudo tee /etc/systemd/system/saro.service > /dev/null << 'EOF'
[Unit]
Description=Saro Student Management System
After=network.target

[Service]
Type=exec
User=root
WorkingDirectory=/var/www/saroyarsir
Environment="PATH=/var/www/saroyarsir/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/var/www/saroyarsir/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8001 --timeout 120 --access-logfile - --error-logfile - wsgi:app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created for port 8001"

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable the service
sudo systemctl enable saro

echo "✅ Service enabled"

# Test if we can import the app
echo ""
echo "🧪 Testing application..."
cd /var/www/saroyarsir
source venv/bin/activate

# Quick test
python3 -c "from wsgi import app; print('✅ App imports successfully')" 2>&1

# Start the service
echo ""
echo "🚀 Starting service..."
sudo systemctl start saro

# Wait a moment
sleep 3

# Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status saro --no-pager -l

echo ""
echo "🌐 Application should be running on: http://YOUR_IP:8001"
echo ""
echo "📝 To view logs: sudo journalctl -u saro -f"
echo "📝 To restart: sudo systemctl restart saro"
