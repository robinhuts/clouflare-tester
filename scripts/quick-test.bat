@echo off
REM Quick Test Script for Cloudflare IP Tester
REM Edit the VLESS_URL below with your actual vless URL

echo ============================================
echo  CLOUDFLARE IP TESTER - Bug/SNI Edition
echo ============================================
echo.

REM Your vless URL here
set VLESS_URL=vless://4b70b98a-1b39-4d76-880a-243ba5c50000@point.natss.store:443?path=/vless^&security=tls^&encryption=none^&host=point.natss.store^&type=ws^&sni=point.natss.store#yamete09

echo Choose testing mode:
echo.
echo 1. Quick Test (104.16.0.1-100, fast)
echo 2. Medium Test (104.16.0.0/24, ~250 IPs)
echo 3. Large Test (104.16.0.0/16, ~65k IPs - SLOW!)
echo 4. ALL Cloudflare IPs (VERY SLOW!)
echo 5. Custom range
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    echo Running: Quick Test (100 IPs)
    python ..\main.py --server-url "%VLESS_URL%" --range "104.16.0.1-100" --timeout 8 --concurrent 20
) else if "%choice%"=="2" (
    echo Running: Medium Test (~250 IPs)
    python ..\main.py --server-url "%VLESS_URL%" --range "104.16.0.0/24" --timeout 8 --concurrent 30
) else if "%choice%"=="3" (
    echo Running: Large Test (~65k IPs - This will take a while!)
    python ..\main.py --server-url "%VLESS_URL%" --range "104.16.0.0/16" --timeout 5 --concurrent 50
) else if "%choice%"=="4" (
    echo Running: ALL Cloudflare IPs (This will take HOURS!)
    python ..\main.py --server-url "%VLESS_URL%" --range "@cloudflare-ips.txt" --timeout 5 --concurrent 100
) else if "%choice%"=="5" (
    set /p custom_range="Enter IP range (e.g., 104.16.0.1-50): "
    echo Running: Custom range - !custom_range!
    python ..\main.py --server-url "%VLESS_URL%" --range "!custom_range!" --timeout 8 --concurrent 20
) else (
    echo Invalid choice!
    goto end
)

echo.
echo ========================================
echo Test completed!
echo Check results/ folder for output files
echo ========================================

:end
pause
