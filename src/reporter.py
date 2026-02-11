#!/usr/bin/env python3
"""
Reporter - Display and save testing results
"""
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)


class Reporter:
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def print_header(self, config: Dict):
        """Print test configuration header"""
        print("\n" + "="*60)
        print(f"{Fore.CYAN}{Style.BRIGHT}Cloudflare IP Tester with Xray")
        print("="*60)
        print(f"{Fore.YELLOW}Configuration:")
        print(f"  Protocol: {config.get('protocol', 'vmess')}")
        print(f"  SNI: {config.get('sni', 'cloudflare.com')}")
        print(f"  Port: {config.get('port', 443)}")
        print(f"  Timeout: {config.get('timeout', 5)}s")
        print(f"  Concurrent: {config.get('concurrent', 10)}")
        print("="*60 + "\n")
    
    def create_progress_bar(self, total: int, desc: str = "Testing") -> tqdm:
        """Create a progress bar"""
        return tqdm(
            total=total,
            desc=desc,
            unit="IP",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]',
            colour='cyan'
        )
    
    def print_live_result(self, result: Dict):
        """Print single result (for verbose mode)"""
        ip = result['ip']
        status = result['status']
        
        if status == 'success':
            latency = result['latency_ms']
            print(f"{Fore.GREEN}✓ {ip} - {latency:.0f}ms")
        else:
            error = result.get('error', 'Unknown error')
            print(f"{Fore.RED}✗ {ip} - {error}")
    
    def print_summary(self, results: List[Dict], stats: Dict):
        """Print summary of results"""
        print("\n" + "="*60)
        print(f"{Fore.CYAN}{Style.BRIGHT}Test Summary")
        print("="*60)
        
        print(f"{Fore.YELLOW}Total IPs Tested: {Fore.WHITE}{stats['total_tested']}")
        print(f"{Fore.GREEN}Successful: {Fore.WHITE}{stats['successful']}")
        print(f"{Fore.RED}Failed: {Fore.WHITE}{stats['failed']}")
        print(f"{Fore.CYAN}Success Rate: {Fore.WHITE}{stats['success_rate']:.1f}%")
        
        if stats['avg_latency_ms']:
            print(f"\n{Fore.YELLOW}Latency Statistics:")
            print(f"  Average: {Fore.WHITE}{stats['avg_latency_ms']:.2f}ms")
            print(f"  Fastest: {Fore.WHITE}{stats['min_latency_ms']:.2f}ms")
            print(f"  Slowest: {Fore.WHITE}{stats['max_latency_ms']:.2f}ms")
        
        print("="*60 + "\n")
    
    def print_top_ips(self, results: List[Dict], top_n: int = 10):
        """Print top N fastest IPs"""
        successful = [r for r in results if r['status'] == 'success']
        
        if not successful:
            print(f"{Fore.RED}No successful connections found!")
            return
        
        sorted_results = sorted(successful, key=lambda x: x['latency_ms'])
        top_results = sorted_results[:top_n]
        
        print(f"{Fore.CYAN}{Style.BRIGHT}Top {len(top_results)} Fastest IPs:")
        print("-" * 40)
        
        for i, result in enumerate(top_results, 1):
            ip = result['ip']
            latency = result['latency_ms']
            print(f"{Fore.GREEN}{i:2d}. {ip:15s} - {latency:6.2f}ms")
        
        print()
    
    def save_json(self, results: List[Dict], filename: str = None) -> str:
        """Save results to JSON file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"results_{timestamp}.json"
            
            output_path = self.output_dir / filename
            
            with open(output_path, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "results": results
                }, f, indent=2)
            
            print(f"{Fore.CYAN}Results saved to: {Fore.WHITE}{output_path}")
            return str(output_path)
        except Exception as e:
            print(f"{Fore.RED}Error saving JSON: {e}")
            return None
    
    def save_csv(self, results: List[Dict], filename: str = None) -> str:
        """Save results to CSV file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"results_{timestamp}.csv"
            
            output_path = self.output_dir / filename
            
            if not results:
                return None
                
            # Get all possible keys from all results to ensure we have all columns
            keys = set()
            for r in results:
                keys.update(r.keys())
            
            fieldnames = list(keys)
            # Ensure specific order if possible, remove duplicates
            preferred_order = ['ip', 'status', 'latency_ms', 'error', 'timestamp']
            ordered_fieldnames = []
            
            # Add preferred keys first if they exist
            for k in preferred_order:
                if k in fieldnames:
                    ordered_fieldnames.append(k)
            
            # Add remaining keys
            for k in fieldnames:
                if k not in ordered_fieldnames:
                    ordered_fieldnames.append(k)
            
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=ordered_fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            print(f"{Fore.CYAN}CSV saved to: {Fore.WHITE}{output_path}")
            return str(output_path)
        except Exception as e:
            print(f"{Fore.RED}Error saving CSV: {e}")
            return None
    
    def save_working_ips(self, results: List[Dict], filename: str = None) -> str:
        """Save only working IPs to text file (one IP per line)"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"working_ips_{timestamp}.txt"
            
            output_path = self.output_dir / filename
            
            successful = [r for r in results if r['status'] == 'success']
            sorted_results = sorted(successful, key=lambda x: x['latency_ms'])
            
            with open(output_path, 'w') as f:
                for result in sorted_results:
                    ip = result['ip']
                    latency = result['latency_ms']
                    f.write(f"{ip} # {latency:.2f}ms\n")
            
            print(f"{Fore.GREEN}Working IPs saved to: {Fore.WHITE}{output_path}")
            print(f"{Fore.GREEN}Total working IPs: {Fore.WHITE}{len(sorted_results)}")
            return str(output_path)
        except Exception as e:
            print(f"{Fore.RED}Error saving working IPs: {e}")
            return None
    
    def generate_full_report(self, results: List[Dict], stats: Dict, 
                           config: Dict) -> str:
        """Generate a comprehensive text report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.txt"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("Cloudflare IP Tester - Detailed Report\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Configuration:\n")
            f.write(f"  Protocol: {config.get('protocol', 'vmess')}\n")
            f.write(f"  SNI: {config.get('sni', 'cloudflare.com')}\n")
            f.write(f"  Port: {config.get('port', 443)}\n")
            f.write(f"  Timeout: {config.get('timeout', 5)}s\n")
            f.write(f"  Concurrent: {config.get('concurrent', 10)}\n\n")
            
            f.write("-"*70 + "\n")
            f.write("Statistics:\n")
            f.write("-"*70 + "\n")
            f.write(f"Total IPs Tested: {stats['total_tested']}\n")
            f.write(f"Successful: {stats['successful']}\n")
            f.write(f"Failed: {stats['failed']}\n")
            f.write(f"Success Rate: {stats['success_rate']:.1f}%\n")
            
            if stats['avg_latency_ms']:
                f.write(f"\nLatency Statistics:\n")
                f.write(f"  Average: {stats['avg_latency_ms']:.2f}ms\n")
                f.write(f"  Fastest: {stats['min_latency_ms']:.2f}ms\n")
                f.write(f"  Slowest: {stats['max_latency_ms']:.2f}ms\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("Successful IPs (sorted by latency):\n")
            f.write("="*70 + "\n\n")
            
            successful = [r for r in results if r['status'] == 'success']
            sorted_results = sorted(successful, key=lambda x: x['latency_ms'])
            
            for i, result in enumerate(sorted_results, 1):
                f.write(f"{i:3d}. {result['ip']:15s} - {result['latency_ms']:7.2f}ms\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("Failed IPs:\n")
            f.write("="*70 + "\n\n")
            
            failed = [r for r in results if r['status'] == 'failed']
            for result in failed:
                error = result.get('error', 'Unknown')
                f.write(f"{result['ip']:15s} - {error}\n")
        
        print(f"{Fore.CYAN}Full report saved to: {Fore.WHITE}{output_path}")
        return str(output_path)


if __name__ == "__main__":
    # Test the reporter
    print("Reporter module loaded successfully")
