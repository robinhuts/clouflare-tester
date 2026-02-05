#!/usr/bin/env python3
"""
Zoom SNI Tester - Test IPs using support.zoom.us SNI
This is for testing SNI bug method with zero-quota SIM cards
"""
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from xray_manager import XrayManager
from ip_generator import IPGenerator
from config_generator import XrayConfigGenerator
from connection_tester import ConnectionTester
from reporter import Reporter
from url_parser import URLParser
from colorama import Fore, Style, init
import time

init(autoreset=True)


def get_zoom_ips():
    """Get Zoom.us IPs for testing"""
    # These are some known Zoom IPs
    # You can add more IPs here
    return [
        "3.7.35.0/24",      # Zoom AWS ranges
        "3.21.137.0/24",
        "3.22.11.0/24",
        "3.23.93.0/24",
        "3.25.41.0/24",
        "3.25.42.0/24",
        "3.25.49.0/24",
        "8.5.128.0/23",     # Zoom direct ranges
        "147.124.96.0/19",
        "170.114.0.0/16",   # Cloudflare (works with Zoom SNI)
        "104.16.0.0/13",    # Cloudflare popular range
    ]


def main():
    parser = argparse.ArgumentParser(
        description='Test IPs using support.zoom.us SNI for zero-quota',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with your vless server using Zoom SNI
  python zoom-sni-test.py --server-url "vless://..." --range "104.16.0.1-100"
  
  # Test known Zoom IPs
  python zoom-sni-test.py --server-url "vless://..." --zoom-ips
  
  # Test Cloudflare with Zoom SNI
  python zoom-sni-test.py --server-url "vless://..." --range "104.16.0.0/24"
        """
    )
    
    parser.add_argument('--server-url', type=str, required=True,
                       help='vless://... or vmess://... URL')
    
    range_group = parser.add_mutually_exclusive_group(required=True)
    range_group.add_argument('--range', type=str,
                           help='IP range to test')
    range_group.add_argument('--zoom-ips', action='store_true',
                           help='Test known Zoom IP ranges')
    range_group.add_argument('--cloudflare-ips', action='store_true',
                           help='Test Cloudflare IPs with Zoom SNI')
    
    parser.add_argument('--timeout', type=int, default=8,
                       help='Timeout per IP (default: 8)')
    parser.add_argument('--concurrent', type=int, default=20,
                       help='Concurrent tests (default: 20)')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize
    reporter = Reporter()
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*60}")
    print(f"Zoom SNI Tester - Zero-Quota Testing")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    # Parse server URL
    print(f"{Fore.YELLOW}[1/5] Parsing server configuration...")
    try:
        server_config = URLParser.parse_url(args.server_url)
        print(f"{Fore.GREEN}Server: {server_config['address']}:{server_config['port']}")
        print(f"{Fore.YELLOW}Original SNI: {server_config['sni']}")
        
        # OVERRIDE SNI dengan support.zoom.us
        server_config['sni'] = 'support.zoom.us'
        server_config['host'] = 'support.zoom.us'
        
        print(f"{Fore.GREEN}✓ Overriding SNI to: {Fore.CYAN}support.zoom.us")
        print(f"{Fore.GREEN}This will test SNI bug for zero-quota!\n")
        
    except Exception as e:
        print(f"{Fore.RED}Error parsing server URL: {e}")
        return 1
    
    # Ensure Xray installed
    print(f"{Fore.YELLOW}[2/5] Checking Xray installation...")
    xray_manager = XrayManager()
    if not xray_manager.ensure_installed():
        print(f"{Fore.RED}Failed to install Xray!")
        return 1
    xray_path = xray_manager.get_xray_path()
    print(f"{Fore.GREEN}✓ Xray ready\n")
    
    # Generate IP list
    print(f"{Fore.YELLOW}[3/5] Generating IP list...")
    
    if args.zoom_ips:
        print(f"{Fore.CYAN}Using Zoom IP ranges:")
        zoom_ranges = get_zoom_ips()
        all_ips = []
        for ip_range in zoom_ranges:
            try:
                ips = IPGenerator.parse_range(ip_range)
                all_ips.extend(ips)
                print(f"  {ip_range}: {len(ips):,} IPs")
            except:
                pass
        ip_list = all_ips
    elif args.cloudflare_ips:
        print(f"{Fore.CYAN}Using Cloudflare ranges with Zoom SNI:")
        cf_ranges = IPGenerator.get_cloudflare_ranges()
        all_ips = []
        for ip_range in cf_ranges[:5]:  # Only first 5 ranges to keep it reasonable
            ips = IPGenerator.parse_range(ip_range)
            all_ips.extend(ips)
            print(f"  {ip_range}: {len(ips):,} IPs")
        ip_list = all_ips
    else:
        ip_list = IPGenerator.parse_range(args.range)
    
    print(f"{Fore.GREEN}Total IPs to test: {len(ip_list):,}\n")
    
    # Generate configs
    print(f"{Fore.YELLOW}[4/5] Generating Xray configs with Zoom SNI...")
    config_generator = XrayConfigGenerator()
    
    ip_configs = []
    for ip in ip_list:
        xray_config = config_generator.generate_config_from_server(server_config, ip)
        ip_configs.append((ip, xray_config))
    
    print(f"{Fore.GREEN}Generated {len(ip_configs)} configurations\n")
    
    # Test connections
    print(f"{Fore.YELLOW}[5/5] Testing connections...")
    print(f"{Fore.CYAN}SNI Header: support.zoom.us")
    print(f"{Fore.CYAN}Concurrent: {args.concurrent}")
    print(f"{Fore.CYAN}Timeout: {args.timeout}s\n")
    
    tester = ConnectionTester(xray_path=xray_path, timeout=args.timeout)
    pbar = reporter.create_progress_bar(len(ip_configs), "Testing IPs")
    
    def progress_callback(completed, total, result):
        pbar.update(1)
        if args.verbose:
            reporter.print_live_result(result)
    
    start_time = time.time()
    results = tester.test_multiple_ips(
        ip_configs,
        max_workers=args.concurrent,
        progress_callback=progress_callback
    )
    elapsed_time = time.time() - start_time
    pbar.close()
    
    print(f"\n{Fore.GREEN}Testing completed in {elapsed_time:.1f}s\n")
    
    # Generate reports
    stats = ConnectionTester.get_statistics(results)
    reporter.print_summary(results, stats)
    reporter.print_top_ips(results, top_n=10)
    
    # Save results
    reporter.save_json(results, filename="zoom-sni-results.json")
    reporter.save_csv(results, filename="zoom-sni-results.csv")
    reporter.save_working_ips(results, filename="zoom-working-ips.txt")
    
    config = {
        'protocol': server_config['protocol'],
        'sni': 'support.zoom.us',
        'port': server_config['port'],
        'timeout': args.timeout,
        'concurrent': args.concurrent
    }
    reporter.generate_full_report(results, stats, config)
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}✓ All done!")
    print(f"{Fore.CYAN}Working IPs saved to: {Fore.WHITE}results/zoom-working-ips.txt")
    print(f"{Fore.CYAN}Use these IPs with SNI 'support.zoom.us' for zero-quota!\n")
    
    return 0 if stats['successful'] > 0 else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
