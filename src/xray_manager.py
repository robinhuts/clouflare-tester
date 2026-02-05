#!/usr/bin/env python3
"""
Xray Manager - Handles Xray-core download, installation, and execution
"""
import os
import sys
import platform
import zipfile
import requests
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

class XrayManager:
    def __init__(self, xray_dir="xray"):
        self.xray_dir = Path(xray_dir)
        self.xray_dir.mkdir(exist_ok=True)
        
        # Determine OS and architecture
        self.os_name = platform.system().lower()
        self.arch = platform.machine().lower()
        
        # Set executable name based on OS
        self.xray_binary = "xray.exe" if self.os_name == "windows" else "xray"
        self.xray_path = self.xray_dir / self.xray_binary
        
    def is_installed(self):
        """Check if Xray is already installed"""
        return self.xray_path.exists()
    
    def get_download_url(self):
        """Get the appropriate download URL for current OS and architecture"""
        # Xray releases URL
        base_url = "https://github.com/XTLS/Xray-core/releases/latest/download/"
        
        # Map platform to download file
        if self.os_name == "windows":
            if "64" in self.arch or "amd64" in self.arch:
                filename = "Xray-windows-64.zip"
            else:
                filename = "Xray-windows-32.zip"
        elif self.os_name == "linux":
            # Better ARM detection for Android/Termux
            if "aarch64" in self.arch or "armv8" in self.arch or "arm64" in self.arch:
                # ARM64 - common in modern Android devices (Termux)
                filename = "Xray-linux-arm64-v8a.zip"
            elif "armv7" in self.arch or "armv7l" in self.arch:
                # ARM32 v7 - older Android devices
                filename = "Xray-linux-arm32-v7a.zip"
            elif "64" in self.arch or "amd64" in self.arch or "x86_64" in self.arch:
                # x86_64 - standard Linux/desktop
                filename = "Xray-linux-64.zip"
            elif "arm" in self.arch:
                # Generic ARM fallback - assume ARM64
                filename = "Xray-linux-arm64-v8a.zip"
            else:
                # 32-bit x86 fallback
                filename = "Xray-linux-32.zip"
        elif self.os_name == "darwin":  # macOS
            if "arm" in self.arch:
                filename = "Xray-macos-arm64-v8a.zip"
            else:
                filename = "Xray-macos-64.zip"
        else:
            raise Exception(f"Unsupported OS: {self.os_name}")
        
        return base_url + filename
    
    def download_and_install(self):
        """Download and install Xray-core"""
        try:
            print(f"{Fore.YELLOW}Downloading Xray-core...")
            download_url = self.get_download_url()
            
            # Download file
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            zip_path = self.xray_dir / "xray.zip"
            
            # Save with progress
            total_size = int(response.headers.get('content-length', 0))
            with open(zip_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = (downloaded / total_size) * 100 if total_size > 0 else 0
                        print(f"\r{Fore.CYAN}Progress: {percent:.1f}%", end='')
            
            print(f"\n{Fore.GREEN}Download complete!")
            
            # Extract ZIP
            print(f"{Fore.YELLOW}Extracting Xray-core...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.xray_dir)
            
            # Remove ZIP file
            zip_path.unlink()
            
            # Make executable on Unix-like systems
            if self.os_name != "windows":
                os.chmod(self.xray_path, 0o755)
            
            print(f"{Fore.GREEN}Xray-core installed successfully!")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Error downloading/installing Xray: {e}")
            return False
    
    def ensure_installed(self):
        """Ensure Xray is installed, download if not"""
        if self.is_installed():
            print(f"{Fore.GREEN}✓ Xray-core already installed")
            return True
        else:
            print(f"{Fore.YELLOW}Xray-core not found, downloading...")
            return self.download_and_install()
    
    def get_xray_path(self):
        """Get the path to Xray executable"""
        return str(self.xray_path.absolute())
    
    def get_version(self):
        """Get Xray version"""
        try:
            import subprocess
            result = subprocess.run([self.get_xray_path(), "version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Extract version from first line
                first_line = result.stdout.split('\n')[0]
                return first_line
            return "Unknown"
        except Exception as e:
            return f"Error: {e}"


if __name__ == "__main__":
    # Test the manager
    manager = XrayManager()
    print(f"OS: {manager.os_name}")
    print(f"Architecture: {manager.arch}")
    print(f"Xray path: {manager.xray_path}")
    print(f"Download URL: {manager.get_download_url()}")
    
    if manager.ensure_installed():
        print(f"Version: {manager.get_version()}")
