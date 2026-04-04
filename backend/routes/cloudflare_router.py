"""
Cloudflare Custom Domain API Routes
Endpoints for managing custom domains via Cloudflare
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from services.cloudflare import CloudflareService

logger = logging.getLogger(__name__)


class DNSRecordCreate(BaseModel):
    domain: str
    target: str
    record_type: str = 'CNAME'
    proxied: bool = True


class DNSRecordDelete(BaseModel):
    record_id: str


def get_cloudflare_router():
    """Get Cloudflare custom domain router"""
    router = APIRouter(prefix="/api/cloudflare", tags=["cloudflare"])
    
    cloudflare_service = CloudflareService()
    
    @router.get("/status")
    async def cloudflare_status():
        """Check Cloudflare integration status"""
        is_configured = cloudflare_service.is_configured()
        
        if not is_configured:
            return {
                'configured': False,
                'message': 'Cloudflare API credentials not set',
                'instructions': 'Add CLOUDFLARE_API_KEY and CLOUDFLARE_ZONE_ID to environment variables'
            }
        
        # Verify credentials
        verification = await cloudflare_service.verify_credentials()
        
        return {
            'configured': True,
            'credentials_valid': verification.get('valid', False),
            'message': verification.get('message') or verification.get('error'),
            'status': verification.get('status')
        }
    
    @router.post("/verify")
    async def verify_cloudflare_credentials():
        """Verify Cloudflare API credentials"""
        result = await cloudflare_service.verify_credentials()
        
        if not result.get('valid'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Invalid credentials'))
        
        return result
    
    @router.get("/zone")
    async def get_zone_info():
        """Get Cloudflare zone information"""
        result = await cloudflare_service.get_zone_info()
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to fetch zone info'))
        
        return result.get('zone', {})
    
    @router.get("/dns/records")
    async def list_dns_records():
        """List all DNS records in the Cloudflare zone"""
        result = await cloudflare_service.list_dns_records()
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to fetch DNS records'))
        
        return {
            'success': True,
            'records': result.get('records', []),
            'count': len(result.get('records', []))
        }
    
    @router.post("/dns/records")
    async def create_dns_record(record: DNSRecordCreate):
        """Create a new DNS record for custom domain"""
        result = await cloudflare_service.add_dns_record(
            domain=record.domain,
            target=record.target,
            record_type=record.record_type,
            proxied=record.proxied
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to create DNS record'))
        
        return result
    
    @router.delete("/dns/records/{record_id}")
    async def delete_dns_record(record_id: str):
        """Delete a DNS record"""
        result = await cloudflare_service.delete_dns_record(record_id)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to delete DNS record'))
        
        return result
    
    @router.get("/setup-instructions")
    async def get_setup_instructions(domain: str, target: str):
        """Get setup instructions for custom domain"""
        instructions = cloudflare_service.generate_setup_instructions(domain, target)
        
        return {
            'success': True,
            'domain': domain,
            'target': target,
            'instructions': instructions
        }
    
    return router
