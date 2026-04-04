"""
API Routes for Community MCP Servers and Token Management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from services.mcp.community_mcp_servers import (
    get_filesystem_mcp,
    get_fetch_mcp,
    get_memory_mcp
)
from services.mcp.mcp_inspector import get_inspector
from services.security.token_manager import get_token_manager

logger = logging.getLogger(__name__)


# Request Models
class FileReadRequest(BaseModel):
    path: str


class FileWriteRequest(BaseModel):
    path: str
    content: str


class FetchRequest(BaseModel):
    url: str
    method: str = "GET"
    headers: Optional[Dict] = None
    body: Optional[Dict] = None


class MemoryStoreRequest(BaseModel):
    agent_id: str
    key: str
    value: Any
    metadata: Optional[Dict] = None


class MemoryRetrieveRequest(BaseModel):
    agent_id: str
    key: str


class TokenStoreRequest(BaseModel):
    service: str
    token: str
    metadata: Optional[Dict] = None
    expires_in_days: Optional[int] = None


def get_community_mcp_router():
    """Get community MCP servers router"""
    router = APIRouter(prefix="/api/mcp/community", tags=["mcp-community"])
    
    filesystem = get_filesystem_mcp()
    fetch = get_fetch_mcp()
    memory = get_memory_mcp()
    inspector = get_inspector()
    token_mgr = get_token_manager()
    
    # ========== Filesystem MCP ==========
    
    @router.post("/filesystem/read")
    async def read_file(request: FileReadRequest):
        """Read file contents"""
        result = await filesystem.read_file(request.path)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    @router.post("/filesystem/write")
    async def write_file(request: FileWriteRequest):
        """Write file contents"""
        result = await filesystem.write_file(request.path, request.content)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    @router.post("/filesystem/list")
    async def list_directory(request: FileReadRequest):
        """List directory contents"""
        result = await filesystem.list_directory(request.path)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    # ========== Fetch MCP ==========
    
    @router.post("/fetch")
    async def fetch_url(request: FetchRequest):
        """Make HTTP request"""
        result = await fetch.fetch(
            request.url,
            request.method,
            request.headers,
            request.body
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    @router.get("/fetch/get")
    async def fetch_get(url: str):
        """GET request"""
        result = await fetch.get(url)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    # ========== Memory MCP ==========
    
    @router.post("/memory/store")
    async def store_memory(request: MemoryStoreRequest):
        """Store agent memory"""
        result = await memory.store_memory(
            request.agent_id,
            request.key,
            request.value,
            request.metadata
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    @router.post("/memory/retrieve")
    async def retrieve_memory(request: MemoryRetrieveRequest):
        """Retrieve agent memory"""
        result = await memory.retrieve_memory(
            request.agent_id,
            request.key
        )
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    
    @router.get("/memory/list/{agent_id}")
    async def list_memories(agent_id: str):
        """List all memories for an agent"""
        result = await memory.list_memories(agent_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    # ========== MCP Inspector ==========
    
    @router.get("/inspector/info")
    async def inspector_info():
        """Get MCP Inspector information"""
        return inspector.get_server_info()
    
    # ========== Token Management ==========
    
    @router.post("/tokens/store")
    async def store_token(request: TokenStoreRequest):
        """Store encrypted token"""
        success = token_mgr.store_token(
            request.service,
            request.token,
            request.metadata,
            request.expires_in_days
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store token")
        return {"success": True, "service": request.service}
    
    @router.get("/tokens/list")
    async def list_tokens():
        """List all stored tokens (metadata only)"""
        return token_mgr.list_tokens()
    
    @router.delete("/tokens/{service}")
    async def delete_token(service: str):
        """Delete a stored token"""
        success = token_mgr.delete_token(service)
        if not success:
            raise HTTPException(status_code=404, detail="Token not found")
        return {"success": True, "service": service}
    
    # ========== Status ==========
    
    @router.get("/status")
    async def community_mcp_status():
        """Get status of all community MCP servers"""
        return {
            "status": "active",
            "servers": {
                "filesystem": {
                    "enabled": True,
                    "mode": "REAL",
                    "allowed_paths": filesystem.allowed_paths,
                    "tools": ["read_file", "write_file", "list_directory"]
                },
                "fetch": {
                    "enabled": True,
                    "mode": "REAL",
                    "tools": ["fetch", "get", "post"]
                },
                "memory": {
                    "enabled": True,
                    "mode": "REAL",
                    "storage_path": str(memory.storage_path),
                    "tools": ["store_memory", "retrieve_memory", "list_memories"]
                },
                "inspector": {
                    "enabled": inspector.inspector_available,
                    "ui_url": "http://localhost:5173",
                    "tools": ["inspect_server", "get_server_info"]
                },
                "token_manager": {
                    "enabled": True,
                    "encrypted": True,
                    "tools": ["store_token", "get_token", "list_tokens", "delete_token", "rotate_token"]
                }
            },
            "total_tools": 17,
            "version": "1.0.0"
        }
    
    return router
