"""
Cloudflare Custom Domain Management
Service for managing custom domains via Cloudflare API
"""
import os
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)


class CloudflareService:
    """Service for Cloudflare custom domain management"""
    
    def __init__(self):
        self.api_key = os.getenv('CLOUDFLARE_API_KEY')
        self.zone_id = os.getenv('CLOUDFLARE_ZONE_ID')
        self.api_base = 'https://api.cloudflare.com/client/v4'
        
    def is_configured(self) -> bool:
        """Check if Cloudflare credentials are configured"""
        return bool(self.api_key and self.zone_id)
    
    async def verify_credentials(self) -> Dict[str, Any]:
        """Verify Cloudflare API credentials"""
        if not self.is_configured():
            return {
                'valid': False,
                'error': 'Cloudflare credentials not configured'
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'{self.api_base}/user/tokens/verify',
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'valid': data.get('success', False),
                        'status': data.get('result', {}).get('status'),
                        'message': 'Credentials verified successfully'
                    }
                else:
                    return {
                        'valid': False,
                        'error': f'API returned status {response.status_code}'
                    }
                    
        except Exception as e:
            logger.error(f'Cloudflare credential verification failed: {e}')
            return {
                'valid': False,
                'error': str(e)
            }
    
    async def list_dns_records(self) -> Dict[str, Any]:
        """List all DNS records in the zone"""
        if not self.is_configured():
            return {'success': False, 'error': 'Not configured'}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'{self.api_base}/zones/{self.zone_id}/dns_records',
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'records': data.get('result', [])
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Failed to fetch records: {response.status_code}'
                    }
                    
        except Exception as e:
            logger.error(f'Failed to list DNS records: {e}')
            return {'success': False, 'error': str(e)}
    
    async def add_dns_record(
        self,
        domain: str,
        target: str,
        record_type: str = 'CNAME',
        proxied: bool = True
    ) -> Dict[str, Any]:
        """
        Add a DNS record for custom domain
        
        Args:
            domain: The custom domain (e.g., "app.example.com")
            target: The target/content (e.g., "myapp.emergentagent.com")
            record_type: DNS record type (A, CNAME, etc.)
            proxied: Whether to proxy through Cloudflare (orange cloud)
        """
        if not self.is_configured():
            return {'success': False, 'error': 'Not configured'}
        
        try:
            payload = {
                'type': record_type,
                'name': domain,
                'content': target,
                'proxied': proxied,
                'ttl': 1 if proxied else 3600
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f'{self.api_base}/zones/{self.zone_id}/dns_records',
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    return {
                        'success': True,
                        'record': data.get('result', {}),
                        'message': f'DNS record created for {domain}'
                    }
                else:
                    error_data = response.json()
                    return {
                        'success': False,
                        'error': error_data.get('errors', [{}])[0].get('message', 'Unknown error')
                    }
                    
        except Exception as e:
            logger.error(f'Failed to add DNS record: {e}')
            return {'success': False, 'error': str(e)}
    
    async def delete_dns_record(self, record_id: str) -> Dict[str, Any]:
        """Delete a DNS record"""
        if not self.is_configured():
            return {'success': False, 'error': 'Not configured'}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f'{self.api_base}/zones/{self.zone_id}/dns_records/{record_id}',
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'message': 'DNS record deleted'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Failed to delete: {response.status_code}'
                    }
                    
        except Exception as e:
            logger.error(f'Failed to delete DNS record: {e}')
            return {'success': False, 'error': str(e)}
    
    async def get_zone_info(self) -> Dict[str, Any]:
        """Get information about the Cloudflare zone"""
        if not self.is_configured():
            return {'success': False, 'error': 'Not configured'}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'{self.api_base}/zones/{self.zone_id}',
                    headers={
                        'Authorization': f'Bearer {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    zone = data.get('result', {})
                    return {
                        'success': True,
                        'zone': {
                            'id': zone.get('id'),
                            'name': zone.get('name'),
                            'status': zone.get('status'),
                            'name_servers': zone.get('name_servers', [])
                        }
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Failed to fetch zone: {response.status_code}'
                    }
                    
        except Exception as e:
            logger.error(f'Failed to get zone info: {e}')
            return {'success': False, 'error': str(e)}
    
    def generate_setup_instructions(self, domain: str, target: str) -> str:
        """Generate setup instructions for custom domain"""
        return f"""
# Custom Domain Setup Instructions

## Domain: {domain}
## Target: {target}

### Option 1: Using Cloudflare (Recommended)

1. **Add your domain to Cloudflare:**
   - Go to https://dash.cloudflare.com
   - Click "Add a Site"
   - Enter your domain and follow the setup wizard

2. **Update nameservers:**
   - At your domain registrar, update nameservers to Cloudflare's nameservers
   - Wait for DNS propagation (can take up to 24 hours)

3. **Add DNS Record:**
   - In Cloudflare dashboard, go to DNS settings
   - Add a CNAME record:
     - Name: {domain}
     - Target: {target}
     - Proxy status: Proxied (orange cloud)

4. **Configure via API (if you have API credentials):**
   - Add your Cloudflare API key and Zone ID to environment variables
   - Use the custom domain management interface in this app

### Option 2: Manual DNS Setup

If not using Cloudflare:

1. **Add DNS Record at your DNS provider:**
   - Type: CNAME
   - Name: {domain}
   - Value: {target}
   - TTL: 3600 (or auto)

2. **Wait for DNS propagation:**
   - Can take 5 minutes to 48 hours depending on provider
   - Test using: `dig {domain}` or `nslookup {domain}`

3. **Verify Setup:**
   - Visit https://{domain} in your browser
   - It should load your application

### Security Notes:
- Always use HTTPS
- Enable Cloudflare SSL/TLS if using Cloudflare
- Keep API credentials secure
"""
