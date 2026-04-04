"""
OpenClaw Real-Time WebSocket Streaming
Provides live updates for dashboard, logs, and system metrics
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set, Dict, Any
import asyncio
import httpx
import logging
import json
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/openclaw/ws", tags=["openclaw-websocket"])

OPENCLAW_GATEWAY = "http://127.0.0.1:18789"

# Active WebSocket connections
active_connections: Set[WebSocket] = set()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.broadcasting = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket)


manager = ConnectionManager()


@router.websocket("/stats")
async def websocket_stats_stream(websocket: WebSocket):
    """
    Real-time gateway statistics stream
    Pushes updates every 2 seconds
    """
    await manager.connect(websocket)
    
    try:
        # Send initial stats immediately
        stats = await get_live_stats()
        await manager.send_personal({
            "type": "stats",
            "data": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, websocket)
        
        # Stream updates
        while True:
            await asyncio.sleep(2)  # Update every 2 seconds
            
            stats = await get_live_stats()
            await manager.send_personal({
                "type": "stats",
                "data": stats,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/logs")
async def websocket_logs_stream(websocket: WebSocket):
    """
    Real-time log streaming
    Streams OpenClaw gateway logs as they occur
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Poll for new logs
            logs = await get_recent_logs()
            
            if logs:
                await manager.send_personal({
                    "type": "logs",
                    "data": logs,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, websocket)
            
            await asyncio.sleep(1)  # Check for logs every second
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket logs error: {e}")
        manager.disconnect(websocket)


@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket):
    """
    Real-time notification stream
    Pushes system events, errors, and autonomous actions
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome notification
        await manager.send_personal({
            "type": "notification",
            "data": {
                "level": "info",
                "title": "Connected",
                "message": "Real-time notifications enabled",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }, websocket)
        
        # Monitor for events
        last_health = None
        
        while True:
            # Check gateway health
            health = await check_gateway_health()
            
            # Notify on health changes
            if last_health is not None and health["healthy"] != last_health["healthy"]:
                await manager.send_personal({
                    "type": "notification",
                    "data": {
                        "level": "success" if health["healthy"] else "error",
                        "title": "Gateway Status Changed",
                        "message": "Gateway is now " + ("healthy" if health["healthy"] else "unhealthy"),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }, websocket)
            
            last_health = health
            
            await asyncio.sleep(5)  # Check every 5 seconds
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket notifications error: {e}")
        manager.disconnect(websocket)


@router.websocket("/autonomous")
async def websocket_autonomous_stream(websocket: WebSocket):
    """
    Real-time autonomous agent activity stream
    Shows tasks, auto-healing, and autonomous decisions
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Get autonomous status
            status = await get_autonomous_status()
            
            await manager.send_personal({
                "type": "autonomous",
                "data": status,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, websocket)
            
            await asyncio.sleep(3)  # Update every 3 seconds
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket autonomous error: {e}")
        manager.disconnect(websocket)


# ============== Helper Functions ==============

async def get_live_stats() -> Dict[str, Any]:
    """Get real-time gateway statistics"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Get status
            status_resp = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={"jsonrpc": "2.0", "method": "status", "id": 1}
            )
            
            # Get sessions
            sessions_resp = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={"jsonrpc": "2.0", "method": "sessions.list", "id": 2}
            )
            
            status_data = status_resp.json().get("result", {})
            sessions_data = sessions_resp.json().get("result", {})
            
            return {
                "healthy": status_data.get("healthy", False),
                "uptime": status_data.get("uptime", 0),
                "version": status_data.get("version", "unknown"),
                "active_sessions": len(sessions_data.get("sessions", [])),
                "connections": status_data.get("connections", 0)
            }
    except Exception as e:
        logger.error(f"Failed to get live stats: {e}")
        return {
            "healthy": False,
            "uptime": 0,
            "version": "unknown",
            "active_sessions": 0,
            "connections": 0,
            "error": str(e)
        }


async def get_recent_logs() -> list:
    """Get recent gateway logs"""
    try:
        # In production, this would tail actual log files
        # For now, return structured log entries
        return []
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        return []


async def check_gateway_health() -> Dict[str, Any]:
    """Check gateway health status"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{OPENCLAW_GATEWAY}/",
                json={"jsonrpc": "2.0", "method": "status", "id": 1}
            )
            
            if response.status_code == 200:
                result = response.json().get("result", {})
                return {
                    "healthy": result.get("healthy", True),
                    "uptime": result.get("uptime", 0)
                }
            
            return {"healthy": False, "uptime": 0}
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"healthy": False, "uptime": 0}


async def get_autonomous_status() -> Dict[str, Any]:
    """Get autonomous agent status"""
    try:
        # This would fetch from the autonomous system
        # For now, return mock status
        return {
            "enabled": False,
            "mode": "manual",
            "tasks_running": 0,
            "auto_heals_today": 0
        }
    except Exception as e:
        logger.error(f"Failed to get autonomous status: {e}")
        return {"enabled": False, "mode": "manual"}


# ============== Broadcast Utilities ==============

async def broadcast_notification(notification: Dict[str, Any]):
    """Broadcast notification to all connected clients"""
    await manager.broadcast({
        "type": "notification",
        "data": notification
    })


async def broadcast_status_change(status: str, message: str):
    """Broadcast status change to all clients"""
    await manager.broadcast({
        "type": "status_change",
        "data": {
            "status": status,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    })


def get_websocket_router():
    """Get the WebSocket router"""
    return router
