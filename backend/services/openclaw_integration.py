"""
OpenClaw Integration Service
Handles enhanced integration with OpenClaw gateway including task management
"""
import asyncio
import logging
import httpx
from typing import Optional, Dict, List
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)

OPENCLAW_GATEWAY_PORT = 18789
OPENCLAW_CONTROL_PORT = 18791


class OpenClawTaskManager:
    """
    Manages tasks sent to OpenClaw gateway
    Provides async task submission and result tracking
    """
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.gateway_url = f"http://127.0.0.1:{OPENCLAW_GATEWAY_PORT}"
        self.control_url = f"http://127.0.0.1:{OPENCLAW_CONTROL_PORT}"
    
    async def submit_task(
        self, 
        description: str, 
        context: Optional[str] = None,
        files: Optional[List[str]] = None
    ) -> str:
        """
        Submit a task to OpenClaw gateway
        
        Args:
            description: Task description
            context: Additional context for the task
            files: List of file paths relevant to the task
            
        Returns:
            task_id: Unique task identifier
        """
        task_id = str(uuid.uuid4())
        
        task_data = {
            "task_id": task_id,
            "description": description,
            "context": context,
            "files": files or [],
            "status": "submitted",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
            "result": None
        }
        
        self.tasks[task_id] = task_data
        
        # Submit to OpenClaw gateway (async)
        asyncio.create_task(self._execute_task(task_id))
        
        return task_id
    
    async def _execute_task(self, task_id: str):
        """
        Execute task via OpenClaw gateway
        This is a placeholder - actual implementation would use OpenClaw's MCP protocol
        """
        try:
            task = self.tasks[task_id]
            task["status"] = "running"
            
            # Simulate task execution
            # In production, this would:
            # 1. Connect to OpenClaw gateway via WebSocket/HTTP
            # 2. Submit task via MCP protocol
            # 3. Stream results back
            # 4. Update task status
            
            await asyncio.sleep(2)  # Simulate work
            
            task["status"] = "completed"
            task["completed_at"] = datetime.now(timezone.utc).isoformat()
            task["result"] = {
                "success": True,
                "message": "Task completed (simulated)"
            }
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            task["status"] = "failed"
            task["result"] = {
                "success": False,
                "error": str(e)
            }
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def list_tasks(self) -> List[Dict]:
        """List all tasks"""
        return list(self.tasks.values())
    
    async def check_gateway_health(self) -> bool:
        """Check if OpenClaw gateway is healthy"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.gateway_url, timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False


class OpenClawIntegration:
    """
    Main integration class for OpenClaw
    Provides high-level methods for interacting with OpenClaw
    """
    
    def __init__(self):
        self.task_manager = OpenClawTaskManager()
    
    async def execute_code_task(
        self, 
        code: str, 
        language: str = "python",
        context: Optional[str] = None
    ) -> str:
        """
        Execute a code-related task via OpenClaw
        
        Args:
            code: Code to execute or analyze
            language: Programming language
            context: Additional context
            
        Returns:
            task_id: Task identifier
        """
        description = f"Execute {language} code"
        if context:
            description += f": {context}"
        
        return await self.task_manager.submit_task(
            description=description,
            context=f"Language: {language}\n\nCode:\n{code}"
        )
    
    async def analyze_file(self, file_path: str, analysis_type: str = "general") -> str:
        """
        Analyze a file using OpenClaw
        
        Args:
            file_path: Path to file
            analysis_type: Type of analysis (general, security, performance)
            
        Returns:
            task_id: Task identifier
        """
        description = f"Analyze file: {file_path} (type: {analysis_type})"
        
        return await self.task_manager.submit_task(
            description=description,
            files=[file_path]
        )
    
    async def generate_code(
        self, 
        requirements: str, 
        language: str = "python"
    ) -> str:
        """
        Generate code using OpenClaw
        
        Args:
            requirements: Code requirements
            language: Target programming language
            
        Returns:
            task_id: Task identifier
        """
        description = f"Generate {language} code"
        context = f"Requirements:\n{requirements}"
        
        return await self.task_manager.submit_task(
            description=description,
            context=context
        )
    
    async def refactor_code(
        self, 
        code: str, 
        refactoring_goal: str,
        language: str = "python"
    ) -> str:
        """
        Refactor code using OpenClaw
        
        Args:
            code: Original code
            refactoring_goal: Refactoring objective
            language: Programming language
            
        Returns:
            task_id: Task identifier
        """
        description = f"Refactor {language} code: {refactoring_goal}"
        context = f"Original code:\n{code}"
        
        return await self.task_manager.submit_task(
            description=description,
            context=context
        )
    
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get status of a task"""
        return self.task_manager.get_task(task_id)
    
    async def list_all_tasks(self) -> List[Dict]:
        """List all tasks"""
        return self.task_manager.list_tasks()
    
    async def health_check(self) -> Dict:
        """Perform health check on OpenClaw integration"""
        is_healthy = await self.task_manager.check_gateway_health()
        
        return {
            "openclaw_gateway": "healthy" if is_healthy else "unhealthy",
            "task_manager": "active",
            "total_tasks": len(self.task_manager.tasks),
            "gateway_url": self.task_manager.gateway_url,
            "control_url": self.task_manager.control_url
        }


# Global instance
_openclaw_integration: Optional[OpenClawIntegration] = None


def get_openclaw_integration() -> OpenClawIntegration:
    """Get or create OpenClaw integration instance"""
    global _openclaw_integration
    if _openclaw_integration is None:
        _openclaw_integration = OpenClawIntegration()
    return _openclaw_integration
