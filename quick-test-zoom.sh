#!/usr/bin/bash
# Quick test untuk zoom-style config (Termux/Linux)
# Sesuaikan dengan server URL Anda

echo "============================================"
echo "CLOUDFLARE IP TESTER - ZOOM STYLE"
echo "============================================"
echo ""

# Ganti dengan server URL Anda!
SERVER_URL="vless://4b70b98a-1b39-4d76-880a-243ba5c5e03b@point.natss.store:443?type=ws&security=tls&path=/vless&sni=point.natss.store"

# IP range yang akan di-test
IP_RANGE="170.114.45.1-20"

# DNS domain untuk mapping
DNS_DOMAIN="api.ovo.id"

echo "Testing IP range: $IP_RANGE"
echo "DNS domain: $DNS_DOMAIN"
echo ""
echo "CATATAN: Edit file ini untuk mengganti SERVER_URL dengan credentials Anda!"
echo ""

read -p "Press Enter to continue..."

python main.py \
  --range "$IP_RANGE" \
  --server-url "$SERVER_URL" \
  --zoom-style \
  --dns-domain "$DNS_DOMAIN" \
  --timeout 10 \
  --concurrent 10 \
  --verbose

echo ""
read -p "Press Enter to exit..."
