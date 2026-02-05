#!/usr/bin/bash
# Quick Test Script for Cloudflare IP Tester (Termux/Linux)
# Edit the VLESS_URL below with your actual vless URL

echo "========================================"
echo "Cloudflare IP Tester - Quick Start"
echo "========================================"
echo ""

# Your vless URL here
VLESS_URL="vless://4b70b98a-1b39-4d76-880a-243ba5c5e03b@point.natss.store:443?path=/vless&security=tls&encryption=none&host=point.natss.store&type=ws&sni=point.natss.store#yamete09"

echo "Choose testing mode:"
echo ""
echo "1. Quick Test (104.16.0.1-100, fast)"
echo "2. Medium Test (104.16.0.0/24, ~250 IPs)"
echo "3. Large Test (104.16.0.0/16, ~65k IPs - SLOW!)"
echo "4. ALL Cloudflare IPs (VERY SLOW!)"
echo "5. Custom range"
echo ""

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo "Running: Quick Test (100 IPs)"
        python ../main.py --server-url "$VLESS_URL" --range "104.16.0.1-100" --timeout 8 --concurrent 20
        ;;
    2)
        echo "Running: Medium Test (~250 IPs)"
        python ../main.py --server-url "$VLESS_URL" --range "104.16.0.0/24" --timeout 8 --concurrent 30
        ;;
    3)
        echo "Running: Large Test (~65k IPs - This will take a while!)"
        python ../main.py --server-url "$VLESS_URL" --range "104.16.0.0/16" --timeout 5 --concurrent 50
        ;;
    4)
        echo "Running: ALL Cloudflare IPs (This will take HOURS!)"
        python ../main.py --server-url "$VLESS_URL" --range "@cloudflare-ips.txt" --timeout 5 --concurrent 100
        ;;
    5)
        read -p "Enter IP range (e.g., 104.16.0.1-50): " custom_range
        echo "Running: Custom range - $custom_range"
        python ../main.py --server-url "$VLESS_URL" --range "$custom_range" --timeout 8 --concurrent 20
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "Test completed!"
echo "Check results/ folder for output files"
echo "========================================"
