"""
Tailscale Installation and Configuration
Workaround for systemd-less container environments
"""
import logging
import os
import subprocess
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TailscaleManager:
    """
    Tailscale Manager with systemd workarounds
    
    Handles Tailscale installation and configuration in container
    environments where systemd is not available
    """
    
    @staticmethod
    def check_systemd_available() -> bool:
        """Check if systemd is available"""
        try:
            result = subprocess.run(
                ["systemctl", "--version"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    async def install_tailscale_userspace() -> Dict[str, Any]:
        """
        Install Tailscale in userspace mode (no systemd required)
        
        This is the workaround for containers without systemd
        """
        try:
            # Check if already installed
            result = subprocess.run(
                ["which", "tailscale"],
                capture_output=True
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Tailscale already installed",
                    "path": result.stdout.decode().strip()
                }
            
            # Download and install Tailscale
            logger.info("Installing Tailscale in userspace mode...")
            
            commands = [
                # Download tailscale
                "curl -fsSL https://tailscale.com/install.sh | sh",
                
                # Note: In userspace mode, we don't need systemd
                # Tailscale can run directly
            ]
            
            for cmd in commands:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Installation failed: {result.stderr.decode()}"
                    }
            
            return {
                "success": True,
                "message": "Tailscale installed successfully",
                "mode": "userspace",
                "note": "Running without systemd"
            }
        except Exception as e:
            logger.error(f"Tailscale installation failed: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def start_tailscale_userspace(auth_key: str = None) -> Dict[str, Any]:
        """
        Start Tailscale in userspace mode
        
        Args:
            auth_key: Tailscale auth key (optional)
        """
        try:
            # Start tailscaled in userspace mode
            cmd = [
                "tailscaled",
                "--state=/var/lib/tailscale/tailscaled.state",
                "--socket=/var/run/tailscale/tailscaled.sock",
                "--tun=userspace-networking"  # This is the key - userspace networking
            ]
            
            # Run in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give it time to start
            import time
            time.sleep(2)
            
            # Check if running
            if process.poll() is None:
                # Process is running
                
                # If auth key provided, authenticate
                if auth_key:
                    auth_result = subprocess.run(
                        ["tailscale", "up", "--authkey", auth_key],
                        capture_output=True,
                        timeout=10
                    )
                    
                    if auth_result.returncode != 0:
                        return {
                            "success": False,
                            "error": f"Authentication failed: {auth_result.stderr.decode()}"
                        }
                
                return {
                    "success": True,
                    "message": "Tailscale started in userspace mode",
                    "pid": process.pid,
                    "mode": "userspace-networking"
                }
            else:
                return {
                    "success": False,
                    "error": "Tailscaled process exited immediately",
                    "stderr": process.stderr.read().decode()
                }
        except Exception as e:
            logger.error(f"Failed to start Tailscale: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_tailscale_status() -> Dict[str, Any]:
        """Get Tailscale connection status"""
        try:
            result = subprocess.run(
                ["tailscale", "status", "--json"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                import json
                status = json.loads(result.stdout.decode())
                
                return {
                    "success": True,
                    "status": status,
                    "connected": status.get("BackendState") == "Running"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr.decode()
                }
        except Exception as e:
            logger.error(f"Failed to get Tailscale status: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def setup_tailscale() -> Dict[str, Any]:
        """
        Complete Tailscale setup with systemd check and fallback
        """
        # Check if systemd is available
        has_systemd = TailscaleManager.check_systemd_available()
        
        if not has_systemd:
            logger.info("systemd not available - using userspace mode")
            
            # Install in userspace mode
            install_result = await TailscaleManager.install_tailscale_userspace()
            
            if not install_result.get("success"):
                return install_result
            
            return {
                "success": True,
                "mode": "userspace",
                "systemd_available": False,
                "message": "Tailscale installed in userspace mode (systemd workaround)",
                "next_steps": [
                    "Run: tailscaled --tun=userspace-networking",
                    "Run: tailscale up --authkey=YOUR_AUTH_KEY",
                    "Check status: tailscale status"
                ]
            }
        else:
            # Use standard installation with systemd
            return {
                "success": True,
                "mode": "systemd",
                "systemd_available": True,
                "message": "systemd available - use standard installation",
                "next_steps": [
                    "Run: curl -fsSL https://tailscale.com/install.sh | sh",
                    "Run: sudo tailscale up",
                    "Check status: tailscale status"
                ]
            }


# Singleton instance
tailscale_manager = TailscaleManager()
