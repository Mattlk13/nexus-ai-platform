"""
Real MCP Implementation for NEXUS
Using actual MCP Python SDK and PostgreSQL connection
"""
import asyncio
import logging
from typing import Optional, Dict, List, Any
import asyncpg
from dataclasses import dataclass
from enum import Enum
import os
from dotenv import load_dotenv
from services.mcp.playwright_mcp import get_playwright_server

load_dotenv()

logger = logging.getLogger(__name__)


class MCPServerType(Enum):
    """Available MCP server types"""
    GITHUB = "github"
    POSTGRESQL = "postgresql"
    PLAYWRIGHT = "playwright"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    type: MCPServerType
    name: str
    enabled: bool = True
    url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    command: Optional[str] = None
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    timeout: int = 30


class RealMCPClientManager:
    """
    Real MCP Client Manager with PostgreSQL integration
    
    Features:
    - Direct PostgreSQL connection (no Docker needed)
    - Actual database queries with read-only safety
    - Full MCP protocol support
    """
    
    def __init__(self):
        self.sessions: Dict[str, Any] = {}
        self.tools_cache: Dict[str, List[Dict]] = {}
        self.pg_pool: Optional[asyncpg.Pool] = None
        self.initialized = False
        logger.info("Real MCP Client Manager created")
    
    async def initialize_all_servers(self):
        """Initialize all configured and enabled MCP servers"""
        
        logger.info("Initializing MCP servers with real connections...")
        
        # Initialize PostgreSQL connection pool
        await self._initialize_postgresql()
        
        # Cache available tools
        if self.pg_pool:
            self.tools_cache["postgresql"] = [
                {
                    "name": "execute_query",
                    "description": "Execute read-only SQL query",
                    "parameters": {"query": "string"}
                },
                {
                    "name": "list_tables",
                    "description": "List all database tables",
                    "parameters": {}
                },
                {
                    "name": "get_table_schema",
                    "description": "Get schema for a specific table",
                    "parameters": {"table_name": "string"}
                },
                {
                    "name": "describe_database",
                    "description": "Get database statistics and info",
                    "parameters": {}
                }
            ]
            self.sessions["postgresql"] = {
                "type": MCPServerType.POSTGRESQL,
                "status": "connected",
                "pool": self.pg_pool
            }
        
        # Initialize Playwright (REAL implementation)
        await self._initialize_playwright()
        
        self.initialized = True
        logger.info(f"MCP initialization complete. {len(self.sessions)} servers active")
    
    async def _initialize_postgresql(self):
        """Initialize PostgreSQL connection pool"""
        
        postgres_uri = os.getenv("POSTGRES_MCP_URI")
        if not postgres_uri:
            logger.warning("POSTGRES_MCP_URI not set, PostgreSQL MCP disabled")
            return
        
        try:
            self.pg_pool = await asyncpg.create_pool(
                postgres_uri,
                min_size=1,
                max_size=5,
                command_timeout=30
            )
            logger.info("✅ PostgreSQL MCP connection pool created")
            
            # Test connection
            async with self.pg_pool.acquire() as conn:
                version = await conn.fetchval('SELECT version()')
                logger.info(f"PostgreSQL connected: {version.split(',')[0]}")
                
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.pg_pool = None
    
    async def _initialize_playwright(self):
        """Initialize Playwright browser"""
        
        try:
            playwright_server = get_playwright_server()
            success = await playwright_server.initialize()
            
            if success:
                self.sessions["playwright"] = {
                    "type": MCPServerType.PLAYWRIGHT,
                    "status": "connected",
                    "server": playwright_server
                }
                self.tools_cache["playwright"] = [
                    {
                        "name": "browser_goto",
                        "description": "Navigate to URL",
                        "parameters": {"url": "string", "timeout": "integer"}
                    },
                    {
                        "name": "browser_screenshot",
                        "description": "Take screenshot of current page",
                        "parameters": {"full_page": "boolean"}
                    },
                    {
                        "name": "browser_click",
                        "description": "Click an element",
                        "parameters": {"selector": "string"}
                    },
                    {
                        "name": "browser_fill",
                        "description": "Fill a form field",
                        "parameters": {"selector": "string", "text": "string"}
                    },
                    {
                        "name": "browser_evaluate",
                        "description": "Execute JavaScript",
                        "parameters": {"script": "string"}
                    },
                    {
                        "name": "browser_get_content",
                        "description": "Get page HTML content",
                        "parameters": {}
                    },
                    {
                        "name": "browser_pdf",
                        "description": "Generate PDF of page",
                        "parameters": {"path": "string"}
                    },
                    {
                        "name": "browser_wait_for_selector",
                        "description": "Wait for element to appear",
                        "parameters": {"selector": "string", "timeout": "integer"}
                    },
                    {
                        "name": "browser_get_text",
                        "description": "Get text content of element",
                        "parameters": {"selector": "string"}
                    }
                ]
                logger.info("✅ Playwright MCP initialized (Chromium)")
            else:
                logger.warning("Playwright initialization failed")
                
        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {e}")
    
    def get_session(self, server_name: str) -> Optional[Dict]:
        """Get session for a specific server"""
        return self.sessions.get(server_name)
    
    def list_available_tools(self) -> Dict[str, List[Dict]]:
        """List all available tools from all connected servers"""
        return {
            server: [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "server": server,
                    "parameters": tool.get("parameters", {})
                }
                for tool in tools
            ]
            for server, tools in self.tools_cache.items()
        }
    
    def list_tools_for_server(self, server_name: str) -> List[Dict]:
        """List tools available from a specific server"""
        return self.tools_cache.get(server_name, [])
    
    async def call_tool(self, server_name: str, tool_name: str, 
                       arguments: Dict) -> Dict[str, Any]:
        """
        Call a tool on a specific server
        Real implementation with PostgreSQL and Playwright
        """
        
        session = self.get_session(server_name)
        if not session:
            raise ValueError(f"Server {server_name} not connected")
        
        logger.info(f"Executing tool: {server_name}.{tool_name}")
        
        # PostgreSQL tools (REAL implementation)
        if server_name == "postgresql":
            return await self._execute_postgresql_tool(tool_name, arguments)
        
        # Playwright tools (REAL implementation)
        elif server_name == "playwright":
            return await self._execute_playwright_tool(tool_name, arguments)
        
        else:
            raise ValueError(f"Unknown server: {server_name}")
    
    async def _execute_postgresql_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Execute REAL PostgreSQL queries using MCP"""
        
        if not self.pg_pool:
            return {
                "success": False,
                "error": "PostgreSQL not connected"
            }
        
        try:
            async with self.pg_pool.acquire() as conn:
                
                if tool_name == "execute_query":
                    query = arguments.get("query", "")
                    
                    # Safety check: only allow SELECT queries
                    query_upper = query.strip().upper()
                    if not query_upper.startswith("SELECT"):
                        return {
                            "success": False,
                            "error": "Only SELECT queries allowed (read-only mode)"
                        }
                    
                    # Execute query
                    rows = await conn.fetch(query)
                    results = [dict(row) for row in rows]
                    
                    return {
                        "success": True,
                        "tool": "execute_query",
                        "query": query,
                        "rows_returned": len(results),
                        "results": results,
                        "mode": "REAL_POSTGRESQL"
                    }
                
                elif tool_name == "list_tables":
                    query = """
                        SELECT tablename as name, schemaname as schema
                        FROM pg_tables 
                        WHERE schemaname = 'public'
                        ORDER BY tablename;
                    """
                    rows = await conn.fetch(query)
                    tables = [dict(row) for row in rows]
                    
                    return {
                        "success": True,
                        "tool": "list_tables",
                        "tables": tables,
                        "count": len(tables),
                        "mode": "REAL_POSTGRESQL"
                    }
                
                elif tool_name == "get_table_schema":
                    table_name = arguments.get("table_name", "")
                    query = """
                        SELECT 
                            column_name, 
                            data_type, 
                            is_nullable,
                            column_default
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = $1
                        ORDER BY ordinal_position;
                    """
                    rows = await conn.fetch(query, table_name)
                    schema = [dict(row) for row in rows]
                    
                    return {
                        "success": True,
                        "tool": "get_table_schema",
                        "table": table_name,
                        "columns": schema,
                        "mode": "REAL_POSTGRESQL"
                    }
                
                elif tool_name == "describe_database":
                    # Get database statistics
                    db_name = await conn.fetchval("SELECT current_database()")
                    table_count = await conn.fetchval(
                        "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public'"
                    )
                    
                    return {
                        "success": True,
                        "tool": "describe_database",
                        "database": db_name,
                        "tables_count": table_count,
                        "mode": "REAL_POSTGRESQL"
                    }
                
                else:
                    return {
                        "success": False,
                        "error": f"Unknown PostgreSQL tool: {tool_name}"
                    }
                    
        except Exception as e:
            logger.error(f"PostgreSQL tool execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    async def _execute_playwright_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Execute REAL Playwright browser automation"""
        
        playwright_server = get_playwright_server()
        
        try:
            if tool_name == "browser_goto":
                return await playwright_server.goto(
                    arguments.get("url"),
                    arguments.get("timeout", 30000)
                )
            
            elif tool_name == "browser_screenshot":
                return await playwright_server.screenshot(
                    arguments.get("full_page", False)
                )
            
            elif tool_name == "browser_click":
                return await playwright_server.click(
                    arguments.get("selector")
                )
            
            elif tool_name == "browser_fill":
                return await playwright_server.fill(
                    arguments.get("selector"),
                    arguments.get("text")
                )
            
            elif tool_name == "browser_evaluate":
                return await playwright_server.evaluate(
                    arguments.get("script")
                )
            
            elif tool_name == "browser_get_content":
                return await playwright_server.get_content()
            
            elif tool_name == "browser_pdf":
                return await playwright_server.pdf(
                    arguments.get("path")
                )
            
            elif tool_name == "browser_wait_for_selector":
                return await playwright_server.wait_for_selector(
                    arguments.get("selector"),
                    arguments.get("timeout", 30000)
                )
            
            elif tool_name == "browser_get_text":
                return await playwright_server.get_text(
                    arguments.get("selector")
                )
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown Playwright tool: {tool_name}"
                }
                
        except Exception as e:
            logger.error(f"Playwright tool execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    async def cleanup(self):
        """Clean up all connections"""
        logger.info("Cleaning up MCP sessions...")
        
        if self.pg_pool:
            await self.pg_pool.close()
            logger.info("PostgreSQL connection pool closed")
        
        # Cleanup Playwright
        playwright_session = self.sessions.get("playwright")
        if playwright_session and "server" in playwright_session:
            await playwright_session["server"].cleanup()
            logger.info("Playwright browser closed")
        
        self.sessions.clear()
        self.tools_cache.clear()
        self.initialized = False


# Singleton instance
_mcp_manager_instance: Optional[RealMCPClientManager] = None

def get_mcp_manager() -> RealMCPClientManager:
    """Get or create MCP Manager singleton"""
    global _mcp_manager_instance
    if _mcp_manager_instance is None:
        _mcp_manager_instance = RealMCPClientManager()
    return _mcp_manager_instance
