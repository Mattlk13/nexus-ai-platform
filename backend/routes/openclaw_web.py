"""
OpenClaw Complete Web Integration
Implements all features from https://docs.openclaw.ai/web and GitHub repository
"""
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import asyncio
import logging
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/openclaw/web", tags=["openclaw-web"])

OPENCLAW_GATEWAY = "http://127.0.0.1:18789"


# ============== Dashboard API ==============

class DashboardInfo(BaseModel):
    gateway_url: str
    control_ui_url: str
    base_path: str = "/"
    enabled: bool = True
    version: str
    uptime: int
    connections: int


@router.get("/dashboard/info")
async def get_dashboard_info():
    """
    Get dashboard information
    Based on: https://docs.openclaw.ai/web/dashboard
    """
    try:
        async with httpx.AsyncClient() as client:
            # Get gateway status
            status_response = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={"jsonrpc": "2.0", "method": "status", "id": 1},
                timeout=5.0
            )
            
            status = status_response.json().get("result", {})
            
            return {
                "gateway_url": "http://127.0.0.1:18789",
                "control_ui_url": "/api/openclaw/ui/",
                "base_path": "/",
                "enabled": True,
                "version": status.get("version", "2026.3.2"),
                "uptime": status.get("uptime", 0),
                "connections": status.get("connections", 0),
                "features": [
                    "Control UI",
                    "WebSocket Gateway",
                    "Webhooks",
                    "Device Management",
                    "Cron Jobs",
                    "Skills",
                    "Channels"
                ]
            }
    except Exception as e:
        logger.error(f"Failed to get dashboard info: {e}")
        # Try to get version from local gateway if API fails
        try:
            import subprocess
            version_output = subprocess.check_output(
                ["openclaw", "--version"],
                stderr=subprocess.STDOUT,
                timeout=2
            ).decode().strip()
            # Extract version from output like "OpenClaw 2026.4.1 (da64a97)"
            version = version_output.split()[1] if len(version_output.split()) > 1 else "2026.4.1"
        except:
            version = "Gateway Offline"
        
        return {
            "gateway_url": "http://127.0.0.1:18789",
            "control_ui_url": "/api/openclaw/ui/",
            "base_path": "/",
            "enabled": False,
            "version": version,
            "uptime": 0,
            "connections": 0,
            "error": str(e),
            "note": "Gateway API not responding - version retrieved from CLI"
        }


@router.get("/dashboard/quick-stats")
async def get_dashboard_quick_stats():
    """Get quick stats for dashboard overview"""
    try:
        async with httpx.AsyncClient() as client:
            # Get multiple stats in parallel
            status_task = client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={"jsonrpc": "2.0", "method": "status", "id": 1}
            )
            
            sessions_task = client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={"jsonrpc": "2.0", "method": "sessions.list", "id": 2}
            )
            
            models_task = client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={"jsonrpc": "2.0", "method": "models.list", "id": 3}
            )
            
            status_resp, sessions_resp, models_resp = await asyncio.gather(
                status_task, sessions_task, models_task,
                return_exceptions=True
            )
            
            stats = {
                "active_sessions": 0,
                "total_models": 0,
                "gateway_healthy": False,
                "uptime_hours": 0
            }
            
            if not isinstance(status_resp, Exception):
                status_data = status_resp.json().get("result", {})
                stats["gateway_healthy"] = status_data.get("healthy", False)
                stats["uptime_hours"] = status_data.get("uptime", 0) // 3600
            
            if not isinstance(sessions_resp, Exception):
                sessions_data = sessions_resp.json().get("result", {})
                stats["active_sessions"] = len(sessions_data.get("sessions", []))
            
            if not isinstance(models_resp, Exception):
                models_data = models_resp.json().get("result", {})
                stats["total_models"] = len(models_data.get("providers", {}).get("emergent-gpt", {}).get("models", []))
            
            return stats
            
    except Exception as e:
        logger.error(f"Failed to get quick stats: {e}")
        return {
            "active_sessions": 0,
            "total_models": 0,
            "gateway_healthy": False,
            "uptime_hours": 0,
            "error": str(e)
        }


# ============== Webhooks API ==============

