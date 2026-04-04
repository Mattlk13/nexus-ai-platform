"""
MCP Inspector Integration for NEXUS
Provides visual testing and debugging for MCP servers
"""
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MCPInspector:
    """
    MCP Inspector wrapper for debugging MCP servers
    """
    
    def __init__(self):
        self.inspector_available = self._check_inspector()
        logger.info(f"MCP Inspector available: {self.inspector_available}")
    
    def _check_inspector(self) -> bool:
        """Check if MCP Inspector is installed"""
        try:
            result = subprocess.run(
                ["which", "mcp-inspector"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Inspector check failed: {e}")
            return False
    
    def inspect_server(self, server_command: str, server_args: list = None) -> Dict[str, Any]:
        """
        Inspect an MCP server using the inspector tool
        
        Args:
            server_command: Command to start the MCP server
            server_args: Arguments for the server
            
        Returns:
            Inspection results
        """
        if not self.inspector_available:
            return {
                "success": False,
                "error": "MCP Inspector not installed"
            }
        
        try:
            # Build command
            cmd = ["mcp-inspector", server_command]
            if server_args:
                cmd.extend(server_args)
            
            # Run inspector (non-blocking for web UI)
            result = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return {
                "success": True,
                "message": "Inspector started",
                "pid": result.pid,
                "note": "Inspector UI available at http://localhost:5173"
            }
            
        except Exception as e:
            logger.error(f"Inspector failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get information about installed MCP servers"""
        return {
            "inspector_available": self.inspector_available,
            "inspector_version": "latest",
            "inspector_ui": "http://localhost:5173",
            "supported_transports": ["stdio", "http"],
            "features": [
                "Visual testing",
                "Tool exploration",
                "Resource inspection",
                "Prompt testing"
            ]
        }


# Singleton
_inspector = None

def get_inspector() -> MCPInspector:
    """Get MCP Inspector singleton"""
    global _inspector
    if _inspector is None:
        _inspector = MCPInspector()
    return _inspector
