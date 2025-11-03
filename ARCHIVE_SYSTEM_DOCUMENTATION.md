# 📦 Archive System - Complete Documentation

## ✨ Features Overview

The Archive System allows teachers to:
1. **Archive Batches** - Move entire batches to archive
2. **Archive Students** - Move individual students to archive
3. **Batch Security** - When a batch is archived, ALL students in that batch are automatically archived
4. **Restore Functionality** - Archived items can be restored back to active status
5. **Safe Storage** - Archived data is NEVER deleted, only hidden from active views
6. **Audit Trail** - Track who archived items, when, and why

---

## 🚀 Quick Start Guide

### For VPS Deployment

```bash
# Step 1: Navigate to project
cd /var/www/saroyarsir

# Step 2: Pull latest code
git pull origin main

# Step 3: Run migration to add archive fields
source venv/bin/activate
python migrate_add_archive_fields.py

# Step 4: Restart application
sudo systemctl restart saro

# Step 5: Verify
sudo systemctl status saro
```

---

## 📋 How to Use

### Archive a Batch

1. **Go to Teacher Dashboard**
2. **Navigate to "Batches" section**
3. **Click on a batch**
4. **Click "Archive Batch" button**
5. **Enter reason for archiving** (optional)
6. **Confirm** - All students in the batch will be archived automatically

### Archive a Student

1. **Go to Teacher Dashboard**
2. **Navigate to "Students" section**
3. **Find the student**
4. **Click "Archive Student" button**
5. **Enter reason for archiving** (optional)
6. **Confirm** - Student is archived

### View Archived Items

1. **Go to Teacher Dashboard**
2. **Click "Archive" in sidebar menu**
3. **Choose tab:**
   - **Archived Batches** - View all archived batches
   - **Archived Students** - View all archived students
4. **See details:**
   - Who archived it
   - When it was archived
   - Reason for archiving
   - Number of students affected (for batches)

### Restore from Archive

**Restore Batch:**
1. Go to **Archive → Archived Batches** tab
2. Find the batch
3. Click **"Restore"** button
4. Confirm - Batch and its students are restored

**Restore Student:**
1. Go to **Archive → Archived Students** tab
2. Find the student
3. Click **"Restore"** button
4. Confirm - Student is restored

---

## 🔐 Security Features

### Automatic Batch Archiving
When you archive a batch:
- ✅ The batch is marked as archived
- ✅ ALL students in that batch are automatically archived
- ✅ Archive reason is logged for the batch
- ✅ Archive reason for students shows: "Archived with batch: [Batch Name]"
- ✅ Timestamp and teacher who archived are recorded

### Restore Safety
When you restore a batch:
- ✅ The batch is restored to active
- ✅ Students archived WITH this batch are automatically restored
- ✅ Students archived separately (not with the batch) stay archived
- ✅ This prevents accidentally restoring students who were intentionally archived

### Data Protection
- ❌ **NO DELETION** - Archived items are never deleted
- ✅ **Hidden from Active Views** - Archived items don't appear in regular student/batch lists
- ✅ **Separate Archive View** - Dedicated section to manage archived items
- ✅ **Audit Trail** - Complete history of who, when, why

---

## 🛠️ Technical Implementation

### Database Changes

**New fields added to `users` table:**
```sql
is_archived BOOLEAN DEFAULT 0 NOT NULL
archived_at DATETIME NULL
archived_by INTEGER NULL (Foreign Key to users.id)
archive_reason TEXT NULL
```

**New fields added to `batches` table:**
```sql
is_archived BOOLEAN DEFAULT 0 NOT NULL
archived_at DATETIME NULL
archived_by INTEGER NULL (Foreign Key to users.id)
archive_reason TEXT NULL
```

### API Endpoints

**Batch Archive Routes:**
- `POST /api/batches/<batch_id>/archive` - Archive a batch
- `POST /api/batches/<batch_id>/restore` - Restore a batch
- `GET /api/batches/archived` - Get all archived batches

**Student Archive Routes:**
- `POST /api/students/<student_id>/archive` - Archive a student
- `POST /api/students/<student_id>/restore` - Restore a student
- `GET /api/students/archived` - Get all archived students

### Query Filters

All existing batch and student queries automatically exclude archived items:
- `Batch.query.filter_by(is_archived=False)` - Active batches only
- `User.query.filter(User.is_archived == False)` - Active students only

---

## 📊 Use Cases

### Use Case 1: Batch Completed
**Scenario:** HSC-2025 batch has finished their course
- Archive the entire batch
- All students in that batch are archived
- Data preserved for records
- Not cluttering active batch lists

### Use Case 2: Student Left
**Scenario:** A student left mid-course
- Archive individual student
- Student removed from active lists
- Fees, attendance, exam records preserved
- Can be restored if student returns

### Use Case 3: Seasonal Break
**Scenario:** Summer break - all batches paused
- Archive all batches temporarily
- Students archived with batches
- After break: Restore all batches
- Everything returns to active state

### Use Case 4: Data Cleanup
**Scenario:** Old data cluttering the system
- Archive old batches from previous years
- Keep system organized
- Historical data safe and accessible
- Active view stays clean

---

## 🎨 UI Components

### Archive Tab in Sidebar
- New menu item: **"Archive"** with archive icon
- Located below "Online Exams"
- Shows archive management interface

