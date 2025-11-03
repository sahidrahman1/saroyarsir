# VPS Bug Fix Guide - Fees & Marks Update

## 🐛 Issues Fixed

### Issue 1: Fee Section Error
**Error:** `(sqlite3.OperationalError) no such column: fees.exam`

**Cause:** The VPS database may have an old or incorrect column name in the `fees` table. The column should be `exam_fee` but might be named just `exam` or be missing entirely.

**Solution:** The fix script will:
1. Check the current fees table schema
2. Rename `exam` to `exam_fee` if needed
3. Add missing `exam_fee` and `others_fee` columns if they don't exist

### Issue 2: Marks Update Not Working
**Error:** Marks entered in the Monthly Exam system don't save or update

**Cause:** Potential issues:
1. Permission issues on the database file
2. Session/authentication not working properly
3. SQLAlchemy not committing changes

**Solution:** The fix script will:
1. Verify database write permissions
2. Test the MonthlyMark table structure
3. Ensure proper indexing

## 📋 Prerequisites

Before running the fix, ensure:
- You have SSH access to your VPS
- Git is configured on your VPS
- Your Flask application is set up
- You have sudo access (for service restart)

## 🚀 Deployment Steps

### Step 1: Push Changes to Git

On your **LOCAL machine** (where you're developing):

```bash
# Navigate to your project directory
cd /path/to/saro

# Add all changes
git add .

# Commit with a descriptive message
git commit -m "Fix: Resolve fees table column error and marks update issue"

# Push to your repository
git push origin main
```

### Step 2: Deploy to VPS

On your **VPS server**:

```bash
# SSH into your VPS
ssh your-username@your-vps-ip

# Navigate to your application directory
cd /path/to/your/app

# Run the automated deployment script
./deploy_fix_to_vps.sh
```

The script will automatically:
1. Pull the latest code from Git
2. Create a database backup
3. Fix the database schema
4. Restart your application

### Step 3: Manual Deployment (Alternative)

If the automated script doesn't work, follow these manual steps:

```bash
# 1. Navigate to your app directory
cd /path/to/your/app

# 2. Pull latest code
git pull origin main

# 3. Backup database
cp instance/app.db instance/app.db.backup.$(date +%Y%m%d_%H%M%S)

# 4. Activate virtual environment
source venv/bin/activate  # or source .venv/bin/activate

# 5. Run fix script
python3 fix_vps_issues.py

# 6. Restart application
# Option A: If using systemd
sudo systemctl restart your-app-service

# Option B: If using supervisor
sudo supervisorctl restart your-app

# Option C: If using gunicorn directly
pkill -f "gunicorn.*app:app"
# Then start your app again with your usual command
```

## 🧪 Testing After Deployment

### Test 1: Fee Section
1. Log in as a teacher/admin
2. Navigate to **Fees** section
3. Select a batch from dropdown
4. Select academic year (2025)
5. **Expected:** Students should load without error
6. **If error persists:** Check logs (see Troubleshooting)

### Test 2: Marks Update
1. Log in as a teacher/admin
2. Navigate to **Monthly Exams**
3. Open an existing exam
4. Click on "Enter Marks" for a subject
5. Enter marks for students (e.g., 100, 97, 11, 11, 1)
6. Click **Save Marks** button
7. **Expected:** Success message appears, marks are saved
8. Refresh the page and verify marks are still there

### Test 3: Generate Rankings
1. After entering marks for all subjects in a monthly exam
2. Click **Generate Rankings** or **Comprehensive Ranking**
3. **Expected:** Rankings should display with roll numbers, marks, and positions

## 🔧 Troubleshooting

### If Fee Section Still Shows Error

**Check database columns:**
```bash
sqlite3 instance/app.db "PRAGMA table_info(fees);"
```

Look for:
- `exam_fee` column should exist
- `others_fee` column should exist
- There should NOT be a column named just `exam`

**If columns are wrong, fix manually:**
```bash
sqlite3 instance/app.db
```

Then in SQLite shell:
```sql
-- If 'exam' column exists instead of 'exam_fee'
ALTER TABLE fees RENAME COLUMN exam TO exam_fee;

-- If 'exam_fee' is missing
ALTER TABLE fees ADD COLUMN exam_fee NUMERIC(10, 2) DEFAULT 0.00;

-- If 'others_fee' is missing
ALTER TABLE fees ADD COLUMN others_fee NUMERIC(10, 2) DEFAULT 0.00;

-- Exit
.quit
```

### If Marks Don't Save

**Check application logs:**
```bash
# If logs are in a file
tail -f logs/app.log

# If using systemd
sudo journalctl -u your-service-name -f

# If using supervisor
sudo tail -f /var/log/supervisor/your-app-stderr.log
```

**Check database permissions:**
```bash
ls -la instance/app.db

# Fix permissions if needed (replace www-data with your user)
sudo chown www-data:www-data instance/app.db
sudo chmod 664 instance/app.db
```

**Test database write access:**
```bash
sqlite3 instance/app.db "INSERT INTO settings (key, value) VALUES ('test_key', '{}');"
sqlite3 instance/app.db "DELETE FROM settings WHERE key='test_key';"
```

### If Application Won't Start

**Check for Python errors:**
```bash
python3 -c "from app import create_app; app = create_app(); print('OK')"
```

**Check for port conflicts:**
```bash
# Check if port is in use (e.g., 5000 or 8000)
netstat -tulpn | grep :5000
```

**Restart from scratch:**
```bash
# Kill all Python/Gunicorn processes
pkill -f python
pkill -f gunicorn

# Start fresh
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📊 Database Schema Reference

### Correct Fees Table Schema

```sql
CREATE TABLE fees (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    batch_id INTEGER NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    exam_fee NUMERIC(10, 2) DEFAULT 0.00,      -- ✅ Correct name
    others_fee NUMERIC(10, 2) DEFAULT 0.00,    -- ✅ Correct name
    due_date DATE NOT NULL,
    paid_date DATE,
    status VARCHAR(7) NOT NULL,
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    late_fee NUMERIC(10, 2) DEFAULT 0.00,
    discount NUMERIC(10, 2) DEFAULT 0.00,
    notes TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(batch_id) REFERENCES batches(id)
);
```

## 🆘 Emergency Rollback

If something goes wrong and you need to restore:

```bash
# 1. Stop application
sudo systemctl stop your-service-name

# 2. Restore from backup
# (Replace with your actual backup filename)
cp instance/app.db.backup.20231023_140530 instance/app.db

# 3. Restart application
sudo systemctl start your-service-name
```

## 📞 Support

If issues persist after following this guide:

1. **Collect error information:**
   ```bash
   # Get recent logs
   tail -n 50 logs/app.log > error_log.txt
   
   # Get database schema
   sqlite3 instance/app.db ".schema fees" > db_schema.txt
   
   # Get application status
   systemctl status your-service-name > service_status.txt
   ```

2. **Check the following:**
   - Application logs for Python exceptions
   - Database file permissions
   - Network connectivity
   - Disk space: `df -h`

3. **Common quick fixes:**
   ```bash
   # Clear Python cache
   find . -type d -name __pycache__ -exec rm -rf {} +
   
   # Reinstall dependencies
   pip install -r requirements.txt --upgrade
   
   # Restart system services
   sudo systemctl daemon-reload
   ```

## ✅ Success Indicators

You'll know the fix worked when:

1. ✅ Fee section loads without SQL errors
2. ✅ Students appear when batch is selected
3. ✅ Marks can be entered and saved
4. ✅ Saved marks persist after page refresh
5. ✅ Rankings generate successfully
6. ✅ No errors in application logs

---

**Last Updated:** October 23, 2025
**Version:** 1.0
