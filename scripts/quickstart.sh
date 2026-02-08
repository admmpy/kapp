#!/bin/bash

# Quickstart script for Kapp
# Assumes dependencies are already installed (run setup.sh first if not)

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Starting Kapp..."
echo ""

# Check if backend venv exists
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${RED}Error: Backend virtual environment not found.${NC}"
    echo "Please run ./setup.sh first to set up the project."
    exit 1
fi

# Check if frontend node_modules exists
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "${RED}Error: Frontend dependencies not installed.${NC}"
    echo "Please run ./setup.sh first to set up the project."
    exit 1
fi

# Kill any existing process on port 5001
EXISTING_PID=$(lsof -ti:5001 2>/dev/null || true)
if [ ! -z "$EXISTING_PID" ]; then
    echo -e "${YELLOW}Found existing process on port 5001 (PID: $EXISTING_PID), terminating...${NC}"
    kill -9 $EXISTING_PID 2>/dev/null || true
    sleep 1
fi

# Cleanup function to kill backend when script exits
cleanup() {
    echo ""
    echo "Shutting down..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up trap to catch Ctrl+C and other exit signals
trap cleanup INT TERM EXIT

# Start backend in background
echo -e "${GREEN}Starting backend on http://localhost:5001...${NC}"
cd "$BACKEND_DIR"
source venv/bin/activate
python app.py &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"
echo ""

# Wait for backend to be ready
echo "Waiting for backend to start..."
for i in {1..10}; do
    if curl -s http://localhost:5001/api/courses > /dev/null 2>&1; then
        echo -e "${GREEN}Backend is ready!${NC}"
        break
    fi
    sleep 1
done

echo ""

# Start frontend (foreground)
echo -e "${GREEN}Starting frontend on http://localhost:5173...${NC}"
cd "$FRONTEND_DIR"
npm run dev
