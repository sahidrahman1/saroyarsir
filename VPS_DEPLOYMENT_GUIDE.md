# 🚀 VPS Deployment Guide for SARO Education Management System

## Prerequisites
- Ubuntu/Debian VPS (20.04 or later recommended)
- SSH access to your VPS
- Domain name pointed to your VPS IP (optional but recommended)
- At least 1GB RAM and 10GB storage

## Step 1: Clone Repository on VPS

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Install git if not already installed
apt update
apt install -y git

# Clone the repository
cd /var/www
git clone https://github.com/8ytgggygt/saro.git
cd saro
```

## Step 2: Install Dependencies

```bash
# Install Python 3 and pip
apt install -y python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Install Gunicorn for production
pip install gunicorn
```

## Step 3: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file
nano .env
```

Update the following values in `.env`:
```bash
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-very-secure-random-secret-key-here  # Generate a strong key!
HOST=0.0.0.0
PORT=5000
```

To generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Step 4: Initialize Database

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Run database initialization
python3 setup_sqlite.py

# Or use the init script
python3 init_db.py

# Create default admin user (optional)
python3 create_default_users.py
```

## Step 5: Create Required Directories

```bash
# Create upload directories
mkdir -p uploads/documents
mkdir -p static/uploads
mkdir -p instance

# Set proper permissions
chmod -R 755 uploads
chmod -R 755 static/uploads
chmod 755 instance
chmod 644 instance/app.db
```

## Step 6: Test the Application

```bash
# Test with Flask development server first
python3 app.py

# Or test with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Access: `http://your-vps-ip:5000`

## Step 7: Setup Systemd Service (Production)

Create a systemd service file:

```bash
nano /etc/systemd/system/saro.service
```

Add the following content:

```ini
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
```

Set proper permissions and start the service:

```bash
# Set ownership
chown -R www-data:www-data /var/www/saro

# Reload systemd
systemctl daemon-reload

# Enable service to start on boot
systemctl enable saro

# Start the service
systemctl start saro

# Check status
systemctl status saro
```

## Step 8: Setup Nginx Reverse Proxy

```bash
# Install Nginx
apt install -y nginx

# Create Nginx configuration
nano /etc/nginx/sites-available/saro
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Change to your domain
    
    client_max_body_size 64M;  # Allow PDF uploads up to 64MB
    
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
```

Enable the site and restart Nginx:

```bash
# Create symbolic link
ln -s /etc/nginx/sites-available/saro /etc/nginx/sites-enabled/

# Remove default site
rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

## Step 9: Setup SSL Certificate (Optional but Recommended)

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is configured automatically
```

## Step 10: Configure Firewall

```bash
# Allow SSH, HTTP, and HTTPS
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
ufw status
```

## Common Management Commands

```bash
# Check application logs
journalctl -u saro -f

# Restart the application
systemctl restart saro

# Pull latest changes from GitHub
cd /var/www/saro
git pull origin main
systemctl restart saro

# Backup database
cp instance/app.db instance/app.db.backup-$(date +%Y%m%d)

# View Nginx access logs
tail -f /var/log/nginx/access.log

# View Nginx error logs
tail -f /var/log/nginx/error.log
```

## Default Login Credentials

After running `create_default_users.py`:

**Admin:**
- Username: `admin`
- Password: `admin123`

**Teacher:**
- Username: `teacher`
- Password: `teacher123`

**Student:**
- Username: `student`
- Password: `student123`

⚠️ **IMPORTANT:** Change these passwords immediately after first login!

## Troubleshooting

### Application won't start
```bash
# Check logs
journalctl -u saro -n 50

# Check if port 5000 is in use
netstat -tuln | grep 5000

# Verify database exists
ls -lh instance/app.db
```

### Permission issues
```bash
# Fix ownership
chown -R www-data:www-data /var/www/saro

# Fix permissions
chmod -R 755 /var/www/saro
chmod 644 instance/app.db
```

### Database locked error
```bash
# Stop the service
systemctl stop saro

# Check for processes using the database
lsof | grep app.db

# Restart the service
systemctl start saro
```

## Updating the Application

```bash
# Stop the service
systemctl stop saro

# Backup database
cp instance/app.db instance/app.db.backup-$(date +%Y%m%d)

# Pull latest changes
cd /var/www/saro
git pull origin main

# Install any new dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run any new migrations (if needed)
python3 migrate_database.py

# Restart the service
systemctl start saro
```

## Performance Optimization

For better performance on production:

1. **Increase Gunicorn workers** (in `gunicorn.conf.py`):
   ```python
   workers = (CPU_cores * 2) + 1
   ```

2. **Enable Nginx caching**:
   ```nginx
   proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;
   ```

3. **Database optimization**:
   ```bash
   # Vacuum database periodically
   sqlite3 instance/app.db "VACUUM;"
   ```

## Security Recommendations

1. Change SECRET_KEY to a strong random value
2. Change all default passwords immediately
3. Keep system and packages updated: `apt update && apt upgrade`
4. Enable firewall (UFW)
5. Use SSL/HTTPS (Certbot)
6. Regular database backups
7. Monitor logs regularly
8. Disable debug mode in production

## Support

For issues or questions:
- Check logs: `journalctl -u saro -f`
- Review this guide
- Check application logs in the working directory

---

**Deployment Date:** $(date +%Y-%m-%d)
**Version:** 1.0.0
