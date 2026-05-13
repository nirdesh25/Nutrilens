#!/bin/bash

# NutriLens AI - Automated Setup Script
# This script sets up the entire application for local development

set -e

echo "=========================================="
echo "NutriLens AI - Automated Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    echo "Please install Node.js 18 or higher"
    exit 1
fi

echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"
echo ""

# Backend Setup
echo "=========================================="
echo "Setting up Backend..."
echo "=========================================="
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    
    # Generate secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # Update .env with generated secret key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    else
        sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    fi
    
    echo -e "${YELLOW}⚠ Please update DATABASE_URL in backend/.env${NC}"
fi

echo -e "${GREEN}✓ Backend setup complete${NC}"
cd ..
echo ""

# Frontend Setup
echo "=========================================="
echo "Setting up Frontend..."
echo "=========================================="
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env.local file if it doesn't exist
if [ ! -f .env.local ]; then
    echo "Creating .env.local file..."
    cp .env.example .env.local
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"
cd ..
echo ""

# Summary
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure Database:"
echo "   - Update DATABASE_URL in backend/.env"
echo "   - Create PostgreSQL database"
echo ""
echo "2. Start Backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
echo "   python main.py"
echo ""
echo "3. Start Frontend (in new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Visit http://localhost:3000"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
