# Student Fields Update - Mother Name & Address

## 📋 Changes Summary

### Database Changes
✅ **Added `mother_name` column** to `users` table
- Type: VARCHAR(200)
- Nullable: Yes
- Migration script: `migrate_add_mother_name.py`

### Model Updates (`models.py`)
✅ Added `mother_name` field to User model:
```python
mother_name = db.Column(db.String(200), nullable=True)
```

### API Updates (`routes/students.py`)
✅ **GET /api/students** - Returns mother_name and address
✅ **POST /api/students** - Accepts mother_name and address when creating
✅ **PUT /api/students/<id>** - Accepts mother_name when updating
✅ **GET /api/students/archived** - Returns mother_name and address for archived students

### Frontend Updates

#### **Student Management Form** (`student_management.html`)
✅ Added fields:
- **Father Name** field (renamed from "Parent Name")
- **Mother Name** field (new)
- **Address** field (multi-line textarea)
- **Parent Phone Number** (with better description)

Form now shows:
```
First Name | Last Name
Father Name | Mother Name
Parent Phone Number (with note: for SMS & Login)
Address (textarea)
School
Batch
```

#### **Students Table View**
Columns reorganized:
1. **Student Name** - Name + School (subtitle)
2. **Parents Info** - Shows:
   - 👨 Father Name (if available)
   - 👩 Mother Name (if available)
3. **Phone (Login)** - Parent phone + "Login Username" label
4. **Address** - Full address (truncated if long)
5. **Batch** - Batch name
6. **Password** - Show/hide password
7. **Actions** - Edit, Reset Password, Archive, Delete buttons

#### **Archive Management View**
Columns for archived students:
1. **Student Name** - Name + School
2. **Parents Info** - Father & Mother names with icons
3. **Phone** - Contact number
4. **Address** - Student address
5. **Batch** - Which batch they were in
6. **Archived Date** - When archived
7. **Reason** - Why archived + who archived (subtitle)
8. **Actions** - Restore button

### Visual Indicators
- 👨 **Blue male icon** for Father name
- 👩 **Pink female icon** for Mother name
- **Orange archive button** for archiving students
- **Truncated address** display with ellipsis for long addresses

## 🎯 Key Features

### 1. Complete Parent Information
- Father name (guardian_name)
- Mother name (mother_name)
- Parent phone for login and SMS

### 2. Address Management
- Full address field (multi-line)
- Visible in student list (truncated)
- Visible in archive list
- Stored in database address field

### 3. Archive Functionality
- Archive individual students from Students section
- Archive full batch (all students archived automatically)
- View archived students with full details
- Restore archived students
- Track who archived, when, and why

## 📝 Form Validation
- **First Name** - Required
- **Last Name** - Required
- **Parent Phone** - Required (used for login and SMS)
- **Father Name** - Optional
- **Mother Name** - Optional
- **Address** - Optional
- **School** - Optional
- **Batch** - Optional

## 🔄 Migration Instructions

### For Local Development:
```bash
python migrate_add_mother_name.py
```

### For VPS Deployment:
```bash
cd /var/www/saroyarsir
git pull origin main
source venv/bin/activate
python migrate_add_mother_name.py
sudo systemctl restart saro
```

## ✅ Testing Checklist

### Add New Student:
1. Go to Students section
2. Click "Add New Student"
3. Fill in:
   - First Name, Last Name (required)
   - Father Name (optional)
   - Mother Name (optional)
   - Parent Phone (required)
   - Address (optional)
   - School (optional)
   - Batch (optional)
4. Submit and verify all fields are saved

### View Students:
1. Check Students table shows:
   - Parent info column with both father and mother names
   - Address column
2. Verify icons display correctly (👨 blue, 👩 pink)

### Archive Student:
1. Click orange Archive button
2. Enter reason (optional)
3. Verify student removed from active list
4. Go to Archive section
5. Verify student appears with all details

### View Archived:
1. Go to Archive → Archived Students tab
2. Verify all columns display:
   - Parents Info (father and mother)
   - Address
   - Batch
   - Archive date and reason
3. Test Restore button

## 🎨 UI Improvements
- Cleaner form layout with fields grouped logically
- Better visual hierarchy with parent information
- Icons for gender distinction
- Responsive table columns
- Truncated text for long addresses
- Improved spacing and readability

## 📊 Database Schema
```sql
ALTER TABLE users ADD COLUMN mother_name VARCHAR(200);
```

Existing columns used:
- `address` - Full address
- `guardian_name` - Father/Guardian name
- `guardian_phone` - Parent phone (for login and SMS)
- `mother_name` - Mother name (NEW)

## 🔒 Security Notes
- All fields properly sanitized before saving
- Optional fields can be null
- Phone number validation maintained
- Archive feature tracks who performed the action

## 📱 SMS Integration
- Parent phone (`guardian_phone`) used for SMS notifications
- Same phone used for student login
- Phone number properly validated and formatted

## 🎉 Complete!
All features implemented, tested, and committed to GitHub.
Server running on port 3001.
Ready for production deployment to VPS.
