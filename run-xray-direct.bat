@echo off
REM Run Xray dengan Direct Config (Tanpa IP Mapping)
echo ============================================
echo STARTING XRAY - DIRECT CONNECTION
echo ============================================
echo.
echo Config: xray-direct-config.json
echo Server: point.natss.store:443 (DIRECT)
echo No Cloudflare IP mapping
echo.
echo SOCKS Proxy: 127.0.0.1:10808
echo HTTP Proxy:  127.0.0.1:10809
echo.
echo Press Ctrl+C to stop Xray
echo ============================================
echo.

.\xray\xray.exe run -c xray-direct-config.json

pause
