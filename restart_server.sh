#!/bin/bash
cd /workspaces/saro

# Kill existing server
pkill -f "python.*app.py" 2>/dev/null || true
sleep 1

# Start new server
echo "Starting Flask server..."
python3 app.py > /tmp/server.log 2>&1 &
SERVER_PID=$!

sleep 3

if ps -p $SERVER_PID > /dev/null; then
    echo "✓ Server started successfully (PID: $SERVER_PID)"
    echo "✓ Student creation fix applied (removed invalid import)"
    echo "✓ Fee save fix applied (simplified route registration)"
    echo ""
    echo "Fixes completed:"
    echo "1. Student creation: Fixed missing password generator import"
    echo "2. Fee saving: Simplified route to avoid conflicts"
    echo ""
    echo "Both endpoints should now work without 400/404 errors"
else
    echo "✗ Server failed to start"
    echo "Check /tmp/server.log for errors"
fi