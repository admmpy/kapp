#!/bin/bash

# Setup script for Kapp
# Run this once on a fresh checkout to install dependencies and seed the database

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "        Kapp Setup Script"
echo "========================================"
echo ""

# Check for Python 3.10+
echo -e "${BLUE}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3.10 or higher:"
    echo "  - macOS: brew install python@3.10"
    echo "  - Ubuntu: sudo apt install python3.10 python3.10-venv"
    echo "  - Windows: Download from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}Error: Python 3.10 or higher is required (found $PYTHON_VERSION).${NC}"
    echo "Please upgrade Python and try again."
    exit 1
fi
echo -e "${GREEN}Python $PYTHON_VERSION found.${NC}"

# Check for Node.js 18+
echo -e "${BLUE}Checking Node.js version...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed.${NC}"
    echo "Please install Node.js 18 or higher:"
    echo "  - macOS: brew install node"
    echo "  - Ubuntu: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
    echo "  - Windows: Download from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}Error: Node.js 18 or higher is required (found v$(node -v)).${NC}"
    echo "Please upgrade Node.js and try again."
    exit 1
fi
echo -e "${GREEN}Node.js $(node -v) found.${NC}"

echo ""

# Create Python virtual environment
echo -e "${BLUE}Setting up Python virtual environment...${NC}"
if [ ! -d "$BACKEND_DIR/venv" ]; then
    python3 -m venv "$BACKEND_DIR/venv"
    echo -e "${GREEN}Created virtual environment at backend/venv${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists, skipping creation.${NC}"
fi

# Activate venv and install Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
source "$BACKEND_DIR/venv/bin/activate"
pip install --upgrade pip -q
pip install -r "$BACKEND_DIR/requirements.txt" -q
echo -e "${GREEN}Python dependencies installed.${NC}"

echo ""

# Set up backend .env file
echo -e "${BLUE}Setting up backend environment...${NC}"
if [ ! -f "$BACKEND_DIR/.env" ]; then
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"

    # Generate a secure SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

    # Replace the placeholder SECRET_KEY (cross-platform sed)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-generated-secret-key-here/$SECRET_KEY/" "$BACKEND_DIR/.env"
    else
        sed -i "s/your-generated-secret-key-here/$SECRET_KEY/" "$BACKEND_DIR/.env"
    fi

    echo -e "${GREEN}Created backend/.env with generated SECRET_KEY${NC}"
else
    echo -e "${YELLOW}backend/.env already exists, skipping.${NC}"
fi

# Set up frontend .env file
echo -e "${BLUE}Setting up frontend environment...${NC}"
if [ ! -f "$FRONTEND_DIR/.env" ]; then
    cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env"
    echo -e "${GREEN}Created frontend/.env${NC}"
else
    echo -e "${YELLOW}frontend/.env already exists, skipping.${NC}"
fi

echo ""

# Install frontend dependencies
echo -e "${BLUE}Installing frontend dependencies...${NC}"
cd "$FRONTEND_DIR"
npm install --silent
echo -e "${GREEN}Frontend dependencies installed.${NC}"

echo ""

# Import lesson content
echo -e "${BLUE}Importing lesson content into database...${NC}"
cd "$BACKEND_DIR"
python scripts/import_lessons.py --force

echo ""
echo "========================================"
echo -e "${GREEN}        Setup Complete!${NC}"
echo "========================================"
echo ""
echo "To start the application, run:"
echo "  ./quickstart.sh"
echo ""
echo "This will start:"
echo "  - Backend API at http://localhost:5001"
echo "  - Frontend at http://localhost:5173"
echo ""
