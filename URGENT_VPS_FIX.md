# 🚨 URGENT VPS FIX - MySQL to SQLite

## Problem
The VPS is still trying to use MySQL instead of SQLite, causing "Access denied" errors.

## Solution
Run these commands **on your VPS** (SSH into it):

```bash
# Navigate to project directory
cd /var/www/saroyarsir

# Backup old .env (just in case)
cp .env .env.backup.mysql

# Force update .env from GitHub
git checkout main -- .env

# OR manually replace it:
cat > .env << 'EOF'
# Flask Environment Configuration - VPS PRODUCTION
FLASK_ENV=production
FLASK_APP=app.py
DEBUG=False
SECRET_KEY=da518faf7721332786bca402bf8ff796eb5a257bfc9152c8318e3e599930b52c

# SERVER CONFIGURATION
HOST=0.0.0.0
PORT=5000

# DATABASE CONFIGURATION - SQLITE ONLY
DATABASE_URL=sqlite:///smartgardenhub.db

# SMS API CONFIGURATION
# SMS API is HARDCODED in routes/sms.py - works automatically

# AI/GOOGLE GEMINI API CONFIGURATION (OPTIONAL)
GOOGLE_API_KEY=

# FILE UPLOAD SETTINGS
MAX_UPLOAD_SIZE=16777216
UPLOAD_FOLDER=static/uploads

# SESSION SETTINGS
SESSION_TYPE=filesystem
SESSION_PERMANENT=false
SESSION_FILE_THRESHOLD=500

# LOGGING CONFIGURATION
LOG_LEVEL=info
ERROR_LOG=-
ACCESS_LOG=-
EOF

# Verify the file is correct
grep "DATABASE_URL" .env
# Should show: DATABASE_URL=sqlite:///smartgardenhub.db
# Should NOT show any mysql:// or MYSQL_ variables

# Restart the service
sudo systemctl restart saro

# Check status
sudo systemctl status saro

# Watch logs to confirm it works
sudo journalctl -u saro -f
```

## What Happened?
- Your VPS had an old `.env` file with MySQL configuration
- When you did `git pull`, Git didn't overwrite it (local changes)
- The app kept trying to connect to MySQL (which isn't installed)
- This fix forces the SQLite configuration

## After Fix
You should see:
- ✅ No more MySQL connection errors
- ✅ Application starts successfully
- ✅ SQLite database created at `/var/www/saroyarsir/smartgardenhub.db`
- ✅ Website works properly

## Quick Verification
```bash
# Check if SQLite database was created
ls -lh /var/www/saroyarsir/smartgardenhub.db

# Check application logs
sudo journalctl -u saro -n 50 --no-pager
```

If you still see MySQL errors after this, it means the .env file is not being loaded correctly. Let me know!