class WebhookConfig(BaseModel):
    enabled: bool = True
    url: str
    secret: Optional[str] = None
    events: List[str] = ["chat.message", "cron.run", "error"]


class WebhookPayload(BaseModel):
    event: str
    timestamp: str
    data: Dict[str, Any]
    signature: Optional[str] = None


@router.post("/webhooks/configure")
async def configure_webhooks(config: WebhookConfig):
    """
    Configure webhook settings
    Based on: https://docs.openclaw.ai/web#webhooks
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "config.patch",
                    "params": {
                        "hooks.enabled": config.enabled,
                        "hooks.url": config.url,
                        "hooks.secret": config.secret,
                        "hooks.events": config.events
                    },
                    "id": 1
                }
            )
            
            return {
                "success": True,
                "message": "Webhooks configured",
                "config": config.dict()
            }
    except Exception as e:
        logger.error(f"Failed to configure webhooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhooks/status")
async def get_webhook_status():
    """Get current webhook configuration and status"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "config.get",
                    "params": {"path": "hooks"},
                    "id": 1
                }
            )
            
            hooks_config = response.json().get("result", {})
            
            return {
                "enabled": hooks_config.get("enabled", False),
                "url": hooks_config.get("url"),
                "events": hooks_config.get("events", []),
                "total_sent": hooks_config.get("stats", {}).get("total", 0),
                "failed": hooks_config.get("stats", {}).get("failed", 0)
            }
    except Exception as e:
        logger.error(f"Failed to get webhook status: {e}")
        return {
            "enabled": False,
            "url": None,
            "events": [],
            "total_sent": 0,
            "failed": 0,
            "error": str(e)
        }


@router.post("/webhooks/test")
async def test_webhook(url: str, secret: Optional[str] = None):
    """Test webhook endpoint"""
    try:
        test_payload = {
            "event": "test",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {"message": "Test webhook from OpenClaw"}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=test_payload,
                headers={"X-OpenClaw-Secret": secret} if secret else {},
                timeout=10.0
            )
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.text[:200]
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============== Configuration Management ==============

