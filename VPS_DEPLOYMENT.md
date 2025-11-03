# VPS Production Deployment Guide

## 🚀 Quick Deploy (Copy-Paste Commands)

Run these commands line-by-line on your VPS:

```bash
# 1. Navigate to project directory
cd /var/www/saroyarsir

# 2. Stop any running servers
pkill -f "flask run" || true
pkill -f "python run.py" || true
pkill -f "gunicorn" || true

# 3. Pull latest code
git pull origin main

# 4. Activate virtual environment
source venv/bin/activate

# 5. Update pip
pip install --upgrade pip

# 6. Install dependencies
pip install -r requirements.txt
pip install gunicorn

# 7. Copy .env file from GitHub (if not exists)
if [ ! -f .env ]; then cp .env.example .env; fi

# 8. Edit .env with your API keys
nano .env

# 9. Initialize database (creates default users)
python create_default_users.py

# 10. Start with gunicorn (production server)
gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 120 "app:create_app()"
```

## 📋 One-Line Deployment Script

Or use the automated deployment script:

```bash
# Make script executable
chmod +x deploy_vps.sh

# Run deployment script
./deploy_vps.sh
```

## 🔧 Manual Configuration

### .env File Setup

Edit your `.env` file with actual values:

```bash
nano .env
```

Replace these placeholders:
- `your_google_gemini_api_key_here` → Your Google Gemini API key (optional)

**Note**: SMS API is hardcoded in the application - no configuration needed!

### Database Setup

**SQLite (Default - Recommended for VPS)**
```bash
# No setup needed! Database auto-creates on first run
# Location: /var/www/saroyarsir/smartgardenhub.db
```

**MySQL (Alternative)**
```bash
# Install MySQL
sudo apt update
sudo apt install mysql-server -y

# Secure MySQL
sudo mysql_secure_installation

# Create database
sudo mysql -e "CREATE DATABASE smartgardenhub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER 'saro'@'localhost' IDENTIFIED BY 'your_password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON smartgardenhub.* TO 'saro'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Update .env file
nano .env
# Uncomment MySQL lines and set credentials
```

## 🔄 Systemd Service Setup (Recommended)

Create service file:

```bash
sudo nano /etc/systemd/system/saro.service
```

Paste this configuration:

```ini
[Unit]
Description=SmartGardenHub Flask Application
After=network.target

[Service]
Type=notify
User=root
WorkingDirectory=/var/www/saroyarsir
Environment="PATH=/var/www/saroyarsir/venv/bin"
ExecStart=/var/www/saroyarsir/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 120 --access-logfile - --error-logfile - "app:create_app()"
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable saro
sudo systemctl start saro
sudo systemctl status saro
```

## 📊 Service Management Commands

```bash
# Start service
sudo systemctl start saro

# Stop service
sudo systemctl stop saro

# Restart service
sudo systemctl restart saro

# Check status
sudo systemctl status saro

# View live logs
sudo journalctl -u saro -f

# View recent logs
sudo journalctl -u saro -n 100
```

## 🌐 Nginx Reverse Proxy (Recommended)

Install Nginx:

```bash
sudo apt update
sudo apt install nginx -y
```

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/saro
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP

    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 120;
        proxy_send_timeout 120;
        proxy_read_timeout 120;
    }

    location /static {
        alias /var/www/saroyarsir/static;
        expires 30d;
    }
}
```

Enable and test:

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/saro /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## 🔐 SSL/HTTPS with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

## 🔥 Firewall Configuration

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Flask port (if not using Nginx)
sudo ufw allow 5000/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

## 🔄 Update Deployment (Pull New Changes)

```bash
cd /var/www/saroyarsir
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart saro
```

## 🐛 Troubleshooting

### Service won't start

```bash
# Check service status
sudo systemctl status saro

# View detailed logs
sudo journalctl -u saro -n 50

# Check for port conflicts
sudo netstat -tulpn | grep 5000

# Test manually
cd /var/www/saroyarsir
source venv/bin/activate
python run.py
```

### Database issues

```bash
# Check database file exists
ls -lah smartgardenhub.db

# Reset database (WARNING: deletes all data)
rm smartgardenhub.db
python run.py  # Auto-creates new database
python create_default_users.py
```

### Permission issues

```bash
# Fix ownership
sudo chown -R root:root /var/www/saroyarsir

# Fix permissions
chmod +x deploy_vps.sh
chmod 600 .env
```

## 📱 Default Login Credentials

After running `create_default_users.py`:

- **Super User**: Phone: `01712345678`, Password: `admin123`
- **Teacher**: Phone: `01812345678`, Password: `teacher123`
- **Student**: Phone: `01912345678`, Password: `student123`

## 🎯 Performance Tuning

### Gunicorn Workers

Recommended workers formula: `(2 x CPU_cores) + 1`

```bash
# Check CPU cores
nproc

# Update service file with optimal workers
sudo nano /etc/systemd/system/saro.service
# Change --workers value
```

### Database Optimization

For high traffic, consider switching to MySQL:

```bash
# Edit .env
nano .env

# Uncomment and configure MySQL settings
# Then restart service
sudo systemctl restart saro
```

## 📊 Monitoring

### Check application health

```bash
curl http://localhost:5000/health
```

### Monitor resource usage

```bash
# CPU and Memory
top

# Disk space
df -h

# Service resource usage
systemctl status saro
```

## 🔄 Backup

### SQLite Database Backup

```bash
# Create backup directory
mkdir -p /var/www/saroyarsir/backups

# Backup database
cp smartgardenhub.db backups/smartgardenhub_$(date +%Y%m%d_%H%M%S).db

# Automated daily backup (crontab)
crontab -e
# Add: 0 2 * * * cp /var/www/saroyarsir/smartgardenhub.db /var/www/saroyarsir/backups/smartgardenhub_$(date +\%Y\%m\%d).db
```

### Full Application Backup

```bash
# Backup entire application
tar -czf saro_backup_$(date +%Y%m%d).tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    /var/www/saroyarsir
```

---

## 📞 Support

For issues:
1. Check logs: `sudo journalctl -u saro -f`
2. Review [DATABASE_SETUP.md](DATABASE_SETUP.md)
3. Open GitHub issue: https://github.com/8ytgggygt/saro/issues

---

**Last Updated**: October 19, 2025  
**Production Database**: SQLite (smartgardenhub.db)  
**Web Server**: Gunicorn + Nginx  
**VPS Path**: /var/www/saroyarsir
