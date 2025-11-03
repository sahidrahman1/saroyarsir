# VPS Deployment Instructions - Fee Column Fix

## Issue
The Fee Management page shows error: `no such column: fees.exam_fee`

## Root Cause
The database migration was run successfully (columns `exam_fee` and `others_fee` were added), but the Flask application on the VPS hasn't been restarted to reload the SQLAlchemy models with the new schema.

## Solution - Run These Commands on VPS

### Step 1: SSH to VPS
```bash
ssh your_username@gsteaching.com
```

### Step 2: Navigate to Project Directory
```bash
cd /path/to/saro
# Common paths:
# cd /var/www/saro
# cd /home/username/saro
# cd ~/saro
```

### Step 3: Pull Latest Code
```bash
git pull origin main
```

### Step 4: Activate Virtual Environment (if using one)
```bash
source venv/bin/activate
# or
source .venv/bin/activate
```

### Step 5: Verify Migration Script Exists
```bash
ls -la migrate_add_fee_columns.py
```

### Step 6: Run Migration (if not already run)
```bash
python migrate_add_fee_columns.py
```

Expected output:
```
Database tables created successfully!
Adding exam_fee column...
✓ exam_fee column added
Adding others_fee column...
✓ others_fee column added

✅ Migration completed successfully!
```

### Step 7: Verify Columns Exist in Database
```bash
sqlite3 instance/app.db "PRAGMA table_info(fees);" | grep -E "exam_fee|others_fee"
```

Expected output showing both columns:
```
8|exam_fee|NUMERIC(10, 2)|0|0.00|0
9|others_fee|NUMERIC(10, 2)|0|0.00|0
```

### Step 8: Restart Flask Application

**If using systemd service:**
```bash
sudo systemctl restart saro
sudo systemctl status saro
```

**If using gunicorn directly:**
```bash
pkill gunicorn
gunicorn -c gunicorn.conf.py app:app --daemon
```

**If using supervisor:**
```bash
sudo supervisorctl restart saro
sudo supervisorctl status saro
```

**If using pm2:**
```bash
pm2 restart saro
pm2 status
```

### Step 9: Check Logs for Errors
```bash
# For systemd:
sudo journalctl -u saro -n 50 -f

# For supervisor:
sudo tail -f /var/log/supervisor/saro-*.log

# For pm2:
pm2 logs saro

# Direct log file:
tail -f logs/app.log
```

### Step 10: Test in Browser
1. Clear browser cache (Ctrl+Shift+Delete)
2. Go to Fee Management page
3. Select a batch and year
4. Should load without SQL errors

## If Still Not Working

### Check Service Status
```bash
sudo systemctl status saro
# or
sudo supervisorctl status saro
# or
pm2 status
```

### Check Process
```bash
ps aux | grep python
ps aux | grep gunicorn
```

### Kill All Python Processes (if stuck)
```bash
pkill -9 python
pkill -9 gunicorn
```

### Then Restart Service
```bash
sudo systemctl start saro
```

## Common Issues

### Issue: Migration says "column already exists"
**Solution:** This is fine! It means the columns were already added. Just restart the app.

### Issue: "Permission denied" when restarting
**Solution:** Use `sudo` before the restart command.

### Issue: App won't start after restart
**Solution:** Check logs for Python errors:
```bash
sudo journalctl -u saro -n 100
```

### Issue: Still getting SQL error after restart
**Solution:** 
1. Verify columns exist in database
2. Clear browser cache completely
3. Check if app actually restarted (check process ID)
4. Try accessing from incognito/private window

## Quick Commands Summary

```bash
# On VPS:
cd /path/to/saro
git pull origin main
python migrate_add_fee_columns.py
sudo systemctl restart saro
sudo systemctl status saro
```

## Verification

After restart, the fee management should work without errors. The columns are:
- `exam_fee` - For exam-related fees
- `others_fee` - For other miscellaneous fees

Both columns default to 0.00 if not specified.
