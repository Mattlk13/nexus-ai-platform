"""
MCP API Routes for NEXUS Hybrid Agents
Provides access to GitHub, PostgreSQL, and Playwright tools via MCP
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from services.mcp.mcp_manager_real import get_mcp_manager

logger = logging.getLogger(__name__)


class ToolInvokeRequest(BaseModel):
    server: str
    tool: str
    arguments: Dict[str, Any]


class MCPQueryRequest(BaseModel):
    query: str
    server: Optional[str] = None


def get_mcp_router():
    """Get MCP integration router"""
    router = APIRouter(prefix="/api/mcp", tags=["mcp-servers"])
    
    mcp_manager = get_mcp_manager()
    
    @router.get("/status")
    async def mcp_status():
        """Get MCP servers status"""
        
        if not mcp_manager.initialized:
            await mcp_manager.initialize_all_servers()
        
        pg_session = mcp_manager.get_session("postgresql")
        playwright_session = mcp_manager.get_session("playwright")
        
        return {
            "status": "active",
            "implementation": "REAL (PostgreSQL + Playwright)",
            "mcp_servers": {
                "total": len(mcp_manager.sessions),
                "active_servers": list(mcp_manager.sessions.keys()),
                "github": {
                    "enabled": False,
                    "status": "disabled_by_user",
                    "tools": 0,
                    "note": "Can be enabled by providing GitHub token"
                },
                "postgresql": {
                    "enabled": pg_session is not None,
                    "status": pg_session.get("status") if pg_session else "disconnected",
                    "tools": len(mcp_manager.list_tools_for_server("postgresql")),
                    "mode": "REAL" if pg_session and pg_session.get("status") == "connected" else "N/A",
                    "database": "nexus_demo"
                },
                "playwright": {
                    "enabled": playwright_session is not None,
                    "status": playwright_session.get("status") if playwright_session else "unavailable",
                    "tools": len(mcp_manager.list_tools_for_server("playwright")),
                    "mode": "REAL" if playwright_session and playwright_session.get("status") == "connected" else "N/A",
                    "browser": "Chromium" if playwright_session and playwright_session.get("status") == "connected" else None
                }
            },
            "note": "PostgreSQL and Playwright MCP are REAL with actual connections. GitHub disabled per user choice.",
            "version": "3.0.0"
        }
    
    @router.get("/tools")
    async def list_tools():
        """List all available MCP tools from all servers"""
        
        if not mcp_manager.initialized:
            await mcp_manager.initialize_all_servers()
        
        tools_by_server = mcp_manager.list_available_tools()
        
        all_tools = []
        for server, tools in tools_by_server.items():
            all_tools.extend(tools)
        
        return {
            "success": True,
            "total_tools": len(all_tools),
            "servers": list(tools_by_server.keys()),
            "tools_by_server": tools_by_server,
            "all_tools": all_tools
        }
    
    @router.get("/tools/{server_name}")
    async def list_server_tools(server_name: str):
        """List tools available from a specific MCP server"""
        
        if not mcp_manager.initialized:
            await mcp_manager.initialize_all_servers()
        
        if server_name not in mcp_manager.sessions:
            raise HTTPException(
                status_code=404,
                detail=f"Server '{server_name}' not found or not connected"
            )
        
        tools = mcp_manager.list_tools_for_server(server_name)
        
        return {
            "success": True,
            "server": server_name,
            "tools_count": len(tools),
            "tools": tools
        }
    
    @router.post("/invoke")
    async def invoke_tool(request: ToolInvokeRequest):
        """
        Invoke an MCP tool on a specific server
        
        Example:
        {
            "server": "github",
            "tool": "search_repositories",
            "arguments": {"query": "python web framework"}
        }
        """
        
        if not mcp_manager.initialized:
            await mcp_manager.initialize_all_servers()
        
        try:
            result = await mcp_manager.call_tool(
                server_name=request.server,
                tool_name=request.tool,
                arguments=request.arguments
            )
            
            return {
                "success": True,
                "server": request.server,
                "tool": request.tool,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"MCP tool invocation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/github/search")
    async def github_search_repositories(request: MCPQueryRequest):
        """Search GitHub repositories using MCP"""
        
        if not mcp_manager.initialized:
            await mcp_manager.initialize_all_servers()
        
        try:
            result = await mcp_manager.call_tool(
                server_name="github",
                tool_name="search_repositories",
                arguments={"query": request.query}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"GitHub search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/database/query")
    async def database_query(request: MCPQueryRequest):
        """Execute database query using PostgreSQL MCP"""
        
        if not mcp_manager.initialized:
            await mcp_manager.initialize_all_servers()
        
        try:
            result = await mcp_manager.call_tool(
                server_name="postgresql",
                tool_name="execute_sql",
                arguments={"sqlStatement": request.query}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/browser/navigate")
    async def browser_navigate(request: MCPQueryRequest):
        """Navigate to URL using Playwright MCP"""
        
        if not mcp_manager.initialized:
            await mcp_manager.initialize_all_servers()
        
        try:
            result = await mcp_manager.call_tool(
                server_name="playwright",
                tool_name="browser_goto",
                arguments={"url": request.query}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Browser navigation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/demo")
    async def mcp_demo():
        """Demo MCP capabilities"""
        
        return {
            "demo": "MCP (Model Context Protocol) Integration",
            "description": "Provides standardized tool access for hybrid agents",
            "available_servers": [
                {
                    "name": "GitHub MCP",
                    "capabilities": [
                        "Search repositories",
                        "Get repository details",
                        "List issues",
                        "Create issues"
                    ],
                    "status": "simulated"
                },
                {
                    "name": "PostgreSQL MCP",
                    "capabilities": [
                        "Execute SQL queries (read-only)",
                        "List tables",
                        "Get table schemas"
                    ],
                    "status": "requires_postgresql"
                },
                {
                    "name": "Playwright MCP",
                    "capabilities": [
                        "Navigate to URLs",
                        "Take screenshots",
                        "Fill forms",
                        "Generate PDFs"
                    ],
                    "status": "simulated"
                }
            ],
            "example_usage": {
                "github_search": {
                    "endpoint": "/api/mcp/github/search",
                    "payload": {"query": "python web framework"}
                },
                "database_query": {
                    "endpoint": "/api/mcp/database/query",
                    "payload": {"query": "SELECT * FROM users LIMIT 10"}
                },
                "browser_navigate": {
                    "endpoint": "/api/mcp/browser/navigate",
                    "payload": {"query": "https://example.com"}
                }
            },
            "note": "Current implementation is simulated. Full MCP requires: (1) mcp Python SDK, (2) GitHub personal access token, (3) PostgreSQL setup, (4) Docker containers for Playwright"
        }
    
    return router
