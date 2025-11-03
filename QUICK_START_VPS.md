# 🚀 Quick Start - Deploy to VPS in 5 Minutes

## Automated Deployment (Recommended)

### Option 1: One-Command Setup

SSH into your VPS and run:

```bash
curl -sSL https://raw.githubusercontent.com/8ytgggygt/saro/main/vps_quick_setup.sh | sudo bash
```

### Option 2: Manual Download

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Download setup script
wget https://raw.githubusercontent.com/8ytgggygt/saro/main/vps_quick_setup.sh

# Make executable
chmod +x vps_quick_setup.sh

# Run setup
sudo bash vps_quick_setup.sh
```

**That's it!** The script will:
- ✅ Install all dependencies (Python, Nginx, etc.)
- ✅ Clone the repository
- ✅ Setup virtual environment
- ✅ Configure database (SQLite)
- ✅ Create default users
- ✅ Setup systemd service
- ✅ Configure Nginx reverse proxy
- ✅ Setup firewall
- ✅ Start the application

After installation, access your app at: `http://your-vps-ip`

---

## Manual Deployment

If you prefer manual control, follow the detailed guide:

📖 **[VPS_DEPLOYMENT_GUIDE.md](VPS_DEPLOYMENT_GUIDE.md)**

---

## Default Login Credentials

After deployment, use these credentials:

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Teacher | `teacher` | `teacher123` |
| Student | `student` | `student123` |

⚠️ **Change these passwords immediately after first login!**

---

## Post-Deployment Steps

### 1. Update Domain (Optional)

Edit Nginx configuration:
```bash
nano /etc/nginx/sites-available/saro
```

Change `server_name _;` to your domain:
```nginx
server_name your-domain.com www.your-domain.com;
```

Restart Nginx:
```bash
systemctl restart nginx
```

### 2. Setup SSL Certificate (Recommended)

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 3. Change Default Passwords

1. Login as admin: `http://your-vps-ip`
2. Go to Settings → Change Password
3. Update all default user passwords

---

## Management Commands

```bash
# View application logs
journalctl -u saro -f

# Restart application
systemctl restart saro

# Check status
systemctl status saro

# Update from GitHub
cd /var/www/saro
git pull origin main
systemctl restart saro

# Backup database
cp /var/www/saro/instance/app.db /var/www/saro/instance/app.db.backup-$(date +%Y%m%d)
```

---

## Features

### For Teachers
- ✅ Student Management (Add, Edit, Archive)
- ✅ Batch Management (Create classes, assign students)
- ✅ Monthly Exams (Create exams, enter marks, rankings)
- ✅ Attendance System (Daily tracking, reports)
- ✅ Fee Management (Track payments, due amounts)
- ✅ SMS Notifications (Send to students/parents)
- ✅ **Online Resources (Upload PDFs, study materials)**
- ✅ AI Question Generator (Auto-generate questions)

### For Students
- ✅ View Monthly Exam Results
- ✅ View Attendance Records
- ✅ Check Fee Status
- ✅ **Download Study Resources (PDFs, books)**
- ✅ View Batch Information

### For Admins
- ✅ All teacher features
- ✅ Teacher management
- ✅ System settings
- ✅ SMS balance management
- ✅ Global configurations

---

## Technology Stack

- **Backend:** Flask 3.1.2 (Python)
- **Database:** SQLite (Production-ready)
- **Frontend:** Alpine.js, Tailwind CSS
- **Web Server:** Nginx (Reverse Proxy)
- **App Server:** Gunicorn
- **SMS API:** Pre-configured (bulksmsbd.net)
- **AI:** Google Gemini API (Optional)

---

## System Requirements

### Minimum
- **OS:** Ubuntu 20.04+ or Debian 10+
- **RAM:** 1GB
- **Storage:** 10GB
- **CPU:** 1 Core

### Recommended
- **RAM:** 2GB+
- **Storage:** 20GB+ SSD
- **CPU:** 2+ Cores

---

## Troubleshooting

### Application won't start

```bash
# Check logs
journalctl -u saro -n 50

# Check port
netstat -tuln | grep 5000

# Verify database
ls -lh /var/www/saro/instance/app.db
```

### Can't access from browser

```bash
# Check Nginx status
systemctl status nginx

# Check firewall
ufw status

# Test locally
curl http://localhost
```

### Database errors

```bash
# Check permissions
ls -lh /var/www/saro/instance/

# Fix ownership
chown -R www-data:www-data /var/www/saro

# Fix permissions
chmod 644 /var/www/saro/instance/app.db
```

### PDF upload fails

```bash
# Check upload directory
ls -lh /var/www/saro/uploads/documents/

# Fix permissions
chown -R www-data:www-data /var/www/saro/uploads
chmod -R 755 /var/www/saro/uploads

# Check Nginx client_max_body_size
grep client_max_body_size /etc/nginx/sites-available/saro
```

---

## Updating the Application

```bash
# Stop service
systemctl stop saro

# Backup database
cp /var/www/saro/instance/app.db /var/www/saro/instance/app.db.backup-$(date +%Y%m%d)

# Pull updates
cd /var/www/saro
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Start service
systemctl start saro

# Check status
systemctl status saro
```

---

## Security Checklist

- [ ] Changed SECRET_KEY in .env
- [ ] Changed all default passwords
- [ ] Enabled UFW firewall
- [ ] Installed SSL certificate (HTTPS)
- [ ] Updated Nginx server_name to your domain
- [ ] Regular database backups configured
- [ ] Monitoring/logging enabled
- [ ] Debug mode disabled (FLASK_ENV=production)

---

## Support & Documentation

- 📖 **Full Guide:** [VPS_DEPLOYMENT_GUIDE.md](VPS_DEPLOYMENT_GUIDE.md)
- 📖 **Features:** [DOCUMENT_MANAGEMENT_SYSTEM.md](DOCUMENT_MANAGEMENT_SYSTEM.md)
- 🔧 **Configuration:** Check `.env` file
- 📝 **Logs:** `journalctl -u saro -f`

---

## License

This project is for educational purposes.

---

**Deployed successfully? Enjoy your SARO Education Management System! 🎓**
