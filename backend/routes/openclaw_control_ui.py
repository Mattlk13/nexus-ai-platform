"""
OpenClaw Control UI Proxy and Integration
Provides full access to OpenClaw's native Control UI and WebSocket features
"""
from fastapi import APIRouter, Request, Response, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import websockets
import asyncio
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/openclaw/ui", tags=["openclaw-control-ui"])

OPENCLAW_GATEWAY_HTTP = "http://127.0.0.1:18789"
OPENCLAW_GATEWAY_WS = "ws://127.0.0.1:18789"


# ============== HTTP Proxy for Control UI ==============

@router.get("/{path:path}")
async def proxy_control_ui_get(path: str, request: Request):
    """
    Proxy GET requests to OpenClaw Control UI
    Serves the Control UI static files and handles API requests
    """
    try:
        # Forward query parameters
        query_string = str(request.url.query)
        target_url = f"{OPENCLAW_GATEWAY_HTTP}/{path}"
        if query_string:
            target_url += f"?{query_string}"
        
        # Forward headers (excluding host)
        headers = dict(request.headers)
        headers.pop("host", None)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                target_url,
                headers=headers,
                timeout=30.0
            )
        
        # Return response with original headers
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="OpenClaw gateway is not running. Start it first."
        )
    except Exception as e:
        logger.error(f"Control UI proxy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{path:path}")
async def proxy_control_ui_post(path: str, request: Request):
    """
    Proxy POST requests to OpenClaw Control UI
    Handles RPC calls and configuration updates
    """
    try:
        body = await request.body()
        
        target_url = f"{OPENCLAW_GATEWAY_HTTP}/{path}"
        
        headers = dict(request.headers)
        headers.pop("host", None)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                target_url,
                content=body,
                headers=headers,
                timeout=30.0
            )
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="OpenClaw gateway is not running"
        )
    except Exception as e:
        logger.error(f"Control UI POST proxy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== WebSocket Proxy ==============

@router.websocket("/ws")
async def websocket_proxy(websocket: WebSocket):
    """
    Proxy WebSocket connections to OpenClaw Gateway
    Enables real-time chat, events, and Control UI features
    
    This handles:
    - chat.send, chat.history, chat.abort, chat.inject
    - channels.status, sessions.list, cron.*, skills.*
    - config.get, config.set, config.apply
    - logs.tail, status, health, models.list
    """
    await websocket.accept()
    
    openclaw_ws = None
    
    try:
        # Connect to OpenClaw gateway WebSocket
        openclaw_ws = await websockets.connect(
            f"{OPENCLAW_GATEWAY_WS}/",
            extra_headers=websocket.headers
        )
        
        # Bidirectional proxy
        async def forward_to_openclaw():
            """Forward messages from client to OpenClaw"""
            try:
                while True:
                    message = await websocket.receive_text()
                    await openclaw_ws.send(message)
            except WebSocketDisconnect:
                logger.info("Client disconnected")
            except Exception as e:
                logger.error(f"Error forwarding to OpenClaw: {e}")
        
        async def forward_to_client():
            """Forward messages from OpenClaw to client"""
            try:
                async for message in openclaw_ws:
                    await websocket.send_text(message)
            except websockets.exceptions.ConnectionClosed:
                logger.info("OpenClaw WebSocket closed")
            except Exception as e:
                logger.error(f"Error forwarding to client: {e}")
        
        # Run both directions concurrently
        await asyncio.gather(
            forward_to_openclaw(),
            forward_to_client()
        )
    
    except websockets.exceptions.WebSocketException as e:
        logger.error(f"OpenClaw WebSocket connection failed: {e}")
        await websocket.close(code=1011, reason="Gateway connection failed")
    
    except Exception as e:
        logger.error(f"WebSocket proxy error: {e}")
        await websocket.close(code=1011, reason=str(e))
    
    finally:
        if openclaw_ws:
            await openclaw_ws.close()


# ============== Device Management ==============

@router.get("/devices/list")
async def list_pending_devices():
    """
    List pending device pairing requests
    
    Equivalent to: openclaw devices list
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY_HTTP}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "devices.list",
                    "params": {},
                    "id": 1
                },
                timeout=10.0
            )
            
            data = response.json()
            return data.get("result", {})
    
    except Exception as e:
        logger.error(f"Failed to list devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/devices/approve")
async def approve_device(request_id: str):
    """
    Approve a pending device pairing request
    
    Equivalent to: openclaw devices approve <requestId>
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY_HTTP}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "devices.approve",
                    "params": {"requestId": request_id},
                    "id": 1
                },
                timeout=10.0
            )
            
            data = response.json()
            if "error" in data:
                raise HTTPException(status_code=400, detail=data["error"]["message"])
            
            return {"success": True, "result": data.get("result")}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve device: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/devices/revoke")
