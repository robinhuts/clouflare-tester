#!/usr/bin/bash
# Run Xray dengan Zoom Config
echo "============================================"
echo "STARTING XRAY WITH ZOOM CONFIG"
echo "============================================"
echo ""
echo "Config: xray-zoom-config.json"
echo "Server: point.natss.store:443"
echo "DNS Mapping: api.ovo.id -> 170.114.45.6, 170.114.46.6"
echo ""
echo "SOCKS Proxy: 127.0.0.1:10808"
echo "HTTP Proxy:  127.0.0.1:10809"
echo ""
echo "Press Ctrl+C to stop Xray"
echo "============================================"
echo ""

./xray/xray run -c xray-zoom-config.json
