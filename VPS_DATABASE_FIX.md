# 🔧 VPS Database Fix - Student Login Issue

## Problem
Students created with the old system can't login because:
1. Database is missing new columns (`mother_name`, archive fields, documents table)
2. Student passwords are set to old default instead of phone last 4 digits

## Solution

Run this on your VPS to fix everything:

```bash
cd /var/www/saroyarsir
curl -sSL https://raw.githubusercontent.com/8ytgggygt/saro/main/fix_vps_database.sh | sudo bash
```

Or manually:

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Navigate to app directory
cd /var/www/saroyarsir

# Activate virtual environment
source venv/bin/activate

# Run migrations
python3 migrate_add_archive_fields.py
python3 migrate_add_mother_name.py
python3 migrate_add_documents.py

# Reset student passwords
python3 reset_all_student_passwords.py

# Restart service
sudo systemctl restart saro
```

## What It Does

### 1. Run Database Migrations
- Adds `mother_name` column to users table
- Adds archive fields (`is_archived`, `archived_at`, etc.)
- Creates `documents` table for PDF management

### 2. Reset Student Passwords
- Changes all student passwords to last 4 digits of their phone number
- Example: Phone `01812345678` → Password `5678`

### 3. Restart Application
- Restarts the service to apply changes

## After Running the Fix

### Student Login Credentials

Students can now login with:
- **Phone:** Their full phone number (e.g., `01812345678`)
- **Password:** Last 4 digits of phone (e.g., `5678`)

### Test Login

If you created a student with phone `01912345678`:
- Phone: `01912345678`
- Password: `5678`

## Verify It Worked

```bash
# Check service status
sudo systemctl status saro

# View logs
sudo journalctl -u saro -f

# Test login via curl
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "01912345678", "password": "5678"}'
```

## What Changed in Code

The authentication logic now checks passwords in this order for students:

1. ✅ **Last 4 digits of phone** (Primary - NEW)
2. ✅ **"student123"** (Legacy fallback for old accounts)
3. ✅ **Hashed password** (For custom passwords set by admin)

For teachers and admins, it still uses the hashed password system.

## Common Issues

### Issue: "no such column: users.mother_name"
**Fix:** Run `python3 migrate_add_mother_name.py`

### Issue: Student can't login with last 4 digits
**Fix:** Run `python3 reset_all_student_passwords.py`

### Issue: Service won't start after migration
```bash
# Check logs
sudo journalctl -u saro -n 50 --no-pager

# Try manual restart
sudo systemctl stop saro
sudo systemctl start saro
```

### Issue: Permission denied on database
```bash
sudo chown www-data:www-data /var/www/saroyarsir/instance/app.db
sudo chmod 644 /var/www/saroyarsir/instance/app.db
```

## Manual Password Reset for Specific Student

If you need to reset password for just one student:

```bash
cd /var/www/saroyarsir
source venv/bin/activate
python3

# In Python shell:
from app import app, db
from models import User

with app.app_context():
    # Find student by phone
    student = User.query.filter_by(phoneNumber='01912345678').first()
    
    if student:
        # Get last 4 digits
        last_4 = student.phoneNumber[-4:]
        
        # Set password (will be hashed)
        from werkzeug.security import generate_password_hash
        student.password_hash = generate_password_hash(last_4)
        db.session.commit()
        print(f"✅ Password reset for {student.first_name}. New password: {last_4}")
    else:
        print("❌ Student not found")
```

## Rollback (If Needed)

If something goes wrong, you can restore from backup:

```bash
# Stop service
sudo systemctl stop saro

# Restore database (if you made a backup)
cp /var/www/saroyarsir/instance/app.db.backup /var/www/saroyarsir/instance/app.db

# Start service
sudo systemctl start saro
```

## Prevention for Future

The automated deployment script now includes:
- All migrations run automatically
- Student passwords set to last 4 digits on creation
- Proper column validation before user creation

---

**Need help?** Check the logs: `sudo journalctl -u saro -f`
