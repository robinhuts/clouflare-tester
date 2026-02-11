#!/usr/bin/env python3
"""
Config Generator - Generate Xray configuration for testing
"""
import json
import uuid
from pathlib import Path


class XrayConfigGenerator:
    def __init__(self, protocol="vmess", port=443, sni="cloudflare.com"):
        self.protocol = protocol.lower()
        self.port = port
        self.sni = sni
        self.local_port = 10808  # Local SOCKS port
        
    def generate_config(self, ip_address: str, output_path: str = None) -> dict:
        """
        Generate Xray configuration for testing a specific IP
        This uses WebSocket + TLS for injection method testing
        """
        
        # Generate UUID for vmess/vless
        user_id = str(uuid.uuid4())
        
        # Base configuration
        config = {
            "log": {
                "loglevel": "warning"
            },
            "inbounds": [
                {
                    "port": self.local_port,
                    "protocol": "socks",
                    "settings": {
                        "auth": "noauth",
                        "udp": False
                    },
                    "tag": "socks-in"
                }
            ],
            "outbounds": [
                {
                    "protocol": self.protocol,
                    "settings": self._get_protocol_settings(user_id),
                    "streamSettings": self._get_stream_settings(ip_address),
                    "tag": "proxy"
                },
                {
                    "protocol": "freedom",
                    "tag": "direct"
                }
            ]
        }
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
        
        return config
    
    def _get_protocol_settings(self, user_id: str) -> dict:
        """Get protocol-specific settings"""
        if self.protocol == "vmess":
            return {
                "vnext": [
                    {
                        "address": "127.0.0.1",  # Will be overridden by streamSettings
                        "port": self.port,
                        "users": [
                            {
                                "id": user_id,
                                "alterId": 0,
                                "security": "auto"
                            }
                        ]
                    }
                ]
            }
        elif self.protocol == "vless":
            return {
                "vnext": [
                    {
                        "address": "127.0.0.1",
                        "port": self.port,
                        "users": [
                            {
                                "id": user_id,
                                "encryption": "none",
                                "flow": ""
                            }
                        ]
                    }
                ]
            }
        elif self.protocol == "trojan":
            return {
                "servers": [
                    {
                        "address": "127.0.0.1",
                        "port": self.port,
                        "password": user_id
                    }
                ]
            }
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")
    
    def _get_stream_settings(self, ip_address: str) -> dict:
        """
        Get stream settings for WebSocket + TLS
        This is the key for injection method testing
        """
        return {
            "network": "ws",
            "security": "tls",
            "tlsSettings": {
                "serverName": self.sni,  # SNI for injection
                "allowInsecure": True,    # Allow self-signed certs for testing
                "fingerprint": "chrome"
            },
            "wsSettings": {
                "path": "/",
                "headers": {
                    "Host": self.sni
                }
            },
            "sockopt": {
                "dialerProxy": "",
                "tcpFastOpen": False,
                "tcpKeepAliveIdle": 100,
                "mark": 0,
                "interface": "",
                "domainStrategy": "AsIs",
                "tcpCongestion": "",
                "v6only": False,
                "tcpWindowClamp": 0,
                "tcpUserTimeout": 0,
                "tcpMaxSeg": 0,
                "tcpNoDelay": False,
                "customSockopt": [
                    {
                        "level": "socket",
                        "opt": "SO_ORIGINAL_DST",
                        "value": ip_address,  # Use specific IP
                        "type": "string"
                    }
                ]
            }
        }
    
    def generate_direct_config(self, ip_address: str) -> dict:
        """
        Generate a simpler direct connection config for basic testing
        """
        # Update the address in outbound settings
        config = self.generate_config(ip_address)
        
        # Directly set the address
        if self.protocol in ["vmess", "vless"]:
            config["outbounds"][0]["settings"]["vnext"][0]["address"] = ip_address
        elif self.protocol == "trojan":
            config["outbounds"][0]["settings"]["servers"][0]["address"] = ip_address
        
        return config
    
    def generate_config_from_server(self, server_config: dict, cf_ip: str) -> dict:
        """
        Generate Xray config using REAL server credentials but testing with Cloudflare IP
        This is the KEY method for testing zero-quota with actual vless/vmess server
        
        Args:
            server_config: Dict from URL parser (contains real UUID, host, path, etc)
            cf_ip: Cloudflare IP to test
            
        Returns:
            Xray config that connects to real server via Cloudflare IP
        """
        protocol = server_config['protocol']
        
        # Base config
        config = {
            "log": {
                "loglevel": "warning"
            },
            "inbounds": [
                {
                    "port": self.local_port,
                    "protocol": "socks",
                    "settings": {
                        "auth": "noauth",
                        "udp": False
                    },
                    "tag": "socks-in"
                }
            ],
            "outbounds": [
                {
                    "protocol": protocol,
                    "settings": self._get_real_protocol_settings(server_config, cf_ip),
                    "streamSettings": self._get_real_stream_settings(server_config),
                    "tag": "proxy"
                },
                {
                    "protocol": "freedom",
                    "tag": "direct"
                }
            ]
        }
        
        return config
    
    def _get_real_protocol_settings(self, server_config: dict, cf_ip: str) -> dict:
        """Get protocol settings using REAL server credentials"""
        protocol = server_config['protocol']
        
        if protocol == "vless":
            return {
                "vnext": [
                    {
                        "address": cf_ip,  # Use Cloudflare IP instead of original address
                        "port": server_config['port'],
                        "users": [
                            {
                                "id": server_config['uuid'],  # Real UUID from server
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
                        "address": cf_ip,
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
                        "address": cf_ip,
                        "port": server_config['port'],
                        "password": server_config['password']
                    }
                ]
            }
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
    
    def _get_real_stream_settings(self, server_config: dict) -> dict:
        """Get stream settings using REAL server config (host, path, SNI, etc)"""
        settings = {
            "network": server_config.get('type', 'ws'),
            "security": server_config.get('security', 'tls')
        }
        
        # TLS settings
        if settings["security"] == "tls":
            settings["tlsSettings"] = {
                "serverName": server_config['sni'],  # Real SNI
                "allowInsecure": True,  # Use false for real servers
                "fingerprint": server_config.get('fingerprint', 'chrome')
            }
            
            if server_config.get('alpn'):
                settings["tlsSettings"]["alpn"] = server_config['alpn'].split(',')
        
        # WebSocket settings
        if server_config.get('type') == 'ws':
            settings["wsSettings"] = {
                "path": server_config.get('path', '/'),
                "headers": {
                    "Host": server_config.get('host', server_config['address'])
                }
            }
        
        # TCP settings (if needed)
        elif server_config.get('type') == 'tcp':
            settings["tcpSettings"] = {
                "header": {
                    "type": "none"
                }
            }
        
        return settings
    
    def generate_zoom_style_config(self, server_config: dict, cf_ip_or_domain: str, 
                                    dns_domain: str = "api.ovo.id", 
                                    use_domain_in_address: bool = True) -> dict:
        """
        Generate Xray config using ZOOM-STYLE approach with DNS hosts mapping.
        This method is optimal for zero-quota testing with SNI bugs.
        
        Args:
            server_config: Dict from URL parser (contains real UUID, host, path, etc)
            cf_ip_or_domain: Cloudflare IP or domain to test (flexible)
            dns_domain: Domain name to use in DNS hosts mapping (default: api.ovo.id)
            use_domain_in_address: If True, use domain in address field (zoom-style)
                                   If False, use IP directly (direct method)
        
        Returns:
            Xray config with DNS hosts mapping
            
        Example zoom-style config:
        {
            "dns": {
                "hosts": {
                    "api.ovo.id": ["170.114.45.6"]  // Map domain to CF IP
                }
            },
            "outbounds": [{
                "settings": {
                    "vnext": [{
                        "address": "api.ovo.id",  // Use mapped domain
                        "port": 443
                    }]
                },
                "streamSettings": {
                    "sockopt": {
                        "domainStrategy": "UseIP"  // Force use mapped IP
                    },
                    "tlsSettings": {
                        "serverName": "point.natss.store"  // Real SNI
                    }
                }
            }]
        }
        """
        protocol = server_config['protocol']
        
        # Determine if cf_ip_or_domain is an IP or domain
        import ipaddress
        try:
            ipaddress.ip_address(cf_ip_or_domain)
            is_ip = True
        except ValueError:
            is_ip = False
        
        # Base config with DNS section
        config = {
            "dns": {
                "hosts": {},
                "servers": ["1.1.1.1"]
            },
            "log": {
                "loglevel": "warning"
            },
            "inbounds": [
                {
                    "listen": "127.0.0.1",
                    "port": self.local_port,
                    "protocol": "socks",
                    "settings": {
                        "auth": "noauth",
                        "udp": True
                    },
                    "sniffing": {
                        "destOverride": ["http", "tls"],
                        "enabled": True
                    },
                    "tag": "socks"
                },
                {
                    "listen": "127.0.0.1",
                    "port": self.local_port + 1,
                    "protocol": "http",
                    "settings": {},
                    "tag": "http"
                }
            ],
            "outbounds": [
                {
                    "protocol": protocol,
                    "settings": None,  # Will be set below
                    "streamSettings": None,  # Will be set below
                    "tag": "proxy"
                },
                {
                    "protocol": "freedom",
                    "settings": {},
                    "tag": "direct"
                }
            ],
            "routing": {
                "domainStrategy": "AsIs",
                "rules": [
                    {
                        "ip": ["geoip:private"],
                        "outboundTag": "direct",
                        "type": "field"
                    }
                ]
            }
        }
        
        # Decide address to use in outbound
        if use_domain_in_address:
            # Zoom-style: use domain in address, map it to IP in DNS hosts
            address_to_use = dns_domain
            if is_ip:
                # Map domain to this IP
                config["dns"]["hosts"][dns_domain] = [cf_ip_or_domain]
            else:
                # Map domain to domain (Cloudflare will resolve it)
                config["dns"]["hosts"][dns_domain] = [cf_ip_or_domain]
        else:
            # Direct method: use IP/domain directly in address
            address_to_use = cf_ip_or_domain
            # Still add DNS hosts for reference
            if is_ip:
                config["dns"]["hosts"][dns_domain] = [cf_ip_or_domain]
        
        # Set protocol-specific settings
        if protocol == "vless":
            config["outbounds"][0]["settings"] = {
                "vnext": [
                    {
                        "address": address_to_use,
                        "port": server_config['port'],
                        "users": [
                            {
                                "encryption": server_config.get('encryption', 'none'),
                                "flow": "",
                                "id": server_config['uuid']
                            }
                        ]
                    }
                ]
            }
        elif protocol == "vmess":
            config["outbounds"][0]["settings"] = {
                "vnext": [
                    {
                        "address": address_to_use,
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
            config["outbounds"][0]["settings"] = {
                "servers": [
                    {
                        "address": address_to_use,
                        "port": server_config['port'],
                        "password": server_config['password']
                    }
                ]
            }
        
        # Stream settings with zoom-style sockopt
        stream_settings = {
            "network": server_config.get('type', 'ws'),
            "security": server_config.get('security', 'tls'),
            "sockopt": {
                "domainStrategy": "UseIP"  # Key for zoom-style!
            }
        }
        
        # TLS settings
        if stream_settings["security"] == "tls":
            stream_settings["tlsSettings"] = {
                "allowInsecure": server_config.get('allowInsecure', True),
                "serverName": server_config['sni'],
                "show": False
            }
            
            if server_config.get('fingerprint'):
                stream_settings["tlsSettings"]["fingerprint"] = server_config['fingerprint']
            
            if server_config.get('alpn'):
                stream_settings["tlsSettings"]["alpn"] = server_config['alpn'].split(',')
        
        # WebSocket settings
        if server_config.get('type') == 'ws':
            stream_settings["wsSettings"] = {
                "headers": {
                    "Host": server_config.get('host', server_config['sni'])
                },
                "path": server_config.get('path', '/')
            }
        
        config["outbounds"][0]["streamSettings"] = stream_settings
        
        return config


    def generate_batch_config(self, ip_list: list, server_config: dict, 
                             dns_domain: str = "api.ovo.id", 
                             use_domain_in_address: bool = True,
                             base_port: int = 20000) -> dict:
        """
        Generate a SINGLE Xray config for testing multiple IPs simultaneously.
        This creates multiple inbounds and outbounds mapped 1:1.
        """
        
        # Base config
        config = {
            "log": {
                "loglevel": "error"
            },
            "dns": {
                "hosts": {},
                "servers": ["1.1.1.1"]
            },
            "inbounds": [],
            "outbounds": [],
            "routing": {
                "domainStrategy": "AsIs",
                "rules": []
            }
        }
        
        # Add a direct outbound (always needed as fallback/default)
        config["outbounds"].append({
            "protocol": "freedom",
            "tag": "direct",
            "settings": {}
        })
        
        # Determine protocol
        protocol = server_config['protocol']
        
        # Iterate through IPs and create pairs of Inbound -> Outbound
        for i, ip in enumerate(ip_list):
            port = base_port + i
            tag_in = f"socks-{i}"
            tag_out = f"proxy-{i}"
            
            # 1. Create Inbound (SOCKS)
            inbound = {
                "listen": "127.0.0.1",
                "port": port,
                "protocol": "socks",
                "settings": {
                    "auth": "noauth",
                    "udp": True
                },
                "tag": tag_in
            }
            config["inbounds"].append(inbound)
            
            # 2. Create Outbound (Proxy)
            # Use logic similar to generate_zoom_style_config but adapted for loop
            
            # Decide address
            address_to_use = dns_domain if use_domain_in_address else ip
            
            # Map DNS if needed (we map domain to THIS specific IP for THIS outbound??)
            # PROBLEM: DNS hosts is global. We can't map 'api.ovo.id' to 20 different IPs at once globally.
            # SOLVED: Xray 'sockopt' -> 'dialerProxy' or just rely on 'domainStrategy': 'UseIP' 
            # BUT: If we use 'api.ovo.id' as address, Xray resolves it.
            # If we map 'api.ovo.id' to '1.2.3.4' in DNS, it applies to ALL outbounds using that domain.
            
            # SOLUTION for Batch + SNI Bug:
            # We must use the IP directly in the address field for the connectivity, 
            # BUT we need to ensure the SNI/Host header represents the bug domain.
            # generate_zoom_style_config does: address=ip (or mapped domain), sockopt.domainStrategy=UseIP.
            
            # If we pass IP as address:
            # address = "104.16.0.1"
            # sni = "point.natss.store" (Real Server)
            # host = "point.natss.store" (Real Server)
            # This is "Direct" mode.
            
            # If we want "Zoom Style" (SNI Bug):
            # We rely on the fact that we send a request to a Cloudflare IP, 
            # but the TLS SNI is the Real Server SNI? 
            # NO. The "Bug" is that we connect to Cloudflare IP, but valid SNI (for firewall bypass) 
            # is 'api.ovo.id', and INSIDE that TLS tunnel we speak VLESS/VMESS to Real Server.
            
            # Wait, let's look at `generate_zoom_style_config` again.
            # It sets streamSettings.tlsSettings.serverName = server_config['sni'] (Real Server)
            # It sets wsSettings.headers.Host = server_config.get('host') (Real Server)
            # It sets address = dns_domain (Bug Domain) OR ip.
            
            # If we use batching, we cannot use a global DNS map for the Bug Domain if it needs to map to different IPs.
            # So for batching, we MUST use the IP directly in the 'address' field.
            # And we rely on 'api.ovo.id' being irrelevant for the *connection* destination IP, 
            # UNLESS the bug requires the address to match the SNI at some layer?
            
            # Let's assume using IP directly in 'address' is fine, 
            # provided the SNI/Host headers are correct for the VLESS connection.
            
            # However, some "Zero Quota" Tricks need the "Bug" to be the SNI visible to the IDP.
            # If address="104.x.x.x", SNI="real-server.com", that might not pass.
            # We need SNI="api.ovo.id" (Bug) on the outer layer? 
            # No, Xray usually encrypts the VLESS traffic.
            # If we are using WS+TLS, the outer SNI is `tlsSettings.serverName`.
            
            # If `generate_zoom_style_config` sets `serverName` to `server_config['sni']` (Real Server),
            # then the "Bug" is just the IP/Domain resolution? 
            
            # Let's assume we can just use the IP in the address field for batching 
            # and ignore the DNS mapping trick, OR use the `sockopt` `SO_ORIGINAL_DST` trick if supported.
            
            # Safest approach for Batch:
            # Use IP as address.
            # streamSettings same as single-mode.
            # If the user selected "Bug/SNI Mode" where address MUST be the bug domain:
            # Then Batching is hard because DNS is global.
            # UNLESS we use unique fake domains for each IP? 
            # e.g. "ip-1.api.ovo.id", "ip-2.api.ovo.id" and map them in DNS?
            # Yes! That works.
            
            fake_domain = f"ip-{i}-{ip.replace('.', '-')}.{dns_domain}"
            config["dns"]["hosts"][fake_domain] = [ip]
            
            # Now build Outbound
            outbound = {
                "protocol": protocol,
                "settings": {},
                "streamSettings": {},
                "tag": tag_out
            }
            
            # Protocol Settings
            if protocol == "vless":
                outbound["settings"] = {
                    "vnext": [{
                        "address": fake_domain,
                        "port": server_config['port'],
                        "users": [{
                            "encryption": server_config.get('encryption', 'none'),
                            "flow": "",
                            "id": server_config['uuid']
                        }]
                    }]
                }
            elif protocol == "vmess":
                outbound["settings"] = {
                    "vnext": [{
                        "address": fake_domain,
                        "port": server_config['port'],
                        "users": [{
                            "id": server_config['uuid'],
                            "alterId": server_config.get('aid', 0),
                            "security": server_config.get('encryption', 'auto')
                        }]
                    }]
                }
            elif protocol == "trojan":
                outbound["settings"] = {
                    "servers": [{
                        "address": fake_domain,
                        "port": server_config['port'],
                        "password": server_config['password']
                    }]
                }
                
            # Stream Settings (Clone from helper, but we need to inject it here)
            # We can reuse the logic from _get_real_stream_settings but it's internal.
            # Let's copy the essential stream logic here or call internal method if possible.
            # _get_real_stream_settings depends on server_config, which is constant for all IPs.
            stream_settings = self._get_real_stream_settings(server_config)
            
            # Ensure sockopt UseIP
            if "sockopt" not in stream_settings:
                stream_settings["sockopt"] = {}
            stream_settings["sockopt"]["domainStrategy"] = "UseIP"
            
            outbound["streamSettings"] = stream_settings
            
            config["outbounds"].append(outbound)
            
            # 3. Create Routing Rule
            rule = {
                "type": "field",
                "inboundTag": [tag_in],
                "outboundTag": tag_out
            }
            config["routing"]["rules"].append(rule)
            
        return config

if __name__ == "__main__":
    # Test the config generator
    print("Testing Xray Config Generator:")
    
    generator = XrayConfigGenerator(protocol="vmess", port=443, sni="cloudflare.com")
    
    test_ip = "104.16.0.1"
    config = generator.generate_direct_config(test_ip)
    
    # Save test config
    output_file = "test_config.json"
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nGenerated config for IP: {test_ip}")
    print(f"Protocol: vmess")
    print(f"SNI: cloudflare.com")
    print(f"Config saved to: {output_file}")
    print(f"\nLocal SOCKS port: {generator.local_port}")

