# URGENT: VPS Server Fix Instructions

## Two Critical Issues Need Fixing:

### Issue 1: Fee Management SQL Error ❌
**Error:** `no such column: fees.exam_fee`
**Cause:** Database migration completed but app not restarted

### Issue 2: Individual Mark Entry 2nd Time Not Working ❌  
**Cause:** Code working correctly but needs verification

---

## COMPLETE FIX PROCEDURE

### Step 1: SSH to VPS Server
```bash
ssh your_username@gsteaching.com
```

### Step 2: Navigate to Project
```bash
cd /path/to/saro
# Common paths:
# cd /var/www/saro
# cd /home/username/saro
```

### Step 3: Pull Latest Code
```bash
git pull origin main
git log --oneline -3
```

You should see recent commits about fee columns and homework.

### Step 4: Check Current Database
```bash
# Check if columns exist
sqlite3 instance/app.db "PRAGMA table_info(fees);"
```

Look for these lines:
- `8|exam_fee|NUMERIC(10, 2)|...`
- `9|others_fee|NUMERIC(10, 2)|...`

### Step 5: Run Migration (if columns NOT found)
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

OR if already done:
```
✓ exam_fee column already exists
✓ others_fee column already exists
✅ Migration completed successfully!
```

### Step 6: ⭐ CRITICAL - RESTART APPLICATION ⭐

**Option A - systemd (most common):**
```bash
sudo systemctl restart saro
sudo systemctl status saro
```

**Option B - supervisor:**
```bash
sudo supervisorctl restart saro
sudo supervisorctl status
```

**Option C - pm2:**
```bash
pm2 restart saro
pm2 status
```

**Option D - gunicorn directly:**
```bash
# Find and kill existing process
ps aux | grep gunicorn
# Kill the process (replace PID)
kill -9 <PID>

# Start new one
cd /path/to/saro
source venv/bin/activate
gunicorn -c gunicorn.conf.py app:app --daemon
```

**Option E - Manual restart.sh script:**
```bash
./restart_server.sh
```

### Step 7: Verify Service is Running
```bash
# Check process
ps aux | grep -E "python|gunicorn" | grep -v grep

# Check systemd service
sudo systemctl status saro

# Check logs
sudo journalctl -u saro -n 50
# OR
tail -f logs/app.log
```

### Step 8: Test in Browser

1. **Clear Browser Cache Completely:**
   - Press `Ctrl + Shift + Delete`
   - Select "All time"
   - Check "Cached images and files"
   - Click "Clear data"

2. **Test Fee Management:**
   - Go to Fee Management page
   - Select any batch
   - Select year 2025
   - Should load student table WITHOUT red error
   - Should show month columns
   - Try entering a fee amount
   - Should save successfully

3. **Test Individual Marks Entry:**
   - Go to Monthly Exams
   - Open an existing exam
   - Click on an individual subject exam
   - Enter marks for students (first time)
   - Click Save - should save successfully
   - NOW edit those same marks (second time)
   - Click Save again
   - Should UPDATE successfully without errors
   - Verify marks were updated by refreshing page

### Step 9: Check for Errors

Open browser DevTools (F12) and check Console tab:
- Should see NO red errors
- Should see success messages
- No SQL errors about "no such column"

---

## Troubleshooting

### Fee Management Still Shows SQL Error?

**Check 1: Migration actually ran**
```bash
sqlite3 instance/app.db "PRAGMA table_info(fees);" | grep -E "exam_fee|others_fee"
```
Should show 2 lines with the columns.

**Check 2: App actually restarted**
```bash
# Get process start time
ps -eo pid,lstart,cmd | grep gunicorn | grep -v grep
# OR
systemctl status saro | grep "Active:"
```
The process should have started AFTER you ran the restart command.

**Check 3: Using correct database**
```bash
# In your app directory
ls -la instance/
# Should show app.db file

# Check app.py config
grep DATABASE config.py
```

**Check 4: Clear Python cache**
```bash
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
```

Then restart app again.

### Individual Marks Still Not Working?

**Test Process:**
1. Open browser DevTools (F12) → Network tab
2. Enter marks → Click Save
3. Look for the POST request to `/api/monthly-exams/.../marks`
4. Check Response tab - should show `"success": true`
5. Refresh page - marks should be saved
6. Edit same marks → Click Save again
7. Should show `"success": true` again
8. Check Response - should say "Successfully saved X marks"

**If still failing:**
```bash
# Check application logs while testing
tail -f logs/app.log
# OR
sudo journalctl -u saro -f
```

Look for Python errors or stack traces.

---

## Emergency Recovery

### If App Won't Start After Changes:

```bash
# 1. Check logs for Python errors
sudo journalctl -u saro -n 100 --no-pager

# 2. Try running app manually to see errors
cd /path/to/saro
source venv/bin/activate
python app.py
# Press Ctrl+C to stop, read any errors

# 3. If database is corrupted
cp instance/app.db instance/app.db.backup
# Then restore from previous backup if needed

# 4. Roll back code if necessary
git log --oneline -10
git reset --hard <previous-commit-hash>
sudo systemctl restart saro
```

---

## Verification Checklist

After completing all steps:

- [ ] SSH connection successful
- [ ] Code pulled from GitHub
- [ ] Migration script shows columns added (or already exist)
- [ ] Application restarted successfully
- [ ] Service status shows "active (running)"
- [ ] Browser cache cleared completely
- [ ] Fee Management page loads without SQL error
- [ ] Can select batch and year
- [ ] Student fee table displays
- [ ] Can enter and save fee amounts
- [ ] Monthly Exams page works
- [ ] Can enter marks first time (works)
- [ ] Can UPDATE marks second time (works)
- [ ] No console errors in browser DevTools

---

## Quick Commands Summary

```bash
# Complete fix in one go:
cd /path/to/saro
git pull origin main
python migrate_add_fee_columns.py
sudo systemctl restart saro
sudo systemctl status saro

# Verify:
ps aux | grep gunicorn
tail -f logs/app.log

# Then in browser:
# Ctrl+Shift+Delete → Clear cache → Test both features
```

---

## Support Information

If issues persist after following ALL steps:

1. Check Python version: `python --version` (should be 3.8+)
2. Check dependencies: `pip list | grep -i flask`
3. Check disk space: `df -h`
4. Check permissions: `ls -la instance/`
5. Send error logs from: `sudo journalctl -u saro -n 200`

The code is correct. The database migration is correct. 
**The only issue is the app needs to restart to reload the new schema.**
