"""
Additional Community MCP Servers for NEXUS
Filesystem, Fetch, Memory, and enhanced browser automation
"""
import os
import logging
import httpx
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class FilesystemMCP:
    """Filesystem operations MCP server"""
    
    def __init__(self, allowed_paths: Optional[List[str]] = None):
        """
        Initialize filesystem MCP
        
        Args:
            allowed_paths: List of allowed paths for security
        """
        self.allowed_paths = allowed_paths or ["/app/backend/data", "/tmp"]
        logger.info(f"Filesystem MCP initialized with paths: {self.allowed_paths}")
    
    def _is_path_allowed(self, path: str) -> bool:
        """Check if path is within allowed directories"""
        resolved = Path(path).resolve()
        return any(
            str(resolved).startswith(allowed)
            for allowed in self.allowed_paths
        )
    
    async def read_file(self, path: str) -> Dict[str, Any]:
        """Read file contents"""
        if not self._is_path_allowed(path):
            return {"success": False, "error": "Path not allowed"}
        
        try:
            content = Path(path).read_text()
            return {
                "success": True,
                "content": content,
                "size": len(content),
                "mode": "REAL_FILESYSTEM"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write content to file"""
        if not self._is_path_allowed(path):
            return {"success": False, "error": "Path not allowed"}
        
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content)
            return {
                "success": True,
                "path": path,
                "size": len(content),
                "mode": "REAL_FILESYSTEM"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_directory(self, path: str) -> Dict[str, Any]:
        """List directory contents"""
        if not self._is_path_allowed(path):
            return {"success": False, "error": "Path not allowed"}
        
        try:
            dir_path = Path(path)
            items = [
                {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                }
                for item in dir_path.iterdir()
            ]
            return {
                "success": True,
                "path": path,
                "items": items,
                "count": len(items),
                "mode": "REAL_FILESYSTEM"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class FetchMCP:
    """HTTP requests MCP server"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("Fetch MCP initialized")
    
    async def fetch(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict] = None,
        body: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request"""
        try:
            response = await self.client.request(
                method,
                url,
                headers=headers or {},
                json=body if body else None
            )
            
            return {
                "success": True,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text,
                "json": response.json() if response.headers.get("content-type", "").startswith("application/json") else None,
                "mode": "REAL_FETCH"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get(self, url: str, headers: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request"""
        return await self.fetch(url, "GET", headers)
    
    async def post(
        self,
        url: str,
        body: Dict,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """POST request"""
        return await self.fetch(url, "POST", headers, body)
    
    async def cleanup(self):
        """Close HTTP client"""
        await self.client.aclose()


class MemoryMCP:
    """Persistent memory for AI agents"""
    
    def __init__(self, storage_path: str = "/app/backend/data/agent_memory"):
        """
        Initialize memory MCP
        
        Args:
            storage_path: Path to store memory data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Memory MCP initialized at {storage_path}")
    
    async def store_memory(
        self,
        agent_id: str,
        key: str,
        value: Any,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Store memory for an agent"""
        try:
            agent_dir = self.storage_path / agent_id
            agent_dir.mkdir(exist_ok=True)
            
            memory_file = agent_dir / f"{key}.json"
            memory_data = {
                "key": key,
                "value": value,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "agent_id": agent_id
            }
            
            memory_file.write_text(json.dumps(memory_data, indent=2))
            
            return {
                "success": True,
                "agent_id": agent_id,
                "key": key,
                "mode": "REAL_MEMORY"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def retrieve_memory(
        self,
        agent_id: str,
        key: str
    ) -> Dict[str, Any]:
        """Retrieve memory for an agent"""
        try:
            memory_file = self.storage_path / agent_id / f"{key}.json"
            
            if not memory_file.exists():
                return {"success": False, "error": "Memory not found"}
            
            memory_data = json.loads(memory_file.read_text())
            
            return {
                "success": True,
                "agent_id": agent_id,
                "key": key,
                "value": memory_data["value"],
                "metadata": memory_data.get("metadata", {}),
                "created_at": memory_data.get("created_at"),
                "mode": "REAL_MEMORY"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_memories(self, agent_id: str) -> Dict[str, Any]:
        """List all memories for an agent"""
        try:
            agent_dir = self.storage_path / agent_id
            
            if not agent_dir.exists():
                return {"success": True, "memories": [], "count": 0}
            
            memories = []
            for memory_file in agent_dir.glob("*.json"):
                memory_data = json.loads(memory_file.read_text())
                memories.append({
                    "key": memory_data["key"],
                    "created_at": memory_data.get("created_at"),
                    "has_metadata": bool(memory_data.get("metadata"))
                })
            
            return {
                "success": True,
                "agent_id": agent_id,
                "memories": memories,
                "count": len(memories),
                "mode": "REAL_MEMORY"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singletons
_filesystem_mcp = None
_fetch_mcp = None
_memory_mcp = None

def get_filesystem_mcp() -> FilesystemMCP:
    """Get filesystem MCP singleton"""
    global _filesystem_mcp
    if _filesystem_mcp is None:
        _filesystem_mcp = FilesystemMCP()
    return _filesystem_mcp

def get_fetch_mcp() -> FetchMCP:
    """Get fetch MCP singleton"""
    global _fetch_mcp
    if _fetch_mcp is None:
        _fetch_mcp = FetchMCP()
    return _fetch_mcp

def get_memory_mcp() -> MemoryMCP:
    """Get memory MCP singleton"""
    global _memory_mcp
    if _memory_mcp is None:
        _memory_mcp = MemoryMCP()
    return _memory_mcp