async def revoke_device(device_id: str, role: str = "user"):
    """
    Revoke a device's access
    
    Equivalent to: openclaw devices revoke --device <id> --role <role>
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY_HTTP}/",
                json={
                    "jsonrpc": "2.0",
                    "method": "devices.revoke",
                    "params": {"deviceId": device_id, "role": role},
                    "id": 1
                },
                timeout=10.0
            )
            
            data = response.json()
            if "error" in data:
                raise HTTPException(status_code=400, detail=data["error"]["message"])
            
            return {"success": True, "result": data.get("result")}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke device: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== RPC Helper ==============

async def openclaw_rpc(method: str, params: dict = None):
    """
    Helper function to call OpenClaw Gateway RPC methods
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY_HTTP}/",
                json={
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params or {},
                    "id": 1
                },
                timeout=30.0
            )
            
            data = response.json()
            if "error" in data:
                raise HTTPException(
                    status_code=400,
                    detail=data["error"].get("message", "RPC error")
                )
            
            return data.get("result")
    
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="OpenClaw gateway is not running"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RPC call failed ({method}): {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Sessions Management ==============

@router.get("/sessions/list")
async def list_sessions():
    """Get list of all sessions"""
    return await openclaw_rpc("sessions.list")


@router.post("/sessions/patch")
async def patch_session(session_key: str, updates: dict):
    """
    Update session settings (thinking/fast/verbose/reasoning overrides)
    """
    return await openclaw_rpc("sessions.patch", {
        "sessionKey": session_key,
        **updates
    })


# ============== Channels Management ==============

@router.get("/channels/status")
async def get_channels_status():
    """Get status of all channels (WhatsApp, Telegram, Discord, Slack)"""
    return await openclaw_rpc("channels.status")


@router.post("/channels/config")
async def update_channel_config(channel: str, config: dict):
    """Update channel configuration"""
    return await openclaw_rpc("config.patch", {
        f"channels.{channel}": config
    })


# ============== Skills Management ==============

@router.get("/skills/list")
async def list_skills():
    """Get list of all skills"""
    return await openclaw_rpc("skills.list")


@router.post("/skills/enable")
async def enable_skill(skill_id: str):
    """Enable a skill"""
    return await openclaw_rpc("skills.enable", {"skillId": skill_id})


@router.post("/skills/disable")
async def disable_skill(skill_id: str):
    """Disable a skill"""
    return await openclaw_rpc("skills.disable", {"skillId": skill_id})


@router.post("/skills/install")
async def install_skill(skill_url: str):
    """Install a new skill"""
    return await openclaw_rpc("skills.install", {"url": skill_url})


# ============== Config Management ==============

@router.get("/config")
async def get_config():
    """Get current OpenClaw configuration"""
    return await openclaw_rpc("config.get")


@router.post("/config/set")
async def set_config(path: str, value: Any):
    """Set a configuration value"""
    return await openclaw_rpc("config.set", {"path": path, "value": value})


@router.post("/config/apply")
async def apply_config(config: dict):
    """Apply full configuration and restart"""
    return await openclaw_rpc("config.apply", config)


# ============== Logs Streaming ==============

@router.get("/logs/tail")
async def tail_logs(lines: int = 100, filter: Optional[str] = None):
    """
    Tail OpenClaw gateway logs
    Returns recent log entries with optional filtering
    """
    try:
        params = {"lines": lines}
        if filter:
            params["filter"] = filter
        
        return await openclaw_rpc("logs.tail", params)
    
    except Exception as e:
        logger.error(f"Failed to tail logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== System Info ==============

@router.get("/system/status")
async def get_system_status():
    """Get system status snapshot"""
    return await openclaw_rpc("status")


@router.get("/system/health")
async def get_system_health():
    """Get system health"""
    return await openclaw_rpc("health")


@router.get("/models/list")
async def list_models():
    """Get list of available models"""
    return await openclaw_rpc("models.list")


def get_control_ui_router():
    """Get the Control UI router"""
    return router
