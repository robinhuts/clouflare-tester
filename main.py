#!/usr/bin/env python3
"""
Cloudflare IP Tester with Xray - Interactive CLI & Automation
Main application with interactive mode and CLI arguments
"""
import sys
import os
import time
import argparse
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
    # clear_screen() # Only clear in interactive mode
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
    print(f"\n{Fore.YELLOW}{'='*70}")
    print(f"{Fore.YELLOW}TEST PARAMETERS")
    print(f"{Fore.YELLOW}{'='*70}\n")
    
    timeout = get_input("Timeout per IP (seconds)", "10")
    concurrent = get_input("Batch size (Concurrent IPs)", "20")
    top_ips = get_input("Number of top IPs to display", "20")
    
    try:
        timeout = int(timeout)
        concurrent = int(concurrent)
        top_ips = int(top_ips)
        
        return timeout, concurrent, top_ips
    except ValueError:
        print(f"{Fore.RED}Invalid numbers. Using defaults.")
        return 10, 20, 20


def confirm_and_run(config):
    """Show summary and confirm before running"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}TEST CONFIGURATION SUMMARY")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    print(f"{Fore.WHITE}IP Range: {Fore.GREEN}{config['ip_range_display']}")
    print(f"{Fore.WHITE}Server: {Fore.GREEN}{config['server_display']}")
    print(f"{Fore.WHITE}Bug/SNI Mode: {Fore.GREEN}{config['zoom_style']}")
    print(f"{Fore.WHITE}Timeout: {Fore.GREEN}{config['timeout']}s")
    print(f"{Fore.WHITE}Batch Size: {Fore.GREEN}{config['concurrent']}")
    
    print(f"\n{Fore.YELLOW}Estimated time: ~{config['estimated_time']} minutes")
    
    # If auto-run is enabled (from CLI), skip confirmation
    if config.get('auto_run'):
        return True
    
    if not get_yes_no(f"\n{Fore.CYAN}Start testing?", "y"):
        print(f"{Fore.RED}Test cancelled by user.")
        return False
    
    return True


def run_test(config):
    """Execute the test"""
    # clear_screen()
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}STARTING TEST...")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    # Step 1: Ensure Xray
    print(f"{Fore.YELLOW}[1/4] Checking Xray installation...")
    xray_manager = XrayManager()
    if not xray_manager.ensure_installed():
        print(f"{Fore.RED}Failed to install Xray.")
        return False
    xray_path = xray_manager.get_xray_path()
    print(f"{Fore.GREEN}✓ Xray ready\n")
    
    # Step 2: Generate IPs
    print(f"{Fore.YELLOW}[2/4] Generating IP list...")
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
    
    # Step 3: Test connections (Batch Mode)
    print(f"{Fore.YELLOW}[3/4] Testing connections (Batch Mode)...")
    
    config_generator = XrayConfigGenerator()
    tester = ConnectionTester(xray_path=xray_path, timeout=config['timeout'])
    reporter = Reporter()
    
    batch_size = config['concurrent']
    total_ips = len(ip_list)
    results = []
    
    pbar = reporter.create_progress_bar(total_ips, "Testing IPs")
    
    def progress_callback(completed, total, result):
        pbar.update(1)
        
    start_time = time.time()
    
    # Chunk IPs for batch processing
    # If using real server and zoom style, efficient batching is possible
    # If using 'multi_domain', handled differently? 
    # For now assuming single domain testing for batch optimization
    
    # Split IPs into chunks
    chunks = [ip_list[i:i + batch_size] for i in range(0, len(ip_list), batch_size)]
    
    for chunk_idx, chunk in enumerate(chunks):
        if config['server_config']:
            if config['zoom_style']:
                 # Batch config with Zoom/Bug Style
                 xray_config = config_generator.generate_batch_config(
                     chunk, 
                     config['server_config'],
                     dns_domain=config['dns_domain'],
                     use_domain_in_address=config['use_domain_address'],
                     base_port=20000
                 )
            else:
                 # TODO: Add batch support for Direct/Real server without Zoom Style?
                 # For now, fallback to single-IP style if not Zoom Style? 
                 # Or just use the same batch generator but ignore dns_domain?
                 # Actually generate_batch_config supports generic server config.
                 xray_config = config_generator.generate_batch_config(
                     chunk,
                     config['server_config'],
                     dns_domain="cloudflare.com", # Irrelevant for non-zoom?
                     use_domain_in_address=False, # Direct IP
                     base_port=20000
                 )
        else:
             # Fake server / Direct mode - not supported in batch yet? 
             # For now, let's assume server_config is present or we handle it efficiently
             # If no server_config, we can't use generate_batch_config easily because it needs protocol info.
             # Fallback?
             pass
        
        # Run batch
        if config['server_config']:
            batch_results = tester.test_batch_config(
                xray_config, 
                chunk, 
                base_port=20000,
                progress_callback=progress_callback
            )
            results.extend(batch_results)
        else:
            # Fallback for no-server-config (Fake/Direct test) - unlikely use case for this tool
            # But let's handle it for completeness or error out
            pass

    elapsed_time = time.time() - start_time
    pbar.close()
    
    print(f"\n{Fore.GREEN}✓ Testing completed in {elapsed_time:.1f}s\n")
    
    # Step 5: Generate reports
    print(f"{Fore.YELLOW}[4/4] Generating reports...")
    stats = ConnectionTester.get_statistics(results)
    
    reporter.print_summary(results, stats)
    reporter.print_top_ips(results, top_n=config['top_ips'])
    
    reporter.save_json(results)
    # reporter.save_csv(results) # Disabled by user request
    reporter.save_working_ips(results)
    reporter.generate_full_report(results, stats, config)
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}✓ All done!")
    print(f"{Fore.CYAN}Check results folder for detailed reports.\n")
    
    return stats['successful'] > 0


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Cloudflare IP Tester')
    
    parser.add_argument('--url', help='VLESS/VMESS/Trojan URL')
    parser.add_argument('--file', help='Input file with IPs/Ranges (e.g. @ips.txt)')
    parser.add_argument('--range', help='IP Range or CIDR (e.g. 104.16.0.0/24)')
    parser.add_argument('--domain', help='Domain to scan for IPs (e.g. site.com)')
    parser.add_argument('--bug', help='Bug/SNI Domain (e.g. api.ovo.id)')
    parser.add_argument('--quick', action='store_true', help='Run quick test (172.64.0.1-100)')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout per IP in seconds')
    parser.add_argument('--concurrent', type=int, default=20, help='Batch size (concurrent requests)')
    parser.add_argument('--auto', action='store_true', help='Auto run without confirmation')
    
    return parser.parse_args()


def main():
    """Main entry point"""
    try:
        print_banner()
        
        args = parse_arguments()
        
        # Check if arguments provided for automation
        if args.url or args.file or args.range or args.domain or args.quick:
            # CLI Mode
            
            # Determine IP Source
            ip_range = None
            use_cloudflare = False
            test_domain = None
            
            if args.quick:
                ip_range = "172.64.0.1-100"
            elif args.file:
                ip_range = args.file if args.file.startswith('@') else f"@{args.file}"
            elif args.range:
                ip_range = args.range
            elif args.domain:
                # resolve
                all_ips, cf_ips = resolve_domain_to_cloudflare_ips(args.domain)
                if cf_ips:
                    ip_range = ",".join(cf_ips)
                    test_domain = args.domain
                elif all_ips:
                    ip_range = ",".join(all_ips)
                    test_domain = args.domain # Warning: non-CF
            
            if not ip_range:
                print(f"{Fore.RED}Error: No valid IP source provided.")
                return 1
            
            # Server Config
            server_config = None
            if args.url:
                try:
                    server_config = URLParser.parse_url(args.url)
                except Exception as e:
                    print(f"{Fore.RED}Error parsing URL: {e}")
                    return 1
            
            # Build Config
            config = {
                'ip_range': ip_range,
                'use_cloudflare_ranges': False,
                'test_domain': test_domain,
                'ip_range_display': ip_range,
                'server_url': args.url,
                'server_config': server_config,
                'server_display': server_config['address'] if server_config else "None",
                'zoom_style': bool(args.bug),
                'dns_domain': args.bug,
                'use_domain_address': bool(args.bug), # Implicitly true if bug provided via CLI
                'multi_domain': False,
                'domains_list': None,
                'timeout': args.timeout,
                'concurrent': args.concurrent,
                'top_ips': 20,
                'estimated_time': "Unknown",
                'auto_run': args.auto
            }
            
            if confirm_and_run(config):
                success = run_test(config)
                return 0 if success else 1
            return 0
            
        else:
            # Interactive Mode (Legacy)
            clear_screen()
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
            
            config = {
                'ip_range': ip_range,
                'use_cloudflare_ranges': use_cloudflare,
                'test_domain': domain,
                'ip_range_display': "All Cloudflare ranges" if use_cloudflare else ip_range,
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
                'estimated_time': 5 if ip_range and "1-100" in ip_range else "10+",
                'auto_run': False
            }
            
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