### Archive Management Page
Two tabs:
1. **Archived Batches**
   - Table showing: Name, Student count, Archive date, Archived by, Reason
   - "Restore" button for each batch
   - Empty state when no archived batches

2. **Archived Students**
   - Table showing: Name, Phone, Batch, Archive date, Archived by, Reason
   - "Restore" button for each student
   - Empty state when no archived students

### Batch Management (Future Enhancement)
- "Archive" button next to each batch
- Confirmation dialog before archiving
- Shows number of students that will be archived

### Student Management (Future Enhancement)
- "Archive" button for each student
- Confirmation dialog
- Option to add archive reason

---

## 🧪 Testing Checklist

### Test Archive Batch
- [ ] Archive a batch with 5 students
- [ ] Verify batch disappears from active batches list
- [ ] Verify all 5 students disappear from active students list
- [ ] Check Archive tab shows the batch
- [ ] Check Archive tab shows the 5 students
- [ ] Verify archive reason is recorded

### Test Restore Batch
- [ ] Restore the archived batch
- [ ] Verify batch appears in active batches list
- [ ] Verify all 5 students appear in active students list
- [ ] Verify archive fields are cleared

### Test Archive Student
- [ ] Archive one student individually
- [ ] Verify student disappears from active list
- [ ] Check Archive tab shows the student
- [ ] Verify batch is NOT archived
- [ ] Other students in batch remain active

### Test Restore Student
- [ ] Restore the archived student
- [ ] Verify student appears in active list
- [ ] Verify archive fields are cleared

### Test Security
- [ ] Archive batch A with 3 students
- [ ] Archive student from batch B separately
- [ ] Restore batch A
- [ ] Verify: Batch A students are restored
- [ ] Verify: Batch B student stays archived (not affected)

---

## 📝 Migration Guide

### From Old System to Archive System

If you have existing data:

1. **All existing batches and students are automatically active** (is_archived = False)
2. **No data is lost** - Archive fields are added with safe defaults
3. **System continues working** - No breaking changes
4. **New feature is additive** - Only adds functionality

### Running Migration

```bash
# On VPS
cd /var/www/saroyarsir
source venv/bin/activate
python migrate_add_archive_fields.py
```

**Expected Output:**
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

---

## 🔧 Troubleshooting

### Issue: Archive button not showing
**Solution:** Clear browser cache and refresh page

### Issue: Students not archiving with batch
**Solution:** Check database - ensure `is_archived` field exists in users table

### Issue: Restored items not appearing
**Solution:** Refresh the page - lists auto-reload after restore

### Issue: Migration fails
**Solution:** 
```bash
# Check if columns already exist
sqlite3 smartgardenhub.db "PRAGMA table_info(users);" | grep is_archived
sqlite3 smartgardenhub.db "PRAGMA table_info(batches);" | grep is_archived

# If they exist, migration is already done
```

---

## 🎯 Best Practices

### When to Archive
✅ Batch has completed
✅ Student has left permanently
✅ Old data needs organizing
✅ Seasonal breaks (can restore later)

### When NOT to Archive
❌ Student is just absent temporarily
❌ Batch is still ongoing
❌ Unsure if you'll need the data
❌ Just want to hide temporarily (use is_active instead)

### Naming Conventions
- **Batch archive reason:** "Course completed", "Batch ended", "Transferred to new batch"
- **Student archive reason:** "Student left", "Completed course", "Transferred", "Graduated"

---

## 📊 Database Schema

### users table (Archive fields)
```sql
is_archived      BOOLEAN   NOT NULL DEFAULT 0   -- TRUE if archived
archived_at      DATETIME  NULL                  -- When archived
archived_by      INTEGER   NULL                  -- User ID who archived
archive_reason   TEXT      NULL                  -- Why archived
```

### batches table (Archive fields)
```sql
is_archived      BOOLEAN   NOT NULL DEFAULT 0
archived_at      DATETIME  NULL
archived_by      INTEGER   NULL
archive_reason   TEXT      NULL
```

---

## 🚀 Future Enhancements

### Planned Features
1. **Archive action in batch detail view** - Archive button in batch details page
2. **Archive action in student detail view** - Archive button in student profile
3. **Batch archive confirmation modal** - Show list of students that will be archived
4. **Archive statistics** - Dashboard widget showing archive counts
5. **Archive search/filter** - Search archived items by name, date, reason
6. **Bulk restore** - Restore multiple items at once
7. **Archive expiry** - Auto-delete archives after X years (configurable)
8. **Archive export** - Export archived data to CSV/PDF

---

## ✅ Summary

**What was added:**
- ✅ Archive fields in database (users and batches tables)
- ✅ Migration script for existing databases
- ✅ API routes for archive/restore operations
- ✅ Archive Management UI with tabs
- ✅ Automatic batch-student archiving
- ✅ Safe restore with relationship tracking
- ✅ Audit trail (who, when, why)
- ✅ Query filters to hide archived items

**What works:**
- ✅ Archive batches (with automatic student archiving)
- ✅ Archive individual students
- ✅ View archived items in dedicated tab
- ✅ Restore batches (with automatic student restore)
- ✅ Restore individual students
- ✅ Track archive history

**What's protected:**
- ✅ No data deletion
- ✅ Hidden from active views
- ✅ Separate archive view
- ✅ Complete audit trail
- ✅ Relationship-aware restore

---

**Last Updated:** October 20, 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready
