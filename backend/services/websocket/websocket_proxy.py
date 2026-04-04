"""
WebSocket Proxy for Moltbot Control UI
Handles bidirectional WebSocket communication between client and Moltbot
"""
import logging
import asyncio
import websockets
from websockets.exceptions import ConnectionClosed
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class MoltbotWebSocketProxy:
    """WebSocket proxy handler for Moltbot Control UI"""
    
    def __init__(self, moltbot_port: int = 18789):
        self.moltbot_port = moltbot_port
    
    def _build_moltbot_url(self) -> str:
        """Build Moltbot WebSocket URL"""
        return f"ws://127.0.0.1:{self.moltbot_port}/"
    
    def _build_headers(self, token: Optional[str]) -> Dict[str, str]:
        """Build WebSocket connection headers"""
        headers = {}
        if token:
            headers["X-Auth-Token"] = token
        return headers
    
    async def _forward_client_to_moltbot(
        self,
        client_ws: WebSocket,
        moltbot_ws: websockets.WebSocketClientProtocol
    ) -> None:
        """Forward messages from client to Moltbot"""
        try:
            while True:
                try:
                    data = await client_ws.receive()
                    
                    if data["type"] == "websocket.disconnect":
                        break
                    
                    if data["type"] == "websocket.receive":
                        if "text" in data:
                            await moltbot_ws.send(data["text"])
                        elif "bytes" in data:
                            await moltbot_ws.send(data["bytes"])
                            
                except WebSocketDisconnect:
                    break
                    
        except Exception as e:
            logger.error(f"Client to Moltbot forwarding error: {e}")
    
    async def _forward_moltbot_to_client(
        self,
        client_ws: WebSocket,
        moltbot_ws: websockets.WebSocketClientProtocol
    ) -> None:
        """Forward messages from Moltbot to client"""
        try:
            async for message in moltbot_ws:
                if client_ws.client_state != WebSocketState.CONNECTED:
                    break
                
                if isinstance(message, str):
                    await client_ws.send_text(message)
                else:
                    await client_ws.send_bytes(message)
                    
        except ConnectionClosed as e:
            logger.info(f"Moltbot WebSocket closed: {e}")
        except Exception as e:
            logger.error(f"Moltbot to client forwarding error: {e}")
    
    async def _run_bidirectional_proxy(
        self,
        client_ws: WebSocket,
        moltbot_ws: websockets.WebSocketClientProtocol
    ) -> None:
        """Run bidirectional message forwarding"""
        # Create tasks for both directions
        client_to_moltbot = asyncio.create_task(
            self._forward_client_to_moltbot(client_ws, moltbot_ws)
        )
        moltbot_to_client = asyncio.create_task(
            self._forward_moltbot_to_client(client_ws, moltbot_ws)
        )
        
        # Wait for first task to complete
        done, pending = await asyncio.wait(
            [client_to_moltbot, moltbot_to_client],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    async def _close_client_connection(
        self,
        websocket: WebSocket,
        code: int = 1011,
        reason: str = "Proxy connection ended"
    ) -> None:
        """Safely close client WebSocket connection"""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.close(code=code, reason=reason)
        except Exception as e:
            logger.debug(f"Error closing client connection: {e}")
    
    async def proxy(
        self,
        client_websocket: WebSocket,
        token: Optional[str] = None,
        gateway_running_check: Optional[callable] = None
    ) -> None:
        """
        Proxy WebSocket connection between client and Moltbot
        
        Args:
            client_websocket: FastAPI WebSocket from client
            token: Optional auth token for Moltbot
            gateway_running_check: Optional function to check if gateway is running
        """
        # Accept client connection
        await client_websocket.accept()
        
        # Check if gateway is running
        if gateway_running_check and not gateway_running_check():
            await client_websocket.close(code=1013, reason="OpenClaw not running")
            return
        
        moltbot_url = self._build_moltbot_url()
        headers = self._build_headers(token)
        
        logger.info(f"WebSocket proxy connecting to: {moltbot_url}")
        
        try:
            async with websockets.connect(
                moltbot_url,
                ping_interval=20,
                ping_timeout=20,
                close_timeout=10,
                additional_headers=headers if headers else None,
                origin=f"http://127.0.0.1:{self.moltbot_port}"
            ) as moltbot_ws:
                await self._run_bidirectional_proxy(client_websocket, moltbot_ws)
                
        except Exception as e:
            logger.error(f"WebSocket proxy error: {e}")
        finally:
            await self._close_client_connection(client_websocket)


# Singleton instance
_proxy_instance = None

def get_websocket_proxy(moltbot_port: int = 18789) -> MoltbotWebSocketProxy:
    """Get or create WebSocket proxy instance"""
    global _proxy_instance
    if _proxy_instance is None:
        _proxy_instance = MoltbotWebSocketProxy(moltbot_port)
    return _proxy_instance
