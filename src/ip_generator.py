#!/usr/bin/env python3
"""
IP Generator - Generate IP addresses from various input formats
"""
import ipaddress
import re
from typing import List, Iterator
from pathlib import Path


class IPGenerator:
    @staticmethod
    def parse_range(ip_range: str) -> List[str]:
        """
        Parse IP range and return list of IPs
        Supports multiple formats:
        - CIDR: 104.16.0.0/24
        - Range: 104.16.0.0-104.16.0.255
        - Single IP: 104.16.0.1
        - File: @ips.txt (read from file)
        """
        ips = []
        
        # Check if it's a file reference
        if ip_range.startswith('@'):
            file_path = Path(ip_range[1:])
            if file_path.exists():
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            ips.extend(IPGenerator.parse_range(line))
                return ips
            else:
                raise ValueError(f"File not found: {file_path}")
        
        # CIDR notation
        if '/' in ip_range:
            try:
                network = ipaddress.ip_network(ip_range, strict=False)
                return [str(ip) for ip in network.hosts()]
            except Exception as e:
                raise ValueError(f"Invalid CIDR notation: {ip_range} - {e}")
        
        # Range notation (104.16.0.0-104.16.0.255)
        elif '-' in ip_range:
            try:
                start_ip, end_ip = ip_range.split('-')
                start_ip = start_ip.strip()
                end_ip = end_ip.strip()
                
                # If end_ip is just a number, it's last octet
                if '.' not in end_ip:
                    # Get first 3 octets from start_ip
                    base = '.'.join(start_ip.split('.')[:-1])
                    end_ip = f"{base}.{end_ip}"
                
                start = ipaddress.IPv4Address(start_ip)
                end = ipaddress.IPv4Address(end_ip)
                
                if start > end:
                    raise ValueError("Start IP must be less than or equal to end IP")
                
                # Generate IPs in range
                current = int(start)
                end_int = int(end)
                
                while current <= end_int:
                    ips.append(str(ipaddress.IPv4Address(current)))
                    current += 1
                
                return ips
                
            except Exception as e:
                raise ValueError(f"Invalid IP range: {ip_range} - {e}")
        
        # Single IP or comma-separated IPs
        else:
            # Check for comma-separated IPs
            if ',' in ip_range:
                result_ips = []
                for ip in ip_range.split(','):
                    ip = ip.strip()
                    if ip:
                        try:
                            ipaddress.IPv4Address(ip)
                            result_ips.append(ip)
                        except Exception as e:
                            raise ValueError(f"Invalid IP in list: {ip} - {e}")
                return result_ips
            
            # Single IP
            try:
                ipaddress.IPv4Address(ip_range)
                return [ip_range]
            except Exception as e:
                raise ValueError(f"Invalid IP address: {ip_range} - {e}")

    
    @staticmethod
    def validate_ip(ip: str) -> bool:
        """Validate if string is a valid IPv4 address"""
        try:
            ipaddress.IPv4Address(ip)
            return True
        except:
            return False
    
    @staticmethod
    def count_ips(ip_range: str) -> int:
        """Count how many IPs will be generated from a range"""
        try:
            return len(IPGenerator.parse_range(ip_range))
        except:
            return 0
    
    @staticmethod
    def get_cloudflare_ranges() -> List[str]:
        """
        Get common Cloudflare IP ranges
        Source: https://www.cloudflare.com/ips/
        """
        return [
            "173.245.48.0/20",
            "103.21.244.0/22",
            "103.22.200.0/22",
            "103.31.4.0/22",
            "141.101.64.0/18",
            "108.162.192.0/18",
            "190.93.240.0/20",
            "188.114.96.0/20",
            "197.234.240.0/22",
            "198.41.128.0/17",
            "162.158.0.0/15",
            "104.16.0.0/13",
            "104.24.0.0/14",
            "172.64.0.0/13",
            "131.0.72.0/22"
        ]


if __name__ == "__main__":
    # Test the generator
    print("Testing IP Generator:")
    
    # Test CIDR
    print("\n1. CIDR notation (104.16.0.0/30):")
    ips = IPGenerator.parse_range("104.16.0.0/30")
    print(f"   Generated {len(ips)} IPs: {ips}")
    
    # Test range
    print("\n2. Range notation (104.16.0.1-104.16.0.5):")
    ips = IPGenerator.parse_range("104.16.0.1-104.16.0.5")
    print(f"   Generated {len(ips)} IPs: {ips}")
    
    # Test short range
    print("\n3. Short range (104.16.0.1-5):")
    ips = IPGenerator.parse_range("104.16.0.1-5")
    print(f"   Generated {len(ips)} IPs: {ips}")
    
    # Test single IP
    print("\n4. Single IP (104.16.0.1):")
    ips = IPGenerator.parse_range("104.16.0.1")
    print(f"   Generated {len(ips)} IPs: {ips}")
    
    # Test Cloudflare ranges
    print("\n5. Cloudflare IP ranges:")
    ranges = IPGenerator.get_cloudflare_ranges()
    for r in ranges[:3]:
        count = IPGenerator.count_ips(r)
        print(f"   {r}: {count:,} IPs")