@router.get("/config/full")
async def get_full_config():
    """Get complete OpenClaw configuration"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "config.get",
                    "id": 1
                }
            )
            
            return response.json().get("result", {})
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/update")
async def update_config(updates: Dict[str, Any]):
    """Update configuration values"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "config.patch",
                    "params": updates,
                    "id": 1
                }
            )
            
            return {
                "success": True,
                "message": "Configuration updated",
                "updates": updates
            }
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/validate")
async def validate_config(config: Dict[str, Any]):
    """Validate configuration before applying"""
    # Basic validation
    errors = []
    warnings = []
    
    # Check required fields
    if "gateway" not in config:
        errors.append("Missing 'gateway' configuration")
    
    # Check port
    if "gateway" in config and "port" in config["gateway"]:
        port = config["gateway"]["port"]
        if not (1024 <= port <= 65535):
            errors.append(f"Invalid port: {port}. Must be between 1024-65535")
    
    # Check bind mode
    if "gateway" in config and "bind" in config["gateway"]:
        valid_binds = ["loopback", "lan", "tailnet"]
        if config["gateway"]["bind"] not in valid_binds:
            warnings.append(f"Unusual bind mode: {config['gateway']['bind']}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


@router.post("/config/export")
async def export_config():
    """Export current configuration as JSON"""
    try:
        config = await get_full_config()
        
        # Create export with metadata
        export = {
            "version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "openclaw_version": "2026.3.2",
            "config": config
        }
        
        return Response(
            content=json.dumps(export, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=openclaw-config-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Security & Auth ==============

@router.get("/security/auth-info")
async def get_auth_info():
    """Get authentication configuration info"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "config.get",
                    "params": {"path": "gateway.auth"},
                    "id": 1
                }
            )
            
            auth_config = response.json().get("result", {})
            
            return {
                "mode": auth_config.get("mode", "token"),
                "allowTailscale": auth_config.get("allowTailscale", False),
                "requireAuth": True,
                "tokenConfigured": bool(auth_config.get("token")),
                "passwordConfigured": bool(auth_config.get("password"))
            }
    except Exception as e:
        return {
            "mode": "unknown",
            "allowTailscale": False,
            "requireAuth": True,
            "tokenConfigured": False,
            "passwordConfigured": False,
            "error": str(e)
        }


@router.post("/security/rotate-token")
async def rotate_gateway_token():
    """Generate and set a new gateway token"""
    import secrets
    
    new_token = secrets.token_hex(32)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "config.patch",
                    "params": {"gateway.auth.token": new_token},
                    "id": 1
                }
            )
            
            return {
                "success": True,
                "message": "Token rotated successfully",
                "new_token": new_token,
                "warning": "Update all clients with the new token"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/security/allowed-origins")
async def get_allowed_origins():
    """Get Control UI allowed origins"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "config.get",
                    "params": {"path": "gateway.controlUi.allowedOrigins"},
                    "id": 1
                }
            )
            
            origins = response.json().get("result", [])
            
            return {
                "origins": origins,
                "count": len(origins)
            }
    except Exception as e:
        return {"origins": [], "count": 0, "error": str(e)}


@router.post("/security/add-origin")
async def add_allowed_origin(origin: str):
    """Add an allowed origin for Control UI"""
    try:
        # Get current origins
        current = await get_allowed_origins()
        origins = current.get("origins", [])
        
        if origin not in origins:
            origins.append(origin)
            
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{OPENCLAW_GATEWAY}/",
                    json={
                        "jsonrpc": "2.0",
                        "method": "config.patch",
                        "params": {"gateway.controlUi.allowedOrigins": origins},
                        "id": 1
                    }
                )
        
        return {
            "success": True,
            "message": f"Origin added: {origin}",
            "origins": origins
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Models & Providers ==============

@router.get("/models/providers")
async def get_model_providers():
    """Get all configured model providers"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "models.list",
                    "id": 1
                }
            )
            
            models_data = response.json().get("result", {})
            providers = models_data.get("providers", {})
            
            # Format provider info
            provider_list = []
            for provider_id, provider_data in providers.items():
                provider_list.append({
                    "id": provider_id,
                    "name": provider_data.get("name", provider_id),
                    "models": provider_data.get("models", []),
                    "enabled": provider_data.get("enabled", True)
                })
            
            return {
                "providers": provider_list,
                "total": len(provider_list)
            }
    except Exception as e:
        return {"providers": [], "total": 0, "error": str(e)}


@router.get("/models/active")
async def get_active_models():
    """Get list of active/available models"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "models.list",
                    "id": 1
                }
            )
            
            models_data = response.json().get("result", {})
            
            # Flatten all models
            all_models = []
            for provider_id, provider_data in models_data.get("providers", {}).items():
                for model in provider_data.get("models", []):
                    all_models.append({
                        "id": model.get("id"),
                        "name": model.get("name"),
                        "provider": provider_id,
                        "contextWindow": model.get("contextWindow"),
                        "capabilities": model.get("capabilities", [])
                    })
            
            return {
                "models": all_models,
                "total": len(all_models)
            }
    except Exception as e:
        return {"models": [], "total": 0, "error": str(e)}


# ============== System Information ==============

@router.get("/system/info")
async def get_system_info():
    """Get comprehensive system information"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "status",
                    "id": 1
                }
            )
            
            status = response.json().get("result", {})
            
            return {
                "version": status.get("version", "2026.3.2"),
                "uptime": status.get("uptime", 0),
                "platform": status.get("platform", "linux"),
                "node_version": status.get("nodeVersion", "22.22.2"),
                "gateway_port": 18789,
                "control_ui_enabled": True,
                "webhooks_enabled": status.get("hooksEnabled", False),
                "healthy": status.get("healthy", True)
            }
    except Exception as e:
        # Fallback to CLI version check if API fails
        try:
            import subprocess
            version_output = subprocess.check_output(
                ["openclaw", "--version"],
                stderr=subprocess.STDOUT,
                timeout=2
            ).decode().strip()
            version = version_output.split()[1] if len(version_output.split()) > 1 else "2026.4.1"
        except:
            version = "Gateway Offline"
        
        return {
            "version": version,
            "uptime": 0,
            "healthy": False,
            "error": str(e),
            "fallback": "CLI version check"
        }


def get_web_router():
    """Get the web features router"""
    return router
