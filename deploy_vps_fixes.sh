#!/bin/bash

# VPS Fix Deployment Script
# Fixes: Archived students showing, Delete monthly exam not working

echo "=========================================="
echo "VPS FIX DEPLOYMENT"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

VPS_HOST="root@161.35.21.222"
VPS_DIR="/var/www/saroyarsir"

echo -e "${YELLOW}Step 1: Pulling latest code from GitHub...${NC}"
git pull origin main
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to pull from GitHub${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Code updated${NC}"
echo ""

echo -e "${YELLOW}Step 2: Pushing to VPS...${NC}"
git push origin main
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to push to GitHub${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Code pushed${NC}"
echo ""

echo -e "${YELLOW}Step 3: Deploying to VPS...${NC}"

ssh $VPS_HOST << 'ENDSSH'
#!/bin/bash

cd /var/www/saroyarsir || exit 1

echo "→ Pulling latest code..."
git pull origin main

echo ""
echo "→ Running database fix script..."
python3 fix_vps_database.py

echo ""
echo "→ Restarting service..."
sudo systemctl restart smartgardenhub

echo ""
echo "→ Checking service status..."
sudo systemctl status smartgardenhub --no-pager | head -n 15

echo ""
echo "→ Checking recent logs..."
sudo journalctl -u smartgardenhub -n 20 --no-pager

ENDSSH

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to deploy to VPS${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=========================================="
echo -e "✓ DEPLOYMENT COMPLETED"
echo -e "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Clear browser cache (Ctrl+Shift+Delete) or use Incognito mode"
echo "2. Test deleting a monthly exam"
echo "3. Verify archived students don't appear in attendance"
echo "4. Check attendance marking works properly"
echo ""
echo "If delete still doesn't work:"
echo "  - Check browser console (F12) for errors"
echo "  - Check VPS logs: ssh $VPS_HOST 'sudo journalctl -u smartgardenhub -n 50'"
echo ""
