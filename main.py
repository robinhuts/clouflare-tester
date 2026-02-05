#!/usr/bin/env python3
"""
Cloudflare IP Tester with Xray - Interactive CLI
Main application with interactive mode
"""
import sys
import os
import time
from pathlib import Path
from colorama import Fore, Style, init

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from xray_manager import XrayManager
from ip_generator import IPGenerator
from config_generator import XrayConfigGenerator
from connection_tester import ConnectionTester
from reporter import Reporter
from url_parser import URLParser
from domain_resolver import resolve_domain_to_cloudflare_ips

init(autoreset=True)


def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print application banner"""
    clear_screen()
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("=" * 70)
    print("      CLOUDFLARE IP TESTER - Bug/SNI Zero-Quota      ".center(70))
    print("=" * 70)
    print(f"{Style.RESET_ALL}\n")


def get_input(prompt, default=None, choices=None):
    """Get user input with validation"""
    while True:
        if default:
            user_input = input(f"{Fore.CYAN}{prompt} [{default}]: {Style.RESET_ALL}").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{Fore.CYAN}{prompt}: {Style.RESET_ALL}").strip()
            
        if choices and user_input.lower() not in [c.lower() for c in choices]:
            print(f"{Fore.RED}Invalid choice. Please choose from: {', '.join(choices)}")
            continue
            
        if user_input:
            return user_input
        elif not default:
            print(f"{Fore.RED}This field is required!")
            continue


def get_yes_no(prompt, default='y'):
    """Get yes/no input"""
    response = get_input(f"{prompt} (y/n)", default)
    return response.lower() in ['y', 'yes']


def select_test_mode():
    """Select testing mode"""
    print(f"\n{Fore.YELLOW}{'='*70}")
    print(f"{Fore.YELLOW}SELECT TESTING MODE")
    print(f"{Fore.YELLOW}{'='*70}\n")
    
    print(f"{Fore.GREEN}1.{Fore.WHITE} Quick Test (100 IPs - ~5 mins)")
    print(f"{Fore.GREEN}2.{Fore.WHITE} Custom Range (e.g. 104.16.0.0/24)")
    print(f"{Fore.GREEN}3.{Fore.WHITE} Domain Scan (Find IPs for specific domain)")
    print(f"{Fore.GREEN}4.{Fore.WHITE} Load from File (cloudflare-ips.txt)")
    print(f"{Fore.GREEN}5.{Fore.WHITE} ALL Ranges (Hours!)")
    
    choice = get_input("\nSelect mode [1-5]", "1", ["1", "2", "3", "4", "5"])
    
    if choice == "1":
        # Quick test with small range
        print(f"\n{Fore.CYAN}Using quick test range: 172.64.0.1-100")
        return "172.64.0.1-100", False, None
    elif choice == "2":
        # Custom range
        print(f"\n{Fore.YELLOW}Examples:")
        print(f"  - CIDR: 104.16.0.0/24")
        print(f"  - Range: 172.64.0.1-100")
        print(f"  - Single IP: 104.16.0.1")
        ip_range = get_input("\nEnter IP range")
        return ip_range, False, None
    elif choice == "3":
        # Test domain
        print(f"\n{Fore.YELLOW}Examples:")
        print(f"  - api.ovo.id")
        print(f"  - support.zoom.us")
        print(f"  - teams.microsoft.com")
        domain = get_input("\nEnter domain/subdomain")
        
        print(f"\n{Fore.CYAN}Resolving {domain}...")
        try:
            all_ips, cf_ips = resolve_domain_to_cloudflare_ips(domain)
            
            if cf_ips:
                print(f"{Fore.GREEN}✓ Found {len(cf_ips)} Cloudflare IP(s):")
                for ip in cf_ips:
                    print(f"  - {ip}")
                
                if len(cf_ips) == 1:
                    return cf_ips[0], False, domain
                else:
                    # Create range from multiple IPs
                    ip_list = ",".join(cf_ips)
                    return ip_list, False, domain
            else:
                print(f"{Fore.YELLOW}⚠ No Cloudflare IPs found for {domain}")
                if all_ips:
                    print(f"{Fore.YELLOW}Found {len(all_ips)} non-Cloudflare IP(s): {all_ips}")
                    if get_yes_no("Test these IPs anyway?", "n"):
                        return ",".join(all_ips), False, domain
                
                if get_yes_no("Try another domain?", "y"):
                    return select_test_mode()
                return None, False, None
                
        except Exception as e:
            print(f"{Fore.RED}✗ Error resolving domain: {e}")
            if get_yes_no("Try again?", "y"):
                return select_test_mode()
            return None, False, None
            
    elif choice == "4":
        # From file
        filename = get_input("Enter filename", "@cloudflare-ips.txt")
        if not filename.startswith("@"):
            filename = "@" + filename
        return filename, False, None
    else:
        # All Cloudflare ranges
        if get_yes_no(f"\n{Fore.YELLOW}WARNING: This will test thousands of IPs! Continue?", "n"):
            return None, True, None
        else:
            print(f"{Fore.RED}Cancelled. Returning to mode selection...")
            return select_test_mode()


def configure_server():
    """Configure server settings"""
    clear_screen()
    print(f"\n{Fore.YELLOW}{'='*70}")
    print(f"{Fore.YELLOW}SERVER CONFIGURATION")
    print(f"{Fore.YELLOW}{'='*70}\n")
    
    use_real_server = get_yes_no("Use real server URL? (RECOMMENDED for actual testing)", "y")
    
    if use_real_server:
        print(f"\n{Fore.CYAN}Enter your VLESS/VMESS/Trojan server URL")
        print(f"{Fore.YELLOW}Example: vless://uuid@server.com:443?type=ws&security=tls&sni=server.com&path=/path")
        
        server_url = get_input("Server URL")
        
        try:
            server_config = URLParser.parse_url(server_url)
            print(f"\n{Fore.GREEN}✓ Server URL parsed successfully:")
            print(f"  Protocol: {server_config['protocol']}")
            print(f"  Server: {server_config['address']}:{server_config['port']}")
            print(f"  SNI: {server_config['sni']}")
            return server_url, server_config
        except Exception as e:
            print(f"{Fore.RED}✗ Error parsing server URL: {e}")
            if get_yes_no("Try again?", "y"):
                return configure_server()
            return None, None
    else:
        print(f"\n{Fore.YELLOW}⚠ Running without real server (testing tool only)")
        return None, None


def configure_zoom_style():
    """Configure zoom-style settings"""
    clear_screen()
    print(f"\n{Fore.YELLOW}{'='*70}")
    print(f"{Fore.YELLOW}BUG/SNI CONFIGURATION")
    print(f"{Fore.YELLOW}{'='*70}\n")
    
    use_zoom = get_yes_no("Enable Bug/SNI mode?", "y")
    
    if not use_zoom:
        return False, None, True, False, None
    
    # Single Bug/SNI target input
    dns_domain = get_input("Enter Bug/SNI target (e.g. api.ovo.id, support.zoom.us)", "api.ovo.id")
    use_domain_address = get_yes_no("Use domain in address field?", "y")
    
    print(f"\n{Fore.GREEN}✓ Bug/SNI mode enabled:")
    print(f"  Target: {dns_domain}")
    print(f"  Domain in address: {use_domain_address}")
    
    return True, dns_domain, use_domain_address, False, None


def configure_test_params():
    """Configure test parameters"""
    clear_screen()
    print(f"\n{Fore.YELLOW}{'='*70}")
    print(f"{Fore.YELLOW}TEST PARAMETERS")
    print(f"{Fore.YELLOW}{'='*70}\n")
    
    timeout = get_input("Timeout per IP (seconds)", "10")
    concurrent = get_input("Concurrent tests", "20")
    top_ips = get_input("Number of top IPs to display", "20")
    
    try:
        timeout = int(timeout)
        concurrent = int(concurrent)
        top_ips = int(top_ips)
        
        print(f"\n{Fore.GREEN}✓ Test parameters set:")
        print(f"  Timeout: {timeout}s")
        print(f"  Concurrent: {concurrent}")
        print(f"  Top IPs: {top_ips}")
        
        return timeout, concurrent, top_ips
    except ValueError:
        print(f"{Fore.RED}Invalid numbers. Using defaults.")
        return 10, 20, 20


def confirm_and_run(config):
    """Show summary and confirm before running"""
    clear_screen()
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}TEST CONFIGURATION SUMMARY")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    print(f"{Fore.WHITE}IP Range: {Fore.GREEN}{config['ip_range_display']}")
    print(f"{Fore.WHITE}Server: {Fore.GREEN}{config['server_display']}")
    print(f"{Fore.WHITE}Bug/SNI Mode: {Fore.GREEN}{config['zoom_style']}")
    print(f"{Fore.WHITE}Timeout: {Fore.GREEN}{config['timeout']}s")
    print(f"{Fore.WHITE}Concurrent: {Fore.GREEN}{config['concurrent']}")
    
    print(f"\n{Fore.YELLOW}Estimated time: ~{config['estimated_time']} minutes")
    
    if not get_yes_no(f"\n{Fore.CYAN}Start testing?", "y"):
        print(f"{Fore.RED}Test cancelled by user.")
        return False
    
    return True


def run_test(config):
    """Execute the test"""
    clear_screen()
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}STARTING TEST...")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    # Step 1: Ensure Xray
    print(f"{Fore.YELLOW}[1/5] Checking Xray installation...")
    xray_manager = XrayManager()
    if not xray_manager.ensure_installed():
        print(f"{Fore.RED}Failed to install Xray.")
        return False
    xray_path = xray_manager.get_xray_path()
    print(f"{Fore.GREEN}✓ Xray ready\n")
    
    # Step 2: Generate IPs
    print(f"{Fore.YELLOW}[2/5] Generating IP list...")
    try:
        if config['use_cloudflare_ranges']:
            cf_ranges = IPGenerator.get_cloudflare_ranges()
            all_ips = []
            for ip_range in cf_ranges:
                all_ips.extend(IPGenerator.parse_range(ip_range))
            ip_list = all_ips
        else:
            ip_list = IPGenerator.parse_range(config['ip_range'])
        
        print(f"{Fore.GREEN}✓ Generated {len(ip_list):,} IPs\n")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
        return False
    
    # Step 3: Generate configs
    print(f"{Fore.YELLOW}[3/5] Generating Xray configurations...")
    config_generator = XrayConfigGenerator()
    ip_configs = []
    
    if config.get('multi_domain') and config.get('domains_list'):
        # Multi-domain testing: test each IP with multiple domains
        print(f"{Fore.CYAN}Multi-domain mode: Testing {len(ip_list)} IP(s) × {len(config['domains_list'])} domain(s)")
        
        for ip in ip_list:
            for dns_domain in config['domains_list']:
                if config['server_config']:
                    xray_config = config_generator.generate_zoom_style_config(
                        config['server_config'], ip,
                        dns_domain=dns_domain,
                        use_domain_in_address=True
                    )
                    # Add metadata to track which domain+IP combo
                    ip_configs.append((f"{ip}@{dns_domain}", xray_config))
                else:
                    xray_config = config_generator.generate_direct_config(ip)
                    ip_configs.append((f"{ip}@{dns_domain}", xray_config))
    else:
        # Standard single domain/IP testing
        for ip in ip_list:
            if config['server_config']:
                if config['zoom_style']:
                    xray_config = config_generator.generate_zoom_style_config(
                        config['server_config'], ip,
                        dns_domain=config['dns_domain'],
                        use_domain_in_address=config['use_domain_address']
                    )
                else:
                    xray_config = config_generator.generate_config_from_server(
                        config['server_config'], ip
                    )
            else:
                xray_config = config_generator.generate_direct_config(ip)
            ip_configs.append((ip, xray_config))
    
    print(f"{Fore.GREEN}✓ Generated {len(ip_configs)} configurations\n")
    
    # Step 4: Test connections
    print(f"{Fore.YELLOW}[4/5] Testing connections...")
    tester = ConnectionTester(xray_path=xray_path, timeout=config['timeout'])
    reporter = Reporter()
    
    pbar = reporter.create_progress_bar(len(ip_configs), "Testing IPs")
    
    def progress_callback(completed, total, result):
        pbar.update(1)
    
    start_time = time.time()
    results = tester.test_multiple_ips(
        ip_configs,
        max_workers=config['concurrent'],
        progress_callback=progress_callback
    )
    elapsed_time = time.time() - start_time
    pbar.close()
    
    print(f"\n{Fore.GREEN}✓ Testing completed in {elapsed_time:.1f}s\n")
    
    # Step 5: Generate reports
    print(f"{Fore.YELLOW}[5/5] Generating reports...")
    stats = ConnectionTester.get_statistics(results)
    
    reporter.print_summary(results, stats)
    reporter.print_top_ips(results, top_n=config['top_ips'])
    
    reporter.save_json(results)
    reporter.save_csv(results)
    reporter.save_working_ips(results)
    reporter.generate_full_report(results, stats, config)
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}✓ All done!")
    print(f"{Fore.CYAN}Check results folder for detailed reports.\n")
    
    return stats['successful'] > 0


def main():
    """Main interactive application"""
    try:
        print_banner()
        
        # Step 1: Select test mode
        ip_range, use_cloudflare, domain = select_test_mode()
        
        if ip_range is None and not use_cloudflare:
            print(f"\n{Fore.RED}No valid IP range selected. Exiting.")
            return 1
        
        # Step 2: Configure server
        server_url, server_config = configure_server()
        
        # Step 3: Configure zoom-style
        zoom_style, dns_domain, use_domain_address, multi_domain, domains_list = configure_zoom_style()
        
        # Step 4: Configure test parameters
        timeout, concurrent, top_ips = configure_test_params()
        
        # Prepare config
        ip_range_display = "All Cloudflare ranges" if use_cloudflare else ip_range
        if domain:
            ip_range_display = f"{domain} ({ip_range})"
        
        config = {
            'ip_range': ip_range,
            'use_cloudflare_ranges': use_cloudflare,
            'test_domain': domain,
            'ip_range_display': ip_range_display,
            'server_url': server_url,
            'server_config': server_config,
            'server_display': server_config['address'] if server_config else "None (fake config)",
            'zoom_style': zoom_style,
            'dns_domain': dns_domain,
            'use_domain_address': use_domain_address,
            'multi_domain': multi_domain,
            'domains_list': domains_list,
            'timeout': timeout,
            'concurrent': concurrent,
            'top_ips': top_ips,
            'estimated_time': 5 if ip_range and "1-100" in ip_range else "10+"
        }
        
        # Step 5: Confirm and run
        if confirm_and_run(config):
            success = run_test(config)
            return 0 if success else 1
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Interrupted by user. Exiting...")
        return 130
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
