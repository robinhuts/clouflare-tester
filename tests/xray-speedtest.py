#!/usr/bin/env python3
"""
Xray Speed Test
Test download/upload speed through Xray SOCKS5 proxy
"""
import time
import sys
import requests
from colorama import Fore, Style, init

init(autoreset=True)

# Proxy settings
SOCKS5_PROXY = "socks5://127.0.0.1:10808"
HTTP_PROXY = "http://127.0.0.1:10809"

def test_connectivity():
    """Test if Xray proxy is running and accessible"""
    print(f"{Fore.YELLOW}[1/4] Testing proxy connectivity...")
    
    proxies = {
        'http': SOCKS5_PROXY,
        'https': SOCKS5_PROXY
    }
    
    try:
        response = requests.get(
            'https://api.ipify.org?format=json',
            proxies=proxies,
            timeout=10
        )
        
        if response.status_code == 200:
            ip_data = response.json()
            print(f"{Fore.GREEN}✓ Proxy connected successfully!")
            print(f"{Fore.CYAN}  Exit IP: {ip_data['ip']}")
            return True
        else:
            print(f"{Fore.RED}✗ Proxy connection failed (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}✗ Proxy not accessible: {e}")
        print(f"{Fore.YELLOW}  Make sure Xray is running on port 10808")
        return False

def test_latency():
    """Test latency through proxy"""
    print(f"\n{Fore.YELLOW}[2/4] Testing latency...")
    
    proxies = {
        'http': SOCKS5_PROXY,
        'https': SOCKS5_PROXY
    }
    
    test_urls = [
        'https://cloudflare.com',
        'https://google.com',
        'https://api.ipify.org'
    ]
    
    latencies = []
    
    for url in test_urls:
        try:
            start = time.time()
            response = requests.get(url, proxies=proxies, timeout=10)
            latency = (time.time() - start) * 1000  # Convert to ms
            
            if response.status_code == 200:
                latencies.append(latency)
                print(f"{Fore.GREEN}  ✓ {url}: {latency:.2f}ms")
            else:
                print(f"{Fore.YELLOW}  ⚠ {url}: Failed (status {response.status_code})")
                
        except Exception as e:
            print(f"{Fore.RED}  ✗ {url}: {e}")
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        print(f"{Fore.CYAN}  Average latency: {avg_latency:.2f}ms")
        return avg_latency
    else:
        print(f"{Fore.RED}  Failed to measure latency")
        return None

def test_download_speed():
    """Test download speed through proxy"""
    print(f"\n{Fore.YELLOW}[3/4] Testing download speed...")
    
    proxies = {
        'http': SOCKS5_PROXY,
        'https': SOCKS5_PROXY
    }
    
    # Test with different file sizes
    test_files = [
        ('1MB', 'https://speed.cloudflare.com/__down?bytes=1000000'),
        ('5MB', 'https://speed.cloudflare.com/__down?bytes=5000000'),
        ('10MB', 'https://speed.cloudflare.com/__down?bytes=10000000'),
    ]
    
    speeds = []
    
    for name, url in test_files:
        try:
            print(f"{Fore.CYAN}  Testing with {name} file...", end=' ')
            
            start = time.time()
            response = requests.get(url, proxies=proxies, timeout=30, stream=True)
            
            total_bytes = 0
            for chunk in response.iter_content(chunk_size=8192):
                total_bytes += len(chunk)
            
            duration = time.time() - start
            speed_mbps = (total_bytes * 8 / duration) / 1_000_000  # Convert to Mbps
            
            speeds.append(speed_mbps)
            print(f"{Fore.GREEN}{speed_mbps:.2f} Mbps")
            
        except Exception as e:
            print(f"{Fore.RED}Failed: {e}")
    
    if speeds:
        avg_speed = sum(speeds) / len(speeds)
        print(f"{Fore.CYAN}  Average download speed: {avg_speed:.2f} Mbps")
        return avg_speed
    else:
        print(f"{Fore.RED}  Failed to measure download speed")
        return None

def test_real_usage():
    """Test with real-world websites"""
    print(f"\n{Fore.YELLOW}[4/4] Testing real-world usage...")
    
    proxies = {
        'http': SOCKS5_PROXY,
        'https': SOCKS5_PROXY
    }
    
    websites = [
        ('Google', 'https://www.google.com'),
        ('YouTube', 'https://www.youtube.com'),
        ('GitHub', 'https://github.com'),
        ('Twitter', 'https://twitter.com'),
    ]
    
    for name, url in websites:
        try:
            start = time.time()
            response = requests.get(url, proxies=proxies, timeout=10)
            duration = (time.time() - start) * 1000
            
            if response.status_code == 200:
                print(f"{Fore.GREEN}  ✓ {name}: {duration:.2f}ms (status {response.status_code})")
            else:
                print(f"{Fore.YELLOW}  ⚠ {name}: {duration:.2f}ms (status {response.status_code})")
                
        except Exception as e:
            print(f"{Fore.RED}  ✗ {name}: {e}")

def print_summary(latency, download_speed):
    """Print test summary"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}SPEED TEST SUMMARY")
    print(f"{Fore.CYAN}{'='*60}")
    
    if latency:
        print(f"{Fore.GREEN}Average Latency: {latency:.2f}ms")
        
        if latency < 50:
            rating = "Excellent"
            color = Fore.GREEN
        elif latency < 100:
            rating = "Good"
            color = Fore.CYAN
        elif latency < 200:
            rating = "Fair"
            color = Fore.YELLOW
        else:
            rating = "Poor"
            color = Fore.RED
        
        print(f"{color}Latency Rating: {rating}")
    
    if download_speed:
        print(f"{Fore.GREEN}Average Download: {download_speed:.2f} Mbps")
        
        if download_speed > 50:
            rating = "Excellent"
            color = Fore.GREEN
        elif download_speed > 20:
            rating = "Good"
            color = Fore.CYAN
        elif download_speed > 10:
            rating = "Fair"
            color = Fore.YELLOW
        else:
            rating = "Poor"
            color = Fore.RED
        
        print(f"{color}Speed Rating: {rating}")
    
    print(f"{Fore.CYAN}{'='*60}\n")

def main():
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("=" * 60)
    print("XRAY SPEED TEST")
    print("=" * 60)
    print(f"{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Testing Xray connection speed via SOCKS5 proxy")
    print(f"{Fore.YELLOW}Proxy: {SOCKS5_PROXY}\n")
    
    # Test connectivity first
    if not test_connectivity():
        print(f"\n{Fore.RED}Cannot proceed without proxy connection!")
        print(f"{Fore.YELLOW}Start Xray with: .\\xray\\xray.exe run -c xray-zoom-config.json")
        return 1
    
    # Run tests
    latency = test_latency()
    download_speed = test_download_speed()
    test_real_usage()
    
    # Print summary
    print_summary(latency, download_speed)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Test interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
