#!/usr/bin/bash
# Termux Setup Script for Cloudflare IP Tester
# This script will set up all dependencies needed to run the tool on Termux

echo "============================================"
echo " CLOUDFLARE IP TESTER - Bug/SNI Setup"
echo "============================================"
echo ""

# Update packages
echo "[1/5] Updating Termux packages..."
pkg update -y

# Install Python
echo ""
echo "[2/5] Installing Python..."
pkg install -y python

# Install dependencies
echo ""
echo "[3/5] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make shell scripts executable
echo ""
echo "[4/5] Making shell scripts executable..."
chmod +x quick-test.sh

# Test installation
echo ""
echo "[5/5] Testing installation..."
python --version
python -c "import requests, tqdm, colorama; print('✓ All Python packages installed successfully')"

echo ""
echo "============================================"
echo "✓ SETUP COMPLETE!"
echo "============================================"
echo ""
echo "You can now run the tool with:"
echo "  python ../main.py          # Interactive mode"
echo "  bash quick-test.sh      # Quick test script"
echo ""
echo "Xray will be automatically downloaded on first run."
echo ""
