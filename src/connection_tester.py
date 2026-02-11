#!/usr/bin/env python3
"""
Connection Tester - Test connections through Xray proxy
"""
import subprocess
import time
import json
import requests
import tempfile
from pathlib import Path
from typing import Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style


class ConnectionTester:
    def __init__(self, xray_path: str, timeout: int = 5):
        self.xray_path = xray_path
        self.timeout = timeout
        self.test_url = "http://www.gstatic.com/generate_204"  # Google's connectivity check
        
    def test_single_ip(self, ip: str, config: dict, verbose: bool = False) -> Dict:
        """
        Test connection to a single IP using Xray
        Returns dict with status, latency, and error info
        """
        result = {
            "ip": ip,
            "status": "failed",
            "latency_ms": None,
            "error": None,
            "timestamp": time.time()
        }
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_file = f.name
        
        xray_process = None
        
        try:
            # Start Xray process
            if verbose:
                print(f"{Fore.CYAN}Testing {ip}...", end=' ')
            
            xray_process = subprocess.Popen(
                [self.xray_path, "run", "-c", config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # Wait a bit for Xray to start
            time.sleep(1)
            
            # Get SOCKS port from config
            socks_port = config['inbounds'][0]['port']
            
            # Test connection through proxy
            start_time = time.time()
            
            proxies = {
                'http': f'socks5h://127.0.0.1:{socks_port}',
                'https': f'socks5h://127.0.0.1:{socks_port}'
            }
            
            response = requests.get(
                self.test_url,
                proxies=proxies,
                timeout=self.timeout,
                allow_redirects=False
            )
            
            latency = (time.time() - start_time) * 1000  # Convert to ms
            
            # Check if response is valid
            if response.status_code in [200, 204]:
                result["status"] = "success"
                result["latency_ms"] = round(latency, 2)
                if verbose:
                    print(f"{Fore.GREEN}✓ {latency:.0f}ms")
            else:
                result["error"] = f"HTTP {response.status_code}"
                if verbose:
                    print(f"{Fore.RED}✗ HTTP {response.status_code}")
                    
        except requests.exceptions.Timeout:
            result["error"] = "Timeout"
            if verbose:
                print(f"{Fore.RED}✗ Timeout")
                
        except requests.exceptions.ProxyError as e:
            result["error"] = "Proxy error"
            if verbose:
                print(f"{Fore.RED}✗ Proxy error")
                
        except requests.exceptions.ConnectionError as e:
            result["error"] = "Connection failed"
            if verbose:
                print(f"{Fore.RED}✗ Connection failed")
                
        except Exception as e:
            result["error"] = str(e)
            if verbose:
                print(f"{Fore.RED}✗ {str(e)}")
                
        finally:
            # Clean up
            if xray_process:
                try:
                    xray_process.terminate()
                    xray_process.wait(timeout=2)
                except:
                    try:
                        xray_process.kill()
                    except:
                        pass
            
            # Remove temp config file
            try:
                Path(config_file).unlink()
            except:
                pass
        
        return result
    
    def test_multiple_ips(self, ip_configs: list, max_workers: int = 10, 
                         progress_callback=None) -> list:
        """
        Test multiple IPs concurrently
        ip_configs: list of tuples (ip, config)
        Returns list of results
        """
        results = []
        total = len(ip_configs)
        completed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_ip = {
                executor.submit(self.test_single_ip, ip, config, verbose=False): ip 
                for ip, config in ip_configs
            }
            
            # Process completed tasks
            for future in as_completed(future_to_ip):
                result = future.result()
                results.append(result)
                completed += 1
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(completed, total, result)
        
        return results
    
    @staticmethod
    def filter_successful(results: list) -> list:
        """Filter only successful results"""
        return [r for r in results if r['status'] == 'success']
    
    @staticmethod
    def sort_by_latency(results: list) -> list:
        """Sort results by latency (fastest first)"""
        successful = ConnectionTester.filter_successful(results)
        return sorted(successful, key=lambda x: x['latency_ms'])
    
    @staticmethod
    def get_statistics(results: list) -> Dict:
        """Get statistics from results"""
        total = len(results)
        successful = ConnectionTester.filter_successful(results)
        success_count = len(successful)
        
        stats = {
            "total_tested": total,
            "successful": success_count,
            "failed": total - success_count,
            "success_rate": (success_count / total * 100) if total > 0 else 0,
            "avg_latency_ms": None,
            "min_latency_ms": None,
            "max_latency_ms": None
        }
        
        if successful:
            latencies = [r['latency_ms'] for r in successful]
            stats["avg_latency_ms"] = round(sum(latencies) / len(latencies), 2)
            stats["min_latency_ms"] = round(min(latencies), 2)
            stats["max_latency_ms"] = round(max(latencies), 2)
        
        return stats


    def test_batch_config(self, config: dict, ip_list: list, base_port: int, progress_callback=None) -> list:
        """
        Test a batch of IPs using a single Xray process
        """
        results = []
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_file = f.name
            
        xray_process = None
        
        try:
            # Start Xray process
            xray_process = subprocess.Popen(
                [self.xray_path, "run", "-c", config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # Wait for Xray to start
            time.sleep(1.5)
            
            # Check if Xray is still running
            if xray_process.poll() is not None:
                # Process died
                stderr = xray_process.stderr.read().decode()
                print(f"{Fore.RED}Xray failed to start: {stderr}")
                return [{"ip": ip, "status": "failed", "error": "Xray failed to start"} for ip in ip_list]
                
            # Define worker function for thread pool
            def check_ip(index, ip):
                port = base_port + index
                result = {
                    "ip": ip,
                    "status": "failed",
                    "latency_ms": None,
                    "error": None,
                    "timestamp": time.time()
                }
                
                start_time = time.time()
                proxies = {
                    'http': f'socks5h://127.0.0.1:{port}',
                    'https': f'socks5h://127.0.0.1:{port}'
                }
                
                try:
                    response = requests.get(
                        self.test_url,
                        proxies=proxies,
                        timeout=self.timeout,
                        allow_redirects=False
                    )
                    
                    latency = (time.time() - start_time) * 1000
                    
                    if response.status_code in [200, 204]:
                        result["status"] = "success"
                        result["latency_ms"] = round(latency, 2)
                    else:
                        result["error"] = f"HTTP {response.status_code}"
                        
                except requests.exceptions.Timeout:
                    result["error"] = "Timeout"
                except Exception as e:
                    result["error"] = str(e)
                    
                return result

            # Run checks concurrently
            with ThreadPoolExecutor(max_workers=min(len(ip_list), 50)) as executor:
                future_to_ip = {
                    executor.submit(check_ip, i, ip): ip 
                    for i, ip in enumerate(ip_list)
                }
                
                for future in as_completed(future_to_ip):
                    result = future.result()
                    results.append(result)
                    
                    if progress_callback:
                        progress_callback(1, len(ip_list), result)
                        
        finally:
            # Cleanup Xray
            if xray_process:
                xray_process.terminate()
                try:
                    xray_process.wait(timeout=2)
                except:
                    xray_process.kill()
                    
            # Remove temp config
            try:
                Path(config_file).unlink()
            except:
                pass
                
        return results

if __name__ == "__main__":
    # This is just a structure test, won't work without actual Xray
    print("Connection Tester module loaded successfully")
    print("This module requires Xray-core to be installed")

