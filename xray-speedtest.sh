#!/usr/bin/bash
# Xray Speed Test - Bash Wrapper for Termux/Linux
echo "============================================"
echo "XRAY CONNECTION SPEED TEST"
echo "============================================"
echo ""
echo "Testing speed through Xray proxy..."
echo "This will measure:"
echo "  - Proxy connectivity"
echo "  - Latency"
echo "  - Download speed"
echo "  - Real-world website loading"
echo ""
echo "Make sure Xray is running!"
echo "============================================"
echo ""

python xray-speedtest.py

echo ""
read -p "Press Enter to exit..."
