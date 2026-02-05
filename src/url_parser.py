#!/usr/bin/env python3
"""
URL Parser - Parse vmess/vless/trojan URLs
"""
import base64
import json
import urllib.parse
from typing import Dict, Optional


class URLParser:
    @staticmethod
    def parse_vless_url(url: str) -> Dict:
        """
        Parse vless URL format:
        vless://UUID@ADDRESS:PORT?param1=value1&param2=value2#NAME
        
        Example:
        vless://4b70b98a-1b39-4d76-880a-243ba5c5e03b@point.natss.store:443?path=/vless&security=tls&encryption=none&host=point.natss.store&type=ws&sni=point.natss.store#yamete09
        """
        if not url.startswith('vless://'):
            raise ValueError("URL must start with vless://")
        
        # Remove protocol
        url = url[8:]
        
        # Split by #(name/remark)
        if '#' in url:
            url, name = url.split('#', 1)
            name = urllib.parse.unquote(name)
        else:
            name = "vless"
        
        # Split by @ (uuid@address)
        uuid, rest = url.split('@', 1)
        
        # Split by ? (address:port?params)
        if '?' in rest:
            address_port, params_str = rest.split('?', 1)
            params = urllib.parse.parse_qs(params_str)
            # Convert lists to single values
            params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
        else:
            address_port = rest
            params = {}
        
        # Split address and port
        if ':' in address_port:
            address, port = address_port.rsplit(':', 1)
            port = int(port)
        else:
            address = address_port
            port = 443
        
        return {
            'protocol': 'vless',
            'uuid': uuid,
            'address': address,
            'port': port,
            'name': name,
            'security': params.get('security', 'tls'),
            'encryption': params.get('encryption', 'none'),
            'type': params.get('type', 'tcp'),
            'host': params.get('host', address),
            'path': params.get('path', '/'),
            'sni': params.get('sni', address),
            'alpn': params.get('alpn', ''),
            'fingerprint': params.get('fp', 'chrome')
        }
    
    @staticmethod
    def parse_vmess_url(url: str) -> Dict:
        """
        Parse vmess URL format:
        vmess://BASE64_ENCODED_JSON
        """
        if not url.startswith('vmess://'):
            raise ValueError("URL must start with vmess://")
        
        # Decode base64
        encoded = url[8:]
        
        # Add padding if needed
        padding = 4 - len(encoded) % 4
        if padding != 4:
            encoded += '=' * padding
        
        try:
            decoded = base64.b64decode(encoded).decode('utf-8')
            config = json.loads(decoded)
        except Exception as e:
            raise ValueError(f"Invalid vmess URL: {e}")
        
        return {
            'protocol': 'vmess',
            'uuid': config.get('id', ''),
            'address': config.get('add', ''),
            'port': int(config.get('port', 443)),
            'name': config.get('ps', 'vmess'),
            'security': config.get('tls', 'tls'),
            'encryption': config.get('scy', 'auto'),
            'type': config.get('net', 'tcp'),
            'host': config.get('host', config.get('add', '')),
            'path': config.get('path', '/'),
            'sni': config.get('sni', config.get('add', '')),
            'alpn': config.get('alpn', ''),
            'fingerprint': config.get('fp', 'chrome'),
            'aid': config.get('aid', 0)
        }
    
    @staticmethod
    def parse_trojan_url(url: str) -> Dict:
        """
        Parse trojan URL format:
        trojan://PASSWORD@ADDRESS:PORT?params#NAME
        """
        if not url.startswith('trojan://'):
            raise ValueError("URL must start with trojan://")
        
        # Remove protocol
        url = url[9:]
        
        # Split by # (name)
        if '#' in url:
            url, name = url.split('#', 1)
            name = urllib.parse.unquote(name)
        else:
            name = "trojan"
        
        # Split by @ (password@address)
        password, rest = url.split('@', 1)
        password = urllib.parse.unquote(password)
        
        # Split by ? (address:port?params)
        if '?' in rest:
            address_port, params_str = rest.split('?', 1)
            params = urllib.parse.parse_qs(params_str)
            params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
        else:
            address_port = rest
            params = {}
        
        # Split address and port
        if ':' in address_port:
            address, port = address_port.rsplit(':', 1)
            port = int(port)
        else:
            address = address_port
            port = 443
        
        return {
            'protocol': 'trojan',
            'password': password,
            'address': address,
            'port': port,
            'name': name,
            'security': params.get('security', 'tls'),
            'type': params.get('type', 'tcp'),
            'host': params.get('host', address),
            'path': params.get('path', '/'),
            'sni': params.get('sni', address),
            'alpn': params.get('alpn', ''),
            'fingerprint': params.get('fp', 'chrome')
        }
    
    @staticmethod
    def parse_url(url: str) -> Dict:
        """Auto-detect and parse any supported URL"""
        if url.startswith('vless://'):
            return URLParser.parse_vless_url(url)
        elif url.startswith('vmess://'):
            return URLParser.parse_vmess_url(url)
        elif url.startswith('trojan://'):
            return URLParser.parse_trojan_url(url)
        else:
            raise ValueError("Unsupported protocol. Use vless://, vmess://, or trojan://")


if __name__ == "__main__":
    # Test with the user's vless URL
    test_url = "vless://4b70b98a-1b39-4d76-880a-243ba5c5e03b@point.natss.store:443?path=/vless&security=tls&encryption=none&host=point.natss.store&type=ws&sni=point.natss.store#yamete09"
    
    print("Testing vless URL parser:")
    print(f"URL: {test_url}\n")
    
    config = URLParser.parse_vless_url(test_url)
    
    print("Parsed config:")
    for key, value in config.items():
        print(f"  {key}: {value}")
