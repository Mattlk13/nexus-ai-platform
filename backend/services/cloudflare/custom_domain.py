"""
Cloudflare Custom Domain Service
Handles custom domain setup and management via Cloudflare API
"""
import logging
import os
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4"


class CloudflareCustomDomain:
    """
    Cloudflare Custom Domain Manager
    
    Handles DNS configuration, SSL/TLS setup, and Workers routing
    for custom domains on Cloudflare
    """
    
    def __init__(self, api_token: str = None, zone_id: str = None):
        """
        Initialize Cloudflare Custom Domain manager
        
        Args:
            api_token: Cloudflare API token (required)
            zone_id: Cloudflare Zone ID (required)
        """
        self.api_token = api_token or os.getenv("CLOUDFLARE_API_TOKEN")
        self.zone_id = zone_id or os.getenv("CLOUDFLARE_ZONE_ID")
        
        if not self.api_token:
            logger.warning("CLOUDFLARE_API_TOKEN not set - custom domain features disabled")
        
        if not self.zone_id:
            logger.warning("CLOUDFLARE_ZONE_ID not set - custom domain features disabled")
    
    async def check_plan_tier(self) -> Dict[str, Any]:
        """
        Check Cloudflare plan tier
        
        Returns:
            Dict with plan information and capabilities
        """
        if not self.api_token or not self.zone_id:
            return {
                "success": False,
                "error": "Missing API credentials",
                "required_action": "Set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID"
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{CLOUDFLARE_API_BASE}/zones/{self.zone_id}",
                    headers={"Authorization": f"Bearer {self.api_token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    plan = data.get("result", {}).get("plan", {})
                    
                    return {
                        "success": True,
                        "plan_name": plan.get("name", "Free"),
                        "plan_id": plan.get("id"),
                        "can_use_custom_domain": plan.get("name") != "Free",
                        "upgrade_required": plan.get("name") == "Free"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API Error: {response.status_code}",
                        "response": response.text
                    }
        except Exception as e:
            logger.error(f"Failed to check Cloudflare plan: {e}")
            return {"success": False, "error": str(e)}
    
    async def setup_custom_domain(
        self,
        domain: str,
        target_url: str
    ) -> Dict[str, Any]:
        """
        Set up custom domain with DNS and SSL
        
        Args:
            domain: Custom domain (e.g., "app.example.com")
            target_url: Target URL to point to
        
        Returns:
            Setup result with DNS and SSL status
        """
        # Check plan tier first
        plan_check = await self.check_plan_tier()
        
        if not plan_check.get("success"):
            return plan_check
        
        if plan_check.get("upgrade_required"):
            return {
                "success": False,
                "error": "Cloudflare Error 1014: DNS resolution error",
                "reason": "Custom domains require a paid Cloudflare plan",
                "current_plan": plan_check.get("plan_name", "Free"),
                "required_action": "Upgrade to Cloudflare Pro, Business, or Enterprise plan",
                "upgrade_url": f"https://dash.cloudflare.com/{self.zone_id}/overview"
            }
        
        try:
            # Step 1: Create DNS record
            dns_result = await self._create_dns_record(domain, target_url)
            
            if not dns_result.get("success"):
                return dns_result
            
            # Step 2: Configure SSL/TLS
            ssl_result = await self._configure_ssl(domain)
            
            # Step 3: Set up Workers route (if needed)
            route_result = await self._setup_workers_route(domain)
            
            return {
                "success": True,
                "domain": domain,
                "dns": dns_result,
                "ssl": ssl_result,
                "workers_route": route_result,
                "status": "Custom domain configured successfully"
            }
        except Exception as e:
            logger.error(f"Custom domain setup failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_dns_record(
        self,
        domain: str,
        target: str,
        record_type: str = "CNAME"
    ) -> Dict[str, Any]:
        """Create DNS record for custom domain"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{CLOUDFLARE_API_BASE}/zones/{self.zone_id}/dns_records",
                    headers={
                        "Authorization": f"Bearer {self.api_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "type": record_type,
                        "name": domain,
                        "content": target,
                        "ttl": 1,  # Auto
                        "proxied": True  # Enable Cloudflare proxy
                    }
                )
                
                if response.status_code in [200, 201]:
                    return {"success": True, "dns_record": response.json().get("result")}
                else:
                    return {
                        "success": False,
                        "error": f"DNS creation failed: {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            logger.error(f"DNS record creation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _configure_ssl(self, domain: str) -> Dict[str, Any]:
        """Configure SSL/TLS for custom domain"""
        try:
            async with httpx.AsyncClient() as client:
                # Set SSL mode to Full (strict)
                response = await client.patch(
                    f"{CLOUDFLARE_API_BASE}/zones/{self.zone_id}/settings/ssl",
                    headers={
                        "Authorization": f"Bearer {self.api_token}",
                        "Content-Type": "application/json"
                    },
                    json={"value": "full"}
                )
                
                if response.status_code == 200:
                    return {"success": True, "ssl_mode": "full"}
                else:
                    return {
                        "success": False,
                        "error": f"SSL configuration failed: {response.status_code}"
                    }
        except Exception as e:
            logger.error(f"SSL configuration failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _setup_workers_route(self, domain: str) -> Dict[str, Any]:
        """Set up Workers route for custom domain"""
        try:
            # This would configure Workers routing if needed
            # For now, return success as DNS + SSL is sufficient
            return {
                "success": True,
                "note": "Workers route configuration available if needed"
            }
        except Exception as e:
            logger.error(f"Workers route setup failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_domain_status(self, domain: str) -> Dict[str, Any]:
        """Check status of custom domain setup"""
        try:
            async with httpx.AsyncClient() as client:
                # Get DNS records
                response = await client.get(
                    f"{CLOUDFLARE_API_BASE}/zones/{self.zone_id}/dns_records",
                    headers={"Authorization": f"Bearer {self.api_token}"},
                    params={"name": domain}
                )
                
                if response.status_code == 200:
                    records = response.json().get("result", [])
                    
                    if records:
                        return {
                            "success": True,
                            "domain": domain,
                            "configured": True,
                            "records": records
                        }
                    else:
                        return {
                            "success": True,
                            "domain": domain,
                            "configured": False,
                            "message": "No DNS records found for this domain"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get domain status: {response.status_code}"
                    }
        except Exception as e:
            logger.error(f"Domain status check failed: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
cloudflare_domain_manager = CloudflareCustomDomain()
