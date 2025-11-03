# 🚀 Quick Deployment Guide - Archive System

## Deploy to VPS in 5 Steps

```bash
# Step 1: Navigate to project
cd /var/www/saroyarsir

# Step 2: Pull all changes from GitHub
git pull origin main

# Step 3: Activate virtual environment and run migration
source venv/bin/activate
python migrate_add_archive_fields.py

# Step 4: Restart application
sudo systemctl restart saro

# Step 5: Verify service is running
sudo systemctl status saro
```

## What You Get

✅ **Archive Menu** - New "Archive" option in teacher sidebar  
✅ **Archive Batches** - Archive entire batches with all students  
✅ **Archive Students** - Archive individual students  
✅ **View Archives** - See all archived items in dedicated tab  
✅ **Restore Functionality** - Restore archived batches/students  
✅ **Audit Trail** - Track who archived, when, and why  
✅ **Safe Storage** - No data deletion, only hiding from active views  

## Test It Works

1. **Login as Teacher** (Phone: 01712345678, Password: admin123)
2. **Click "Archive" in sidebar** - Should see Archive Management page
3. **Two tabs visible:**
   - Archived Batches (currently 0)
   - Archived Students (currently 0)
4. **No errors in console** (Press F12 to check)

## Expected Migration Output

```
🔄 Starting archive fields migration...
📊 Database: SQLite

📝 Adding archive fields to users table...
  ✅ Added is_archived to users
  ✅ Added archived_at to users
  ✅ Added archived_by to users
  ✅ Added archive_reason to users

📝 Adding archive fields to batches table...
  ✅ Added is_archived to batches
  ✅ Added archived_at to batches
  ✅ Added archived_by to batches
  ✅ Added archive_reason to batches

✅ Migration completed successfully!
```

## If Migration Says "Already Exists"

That's OK! It means the fields are already there. Just continue with restart.

## Features Now Available

### For Teacher:
1. **Archive Batch** - Go to Batches → (future: archive button on each batch)
2. **Archive Student** - Go to Students → (future: archive button on each student)
3. **View Archives** - Click "Archive" in sidebar
4. **Restore Items** - Click "Restore" button on archived items
5. **See History** - View who archived, when, and why

### Automatic Features:
- When batch is archived → All students archived automatically
- When batch is restored → Students archived with batch are restored
- Archived items hidden from active lists
- Audit trail automatically recorded

## Need Help?

Read full documentation: `ARCHIVE_SYSTEM_DOCUMENTATION.md`

## Troubleshooting

**Archive tab not showing?**
```bash
# Clear browser cache
Ctrl + Shift + Delete (or Cmd + Shift + Delete on Mac)
# Then refresh page
```

**Migration fails?**
```bash
# Check logs
sudo journalctl -u saro -n 50 --no-pager
```

**Service won't start?**
```bash
# Check for errors
sudo journalctl -u saro -n 50 | grep -i error
```

---

**Commit:** 837d289  
**Files Changed:** 6 files  
**Status:** ✅ Ready for Production
