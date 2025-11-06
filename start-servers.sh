#!/bin/bash

# Start Kapp Backend and Frontend Servers

echo "🚀 Starting Kapp servers..."
echo ""

# Kill any existing process on port 5001
echo "🔍 Checking for existing backend process on port 5001..."
EXISTING_PID=$(lsof -ti:5001)
if [ ! -z "$EXISTING_PID" ]; then
  echo "⚠️  Found existing process (PID: $EXISTING_PID), terminating..."
  kill -9 $EXISTING_PID
  sleep 1
  echo "✓ Existing process terminated"
fi

# Start backend in background
echo "📦 Starting backend on http://localhost:5001..."
cd /Users/am/Sync/Cursor/Kapp_1/backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
echo "✓ Backend started (PID: $BACKEND_PID)"
echo ""

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "⚛️  Starting frontend on http://localhost:5173..."
cd /Users/am/Sync/Cursor/Kapp_1/frontend
npm run dev

# If frontend exits, kill backend too
kill $BACKEND_PID
