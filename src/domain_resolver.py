#!/usr/bin/env python3
"""
Domain Resolver - Resolve domain to Cloudflare IPs
"""
import socket
import dns.resolver


def resolve_domain(domain):
    """
    Resolve domain to IP addresses
    Returns list of IPs
    """
    ips = []
    
    try:
        # Try DNS resolver first
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        
        # Get A records
        answers = resolver.resolve(domain, 'A')
        for rdata in answers:
            ips.append(str(rdata))
            
    except Exception:
        # Fallback to socket
        try:
            result = socket.getaddrinfo(domain, None)
            for item in result:
                ip = item[4][0]
                if ip not in ips and ':' not in ip:  # IPv4 only
                    ips.append(ip)
        except Exception:
            pass
    
    return ips


def is_cloudflare_ip(ip):
    """
    Check if IP belongs to Cloudflare using common ranges
    """
    cloudflare_prefixes = [
        '173.245.', '103.21.', '103.22.', '103.31.',
        '141.101.', '108.162.', '190.93.', '188.114.',
        '197.234.', '198.41.', '162.158.', '104.16.',
        '104.17.', '104.18.', '104.19.', '104.20.',
        '104.21.', '104.22.', '104.23.', '104.24.',
        '104.25.', '104.26.', '104.27.', '104.28.',
        '104.29.', '104.30.', '104.31.', '172.64.',
        '172.65.', '172.66.', '172.67.', '131.0.72.', '170.114'
    ]
    
    for prefix in cloudflare_prefixes:
        if ip.startswith(prefix):
            return True
    return False


def resolve_domain_to_cloudflare_ips(domain):
    """
    Resolve domain and filter only Cloudflare IPs
    Returns tuple: (all_ips, cloudflare_ips)
    """
    all_ips = resolve_domain(domain)
    cloudflare_ips = [ip for ip in all_ips if is_cloudflare_ip(ip)]
    
    return all_ips, cloudflare_ips


if __name__ == "__main__":
    # Test
    domain = sys.argv[1] if len(sys.argv) > 1 else "api.ovo.id"
    all_ips, cf_ips = resolve_domain_to_cloudflare_ips(domain)
    
    print(f"Domain: {domain}")
    print(f"All IPs: {all_ips}")
    print(f"Cloudflare IPs: {cf_ips}")
