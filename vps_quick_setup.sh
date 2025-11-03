#!/bin/bash
# ========================================
# SARO Education Management System
# Quick VPS Setup Script
# ========================================
# This script automates the VPS deployment process
# Run on Ubuntu/Debian VPS with: sudo bash vps_quick_setup.sh

set -e  # Exit on error

echo "========================================="
echo "SARO Education System - VPS Setup"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root: sudo bash vps_quick_setup.sh"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
apt install -y python3 python3-pip python3-venv git nginx sqlite3 curl

# Create application directory
APP_DIR="/var/www/saro"
echo "📁 Setting up application directory: $APP_DIR"

if [ -d "$APP_DIR" ]; then
    echo "⚠️  Directory exists. Backing up..."
    mv "$APP_DIR" "${APP_DIR}.backup.$(date +%Y%m%d%H%M%S)"
fi

# Clone repository
echo "📥 Cloning repository..."
cd /var/www
git clone https://github.com/8ytgggygt/saro.git
cd saro

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Setup environment file
echo "⚙️  Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    # Generate secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/CHANGE_THIS_TO_A_SECURE_RANDOM_KEY_GENERATE_WITH_PYTHON/$SECRET_KEY/" .env
    echo "✅ Generated secure SECRET_KEY"
else
    echo "⚠️  .env file already exists, skipping..."
fi

# Create required directories
echo "📁 Creating upload directories..."
mkdir -p uploads/documents
mkdir -p static/uploads
mkdir -p instance

# Initialize database
echo "🗄️  Initializing SQLite database..."
python3 setup_sqlite.py

# Create default users
echo "👥 Creating default users..."
python3 create_default_users.py

# Set permissions
echo "🔐 Setting permissions..."
chown -R www-data:www-data "$APP_DIR"
chmod -R 755 "$APP_DIR"
chmod 644 instance/app.db
chmod 755 instance

# Create systemd service
echo "⚙️  Creating systemd service..."
cat > /etc/systemd/system/saro.service << 'EOF'
[Unit]
Description=SARO Education Management System
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/saro
Environment="PATH=/var/www/saro/venv/bin"
ExecStart=/var/www/saro/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "🚀 Starting SARO service..."
systemctl daemon-reload
systemctl enable saro
systemctl start saro

# Check service status
sleep 2
if systemctl is-active --quiet saro; then
    echo "✅ SARO service started successfully"
else
    echo "❌ SARO service failed to start. Check logs: journalctl -u saro -n 50"
    exit 1
fi

# Configure Nginx
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/saro << 'EOF'
server {
    listen 80;
    server_name _;  # Change this to your domain
    
    client_max_body_size 64M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    location /static {
        alias /var/www/saro/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /uploads {
        alias /var/www/saro/uploads;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/saro /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
nginx -t
systemctl restart nginx
systemctl enable nginx

# Configure firewall
echo "🔥 Configuring firewall..."
ufw --force enable
ufw allow OpenSSH
ufw allow 'Nginx Full'

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

echo ""
echo "========================================="
echo "✅ Installation Complete!"
echo "========================================="
echo ""
echo "📊 System Information:"
echo "   • Application: SARO Education Management System"
echo "   • Location: $APP_DIR"
echo "   • Service: saro.service (active)"
echo "   • Database: SQLite (instance/app.db)"
echo "   • Web Server: Nginx"
echo ""
echo "🌐 Access your application:"
echo "   • URL: http://$SERVER_IP"
echo "   • Or: http://your-domain.com (if DNS configured)"
echo ""
echo "🔑 Default Login Credentials:"
echo "   Admin:   username: admin    password: admin123"
echo "   Teacher: username: teacher  password: teacher123"
echo "   Student: username: student  password: student123"
echo ""
echo "⚠️  IMPORTANT SECURITY STEPS:"
echo "   1. Change all default passwords immediately"
echo "   2. Update server_name in /etc/nginx/sites-available/saro"
echo "   3. Setup SSL certificate: certbot --nginx -d your-domain.com"
echo ""
echo "📖 Useful Commands:"
echo "   • View logs:        journalctl -u saro -f"
echo "   • Restart app:      systemctl restart saro"
echo "   • Check status:     systemctl status saro"
echo "   • Update code:      cd $APP_DIR && git pull && systemctl restart saro"
echo ""
echo "📚 Documentation: $APP_DIR/VPS_DEPLOYMENT_GUIDE.md"
echo "========================================="
