# VPS SQLite Fix - Quick Instructions

## Problem
The VPS is trying to connect to PostgreSQL but you need SQLite.

**Error:**
```
sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres
```

## Solution

### Option 1: Quick Fix (Recommended)

Run this **ONE COMMAND** on your VPS:

```bash
ssh root@161.35.21.222 'cd /var/www/saroyarsir && git pull origin main && bash vps_sqlite_quickfix.sh'
```

This will:
1. Pull latest code
2. Configure .env for SQLite
3. Fix phone constraint (allow siblings)
4. Verify database
5. Restart service
6. Show status and logs

### Option 2: Manual Fix

```bash
# SSH to VPS
ssh root@161.35.21.222

# Go to app directory
cd /var/www/saroyarsir

# Pull latest code
git pull origin main

# Run the quick fix script
bash vps_sqlite_quickfix.sh
```

### Option 3: Step by Step

```bash
# SSH to VPS
ssh root@161.35.21.222

# Go to app directory
cd /var/www/saroyarsir

# Pull latest code
git pull origin main

# Create .env file for SQLite
cat > .env << 'EOF'
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-this-in-production
DATABASE_URL=sqlite:///madrasha.db
PORT=8001
HOST=0.0.0.0
SESSION_TYPE=filesystem
EOF

# Restart service
sudo systemctl restart smartgardenhub

# Check status
sudo systemctl status smartgardenhub
```

## What This Does

The fix changes the database configuration from:
- ❌ **OLD**: `DATABASE_URL=postgresql://...` (requires PostgreSQL driver)
- ✅ **NEW**: `DATABASE_URL=sqlite:///madrasha.db` (uses SQLite)

## Verify It Worked

After running the fix, check the logs:

```bash
sudo journalctl -u smartgardenhub -n 50
```

You should see:
- ✅ No more "Can't load plugin: sqlalchemy.dialects:postgres" error
- ✅ Service running successfully
- ✅ Database connected

## Access Your Application

After the fix, your app should be available at:
- http://161.35.21.222:8001
- Or your domain if configured

## If Still Having Issues

1. **Check if madrasha.db exists:**
   ```bash
   ls -lh /var/www/saroyarsir/madrasha.db
   ```

2. **Check .env file:**
   ```bash
   cat /var/www/saroyarsir/.env
   ```
   Should show: `DATABASE_URL=sqlite:///madrasha.db`

3. **Check service logs:**
   ```bash
   sudo journalctl -u smartgardenhub -n 100
   ```

4. **Restart service manually:**
   ```bash
   sudo systemctl restart smartgardenhub
   sudo systemctl status smartgardenhub
   ```

## Files Changed

- `fix_vps_sqlite.sh` - Full SQLite configuration script
- `vps_sqlite_quickfix.sh` - Quick fix script (recommended)
- `deploy_vps_final.sh` - Updated to use SQLite
- `deploy_vps_fixes.sh` - Updated to use SQLite
- `.env` - Will be created/updated on VPS

## Latest Commit

```
8b4fe37 - Fix: VPS SQLite configuration - remove PostgreSQL dependency
```

Verify with: `git log --oneline -1`
