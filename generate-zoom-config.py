#!/usr/bin/env python3
"""
Generate Xray Config with Zoom Subdomain SNI Trick
This uses: support.zoom.us.point.natss.store as SNI/Host
Address: point.natss.store (server domain, NOT Cloudflare IP)
"""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from url_parser import URLParser
from colorama import Fore, Style, init

init(autoreset=True)


def generate_zoom_subdomain_config(server_url, output_file="xray-zoom-config.json"):
    """
    Generate Xray config with Zoom subdomain SNI trick
    
    Server URL: vless://...@point.natss.store:443?...
    
    Generated config will use:
    - address: point.natss.store (original server)
    - SNI: support.zoom.us.point.natss.store (Zoom subdomain trick)
    - Host: support.zoom.us.point.natss.store (Zoom subdomain trick)
    """
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Zoom Subdomain SNI Config Generator")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    # Parse server URL
    print(f"{Fore.YELLOW}Parsing server URL...")
    try:
        server_config = URLParser.parse_url(server_url)
        print(f"{Fore.GREEN}✓ Server parsed successfully")
        print(f"  Original server: {server_config['address']}")
        print(f"  Original SNI: {server_config['sni']}")
        print(f"  Original Host: {server_config['host']}\n")
    except Exception as e:
        print(f"{Fore.RED}Error parsing URL: {e}")
        return False
    
    # Create Zoom subdomain SNI
    original_domain = server_config['address']
    zoom_sni = f"support.zoom.us.{original_domain}"
    
    print(f"{Fore.YELLOW}Applying Zoom Subdomain SNI Trick:")
    print(f"{Fore.GREEN}  Address: {Fore.WHITE}{original_domain} {Fore.CYAN}(unchanged)")
    print(f"{Fore.GREEN}  SNI: {Fore.WHITE}{zoom_sni} {Fore.YELLOW}(modified!)")
    print(f"{Fore.GREEN}  Host: {Fore.WHITE}{zoom_sni} {Fore.YELLOW}(modified!)\n")
    
    # Generate config
    config = {
        "log": {
            "loglevel": "warning"
        },
        "inbounds": [
            {
                "port": 10808,
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": False
                },
                "tag": "socks-in"
            },
            {
                "port": 10809,
                "protocol": "http",
                "settings": {},
                "tag": "http-in"
            }
        ],
        "outbounds": [
            {
                "protocol": server_config['protocol'],
                "settings": _get_protocol_settings(server_config),
                "streamSettings": _get_stream_settings(server_config, zoom_sni),
                "tag": "proxy"
            },
            {
                "protocol": "freedom",
                "tag": "direct"
            }
        ]
    }
    
    # Save config
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"{Fore.GREEN}✓ Config saved to: {Fore.WHITE}{output_file}\n")
    
    # Print usage instructions
    print(f"{Fore.CYAN}{Style.BRIGHT}How to Use:")
    print(f"{Fore.YELLOW}1. Run Xray:")
    print(f"   {Fore.WHITE}xray.exe run -c {output_file}")
    print(f"{Fore.YELLOW}2. Configure your browser/app:")
    print(f"   {Fore.WHITE}SOCKS5: 127.0.0.1:10808")
    print(f"   {Fore.WHITE}HTTP: 127.0.0.1:10809")
    print(f"{Fore.YELLOW}3. Test connection with zero-quota SIM card\n")
    
    print(f"{Fore.CYAN}How it works:")
    print(f"  ISP sees SNI: {Fore.GREEN}support.zoom.us{Fore.WHITE}.point.natss.store")
    print(f"  ISP thinks: {Fore.GREEN}\"User accessing Zoom (zero-rated)\"")
    print(f"  ISP allows: {Fore.GREEN}Traffic passes without quota deduction!")
    print(f"  Reality: {Fore.CYAN}Connects to {original_domain} server\n")
    
    return True


def _get_protocol_settings(server_config):
    """Get protocol-specific settings"""
    protocol = server_config['protocol']
    
    if protocol == "vless":
        return {
            "vnext": [
                {
                    "address": server_config['address'],  # Use original server domain
                    "port": server_config['port'],
                    "users": [
                        {
                            "id": server_config['uuid'],
                            "encryption": server_config.get('encryption', 'none'),
                            "flow": ""
                        }
                    ]
                }
            ]
        }
    elif protocol == "vmess":
        return {
            "vnext": [
                {
                    "address": server_config['address'],
                    "port": server_config['port'],
                    "users": [
                        {
                            "id": server_config['uuid'],
                            "alterId": server_config.get('aid', 0),
                            "security": server_config.get('encryption', 'auto')
                        }
                    ]
                }
            ]
        }
    elif protocol == "trojan":
        return {
            "servers": [
                {
                    "address": server_config['address'],
                    "port": server_config['port'],
                    "password": server_config['password']
                }
            ]
        }


def _get_stream_settings(server_config, zoom_sni):
    """Get stream settings with Zoom subdomain SNI"""
    settings = {
        "network": server_config.get('type', 'ws'),
        "security": server_config.get('security', 'tls')
    }
    
    # TLS settings with Zoom subdomain SNI
    if settings["security"] == "tls":
        settings["tlsSettings"] = {
            "serverName": zoom_sni,  # ← Zoom subdomain SNI!
            "allowInsecure": False,
            "fingerprint": server_config.get('fingerprint', 'chrome')
        }
        
        if server_config.get('alpn'):
            settings["tlsSettings"]["alpn"] = server_config['alpn'].split(',')
    
    # WebSocket settings with Zoom subdomain Host
    if server_config.get('type') == 'ws':
        settings["wsSettings"] = {
            "path": server_config.get('path', '/'),
            "headers": {
                "Host": zoom_sni  # ← Zoom subdomain Host!
            }
        }
    
    return settings


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate Xray config with Zoom subdomain SNI trick',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python generate-zoom-config.py \\
    --server-url "vless://4b70b98a-1b39-4d76-880a-243ba5c5e03b@point.natss.store:443?path=/vless&security=tls&encryption=none&host=point.natss.store&type=ws&sni=point.natss.store#yamete09" \\
    --output my-zoom-config.json
        """
    )
    
    parser.add_argument('--server-url', type=str, required=True,
                       help='vless://... or vmess://... or trojan://... URL')
    parser.add_argument('--output', type=str, default='xray-zoom-config.json',
                       help='Output config file (default: xray-zoom-config.json)')
    
    args = parser.parse_args()
    
    success = generate_zoom_subdomain_config(args.server_url, args.output)
    sys.exit(0 if success else 1)
