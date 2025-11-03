# VPS FIX INSTRUCTIONS

## Issues Being Fixed

1. **Archived students still showing** in attendance, SMS, and other lists
2. **Delete monthly exam returns "Not found" error** on VPS

## Root Causes

### Issue 1: Archived Students Showing
- **Frontend-Backend Mismatch**: Frontend might have cached data
- **Database Inconsistency**: `is_archived` flag might not be properly set
- **Missing Filters**: Some API endpoints might be missing the archive filter

### Issue 2: Delete Monthly Exam Not Working
- **Database Sync Issue**: Monthly exam IDs might not match between frontend and backend
- **Orphaned Data**: Rankings or individual exams might be blocking deletion
- **Session/Cache Issue**: Browser cache might have stale data

## Deployment Steps

### Option 1: Automatic Deployment (Recommended)

```bash
# Run the deployment script
./deploy_vps_fixes.sh
```

This will:
1. Pull latest code
2. Push to GitHub
3. Deploy to VPS
4. Run database fix script
5. Restart service
6. Show status and logs

### Option 2: Manual Deployment

```bash
# Step 1: SSH to VPS
ssh root@161.35.21.222

# Step 2: Navigate to project directory
cd /var/www/saroyarsir

# Step 3: Pull latest code
git pull origin main

# Step 4: Run database fix script
python3 fix_vps_database.py

# Step 5: Restart service
sudo systemctl restart smartgardenhub

# Step 6: Check service status
sudo systemctl status smartgardenhub

# Step 7: Monitor logs
sudo journalctl -u smartgardenhub -f
```

## What the Fix Does

### Database Fix Script (`fix_vps_database.py`)

1. **Checks Archived Students**
   - Lists all students with is_archived=True
   - Shows their phone numbers and names

2. **Finds Inconsistencies**
   - Students with is_archived=1 but archived_at=NULL
   - Students with is_archived=0 but archived_at set
   - Auto-fixes these inconsistencies

3. **Verifies Monthly Exams**
   - Lists recent monthly exams with their IDs
   - Shows which ones can be deleted

4. **Cleans Orphaned Data**
   - Removes rankings without exams
   - Removes individual exams without monthly exams

5. **Verifies Schema**
   - Checks if all required columns exist
   - Adds missing columns if needed

### Code Changes

1. **Enhanced Logging (`routes/monthly_exams.py`)**
   - Added detailed print statements to track deletion process
   - Shows which exam is being deleted
   - Lists all available exam IDs if not found
   - Prints count of deleted rankings and individual exams

2. **Frontend Logging (`dashboard_teacher.html`)**
   - Added console.log to track delete request
   - Shows response status
   - Better error messages

## Testing After Deployment

### 1. Test Archived Students

```bash
# On VPS, check database
ssh root@161.35.21.222
cd /var/www/saroyarsir
sqlite3 madrasha.db "SELECT id, first_name, last_name, is_archived FROM users WHERE role='STUDENT' ORDER BY is_archived DESC LIMIT 20;"
```

**Expected Result:**
- Archived students have is_archived=1
- They should NOT appear in attendance marking
- They should NOT appear in SMS recipient list
- They SHOULD appear in Archive Management section

### 2. Test Delete Monthly Exam

1. **Open Browser (Incognito Mode Recommended)**
   ```
   Press Ctrl+Shift+N for Chrome/Edge
   Or Ctrl+Shift+P for Firefox
   ```

2. **Login as Teacher**
   - Username: 01711111111
   - Password: teacher123

3. **Go to Monthly Exams**
   - Click "Monthly Exams" in sidebar

4. **Try to Delete an Exam**
   - Find an exam with NO marks entered
   - Click the delete (trash) icon
   - Confirm deletion

5. **Check Browser Console (F12)**
   - Should see: "Deleting monthly exam: [ID] [Title]"
   - Should see: "Delete response status: 200"
   - Should see: "Monthly exam deleted successfully"

6. **Check VPS Logs**
   ```bash
   sudo journalctl -u smartgardenhub -n 50 --no-pager
   ```
   Should see:
   - "DELETE request for monthly exam [ID] by user [USER_ID]"
   - "Found monthly exam: [Title]"
   - "Deleted X rankings"
   - "Deleted Y individual exams"
   - "Successfully deleted monthly exam [ID]"

## Troubleshooting

### Delete Still Shows "Not Found"

1. **Check VPS Logs**
   ```bash
   ssh root@161.35.21.222 'sudo journalctl -u smartgardenhub -n 100 | grep DELETE'
   ```

2. **Verify Exam Exists**
   ```bash
   ssh root@161.35.21.222
   cd /var/www/saroyarsir
   sqlite3 madrasha.db "SELECT id, title FROM monthly_exams ORDER BY id DESC LIMIT 10;"
   ```

3. **Clear Browser Cache**
   - Press Ctrl+Shift+Delete
   - Select "Cached images and files"
   - Clear data
   - Or use Incognito mode

4. **Check Frontend Console (F12)**
   - Look for the exam ID being sent
   - Compare with database IDs
   - Check for any CORS or network errors

### Archived Students Still Visible

1. **Run Database Fix Again**
   ```bash
   ssh root@161.35.21.222
   cd /var/www/saroyarsir
   python3 fix_vps_database.py
   ```

2. **Check Database Directly**
   ```bash
   sqlite3 madrasha.db "SELECT COUNT(*) FROM users WHERE role='STUDENT' AND is_archived=1;"
   ```

3. **Clear Browser Cache and Re-login**
   - Logout completely
   - Clear cache
   - Login again in Incognito mode

4. **Check Specific Endpoint**
   - Open browser DevTools (F12)
   - Go to Network tab
   - Mark attendance
   - Check the /api/batches/{id}/students response
   - Archived students should NOT be in the list

## Verification Checklist

After deployment, verify these items:

- [ ] VPS service running: `sudo systemctl status smartgardenhub`
- [ ] Latest code pulled: `git log --oneline -1` shows commit e42bed5 or later
- [ ] Database fix script ran successfully
- [ ] No errors in logs: `sudo journalctl -u smartgardenhub -n 50`
- [ ] Archived students NOT visible in attendance
- [ ] Delete monthly exam works (test with exam without marks)
- [ ] Browser console shows proper logging
- [ ] No "Not found" errors when deleting

## Expected Commit

Latest commit should be:
```
e42bed5 - Fix: Enhanced logging for delete monthly exam and VPS database fix script
```

Check with:
```bash
git log --oneline -1
```

## Support

If issues persist after deployment:

1. **Collect Information**
   ```bash
   # On VPS
   sudo journalctl -u smartgardenhub -n 200 > ~/logs.txt
   
   # In browser console (F12)
   # Copy all error messages
   ```

2. **Check Database State**
   ```bash
   sqlite3 madrasha.db "SELECT * FROM users WHERE is_archived=1;"
   sqlite3 madrasha.db "SELECT id, title FROM monthly_exams ORDER BY id DESC LIMIT 20;"
   ```

3. **Provide Details**
   - Exact error message
   - Browser console logs
   - VPS service logs
   - Steps to reproduce

## Files Changed

1. `routes/monthly_exams.py` - Enhanced logging for delete
2. `templates/templates/dashboard_teacher.html` - Frontend logging
3. `fix_vps_database.py` - Database fix script (NEW)
4. `deploy_vps_fixes.sh` - Deployment automation (NEW)

## Database Schema Required

The `users` table must have these columns:
- `is_archived` (BOOLEAN, default False)
- `archived_at` (DATETIME, nullable)
- `archived_by` (INTEGER, foreign key to users.id)

The fix script will add these if missing.
