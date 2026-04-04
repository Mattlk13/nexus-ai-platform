"""
NEXUS Autonomous Agent Orchestrator
Central brain that coordinates all AI agents across the platform
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class AgentPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class AutonomousAgent:
    """
    Base class for all autonomous agents
    """
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.priority = AgentPriority.MEDIUM
        self.created_at = datetime.now(timezone.utc)
        self.last_run = None
        self.run_count = 0
        self.success_count = 0
        self.error_count = 0
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task - to be overridden by specific agents
        """
        raise NotImplementedError("Agent must implement execute method")
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run agent with error handling and metrics
        """
        self.status = AgentStatus.RUNNING
        self.last_run = datetime.now(timezone.utc)
        self.run_count += 1
        
        try:
            result = await self.execute(context)
            self.success_count += 1
            self.status = AgentStatus.IDLE
            return {
                "success": True,
                "agent_id": self.agent_id,
                "result": result,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            self.error_count += 1
            self.status = AgentStatus.ERROR
            logger.error(f"Agent {self.name} failed: {e}")
            return {
                "success": False,
                "agent_id": self.agent_id,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


class AgentOrchestrator:
    """
    Central orchestrator that manages all autonomous agents
    """
    def __init__(self):
        self.agents: Dict[str, AutonomousAgent] = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.running = False
        self.execution_log: List[Dict[str, Any]] = []
    
    def register_agent(self, agent: AutonomousAgent):
        """
        Register a new agent with the orchestrator
        """
        self.agents[agent.agent_id] = agent
        logger.info(f"Agent registered: {agent.name} ({agent.agent_id})")
    
    def unregister_agent(self, agent_id: str):
        """
        Remove an agent from orchestrator
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Agent unregistered: {agent_id}")
    
    async def schedule_task(self, agent_id: str, context: Dict[str, Any], priority: AgentPriority = AgentPriority.MEDIUM):
        """
        Schedule a task for an agent
        """
        task = {
            "task_id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "context": context,
            "priority": priority,
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending"
        }
        
        # Insert by priority
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda x: x["priority"].value)
        
        logger.info(f"Task scheduled: {task['task_id']} for agent {agent_id}")
        return task["task_id"]
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single task
        """
        agent_id = task["agent_id"]
        
        if agent_id not in self.agents:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found"
            }
        
        agent = self.agents[agent_id]
        task["status"] = "running"
        task["started_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await agent.run(task["context"])
        
        task["status"] = "completed" if result["success"] else "failed"
        task["completed_at"] = datetime.now(timezone.utc).isoformat()
        task["result"] = result
        
        # Log execution
        self.execution_log.append(task)
        
        return result
    
    async def run_orchestrator(self):
        """
        Main orchestrator loop - processes task queue
        """
        self.running = True
        logger.info("Agent Orchestrator started")
        
        while self.running:
            if self.task_queue:
                task = self.task_queue.pop(0)
                logger.info(f"Executing task: {task['task_id']}")
                await self.execute_task(task)
            else:
                await asyncio.sleep(1)  # Wait for new tasks
    
    def stop_orchestrator(self):
        """
        Stop the orchestrator
        """
        self.running = False
        logger.info("Agent Orchestrator stopped")
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific agent
        """
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "description": agent.description,
            "status": agent.status.value,
            "priority": agent.priority.value,
            "run_count": agent.run_count,
            "success_count": agent.success_count,
            "error_count": agent.error_count,
            "last_run": agent.last_run.isoformat() if agent.last_run else None,
            "created_at": agent.created_at.isoformat()
        }
    
    def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all agents
        """
        return [self.get_agent_status(agent_id) for agent_id in self.agents.keys()]
    
    def get_execution_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent execution log
        """
        return self.execution_log[-limit:]


# Global orchestrator instance
orchestrator = AgentOrchestrator()
