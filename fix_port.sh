#!/bin/bash
echo "🔍 Checking for processes on port 5000..."
PIDS=$(sudo lsof -t -i:5000)
if [ -n "$PIDS" ]; then
  echo "🛑 Killing processes using port 5000: $PIDS"
  sudo kill -9 $PIDS
else
  echo "✅ Port 5000 is free"
fi
echo "🚀 Starting Flask..."
flask run --host=0.0.0.0 --port=5000

