"""
ERNIE API Routes
Primary orchestrator endpoints for emergent.sh agent commands
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

from services.ernie import get_ernie_orchestrator

logger = logging.getLogger(__name__)


class AgentCommand(BaseModel):
    command: str
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None


class MultiAgentWorkflow(BaseModel):
    workflow: str
    steps: List[Dict[str, Any]]


def get_ernie_router():
    """Get ERNIE orchestrator router"""
    router = APIRouter(prefix="/api/ernie", tags=["ernie-orchestrator"])
    
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Get ERNIE orchestrator
    ernie = get_ernie_orchestrator(db)
    
    @router.get("/status")
    async def ernie_status():
        """Get ERNIE orchestrator status"""
        status = await ernie.get_agent_status()
        return {
            "status": "active",
            "orchestrator": "ERNIE - Emergent Runtime Nexus Intelligence Engine",
            "version": "1.0.0",
            **status
        }
    
    @router.post("/command")
    async def execute_agent_command(command_data: AgentCommand):
        """
        Execute an emergent.sh agent command via ERNIE
        
        ERNIE will:
        1. Parse the command
        2. Route to appropriate specialized agent
        3. Coordinate execution
        4. Return synthesized results
        """
        try:
            result = await ernie.execute_command(
                command=command_data.command,
                context=command_data.context,
                user_id=command_data.user_id
            )
            
            if not result.get("success"):
                raise HTTPException(
                    status_code=500,
                    detail=result.get("error", "Command execution failed")
                )
            
            return result
            
        except Exception as e:
            logger.error(f"ERNIE command execution failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/workflow")
    async def execute_multi_agent_workflow(workflow_data: MultiAgentWorkflow):
        """Execute a multi-agent workflow coordinated by ERNIE"""
        try:
            result = await ernie.multi_agent_workflow(
                workflow=workflow_data.workflow,
                steps=workflow_data.steps
            )
            return result
            
        except Exception as e:
            logger.error(f"ERNIE workflow execution failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/agents")
    async def list_registered_agents():
        """List all agents registered with ERNIE"""
        status = await ernie.get_agent_status()
        return {
            "orchestrator": "ERNIE",
            "total_agents": status.get("registered_agents", 0),
            "agents": status.get("agents", [])
        }
    
    @router.post("/agent/register")
    async def register_agent(agent_data: Dict[str, Any]):
        """Register a new agent with ERNIE (for extensibility)"""
        agent_id = agent_data.get("agent_id")
        agent_type = agent_data.get("agent_type")
        
        if not agent_id or not agent_type:
            raise HTTPException(
                status_code=400,
                detail="agent_id and agent_type are required"
            )
        
        # Note: handler would need to be provided separately for dynamic registration
        return {
            "success": True,
            "message": f"Agent '{agent_id}' registration acknowledged",
            "agent_type": agent_type,
            "capabilities": agent_data.get("capabilities", []),
            "note": "Full dynamic registration requires handler implementation"
        }
    
    # Integration with existing Hybrid Agents
    @router.post("/hybrid/{agent_name}")
    async def execute_hybrid_agent(agent_name: str, task_data: Dict[str, Any]):
        """
        Execute a Hybrid AI Agent via ERNIE orchestration
        
        Available agents:
        - code_review
        - db_optimization  
        - cost_optimization
        - security_audit
        - performance_analysis
        - api_design
        - testing_strategy
        - deployment_planning
        """
        command = f"Execute {agent_name} hybrid agent: {task_data.get('task', '')}"
        
        result = await ernie.execute_command(
            command=command,
            context={
                "agent_type": "hybrid",
                "agent_name": agent_name,
                **task_data
            }
        )
        
        return result
    
    # Integration with Creator Platform
    @router.post("/creator/recommend")
    async def creator_recommendations_via_ernie(user_data: Dict[str, Any]):
        """Get AI tool recommendations via ERNIE orchestration"""
        command = "Generate personalized AI tool recommendations"
        
        result = await ernie.execute_command(
            command=command,
            context={
                "agent_type": "creator_platform",
                "action": "recommendations",
                **user_data
            }
        )
        
        return result
    
    # Atoms.dev Integration
    @router.post("/atoms/workflow")
    async def atoms_workflow_via_ernie(workflow_data: Dict[str, Any]):
        """Execute Atoms.dev multi-agent workflow via ERNIE"""
        command = f"Execute Atoms workflow: {workflow_data.get('workflow_type', '')}"
        
        result = await ernie.execute_command(
            command=command,
            context={
                "agent_type": "atoms",
                **workflow_data
            }
        )
        
        return result
    
    # Demo: Example agent command
    @router.get("/demo")
    async def demo_agent_command():
        """Demo ERNIE agent command execution"""
        demo_commands = [
            "Analyze code quality in the creator service",
            "Recommend AI tools for content creation",
            "Execute database optimization workflow",
            "Review API endpoint security"
        ]
        
        results = []
        for cmd in demo_commands[:2]:  # Execute first 2 for demo
            result = await ernie.execute_command(command=cmd)
            results.append({
                "command": cmd,
                "success": result.get("success"),
                "agent_used": result.get("agent_used")
            })
        
        return {
            "demo": "ERNIE Agent Command Execution",
            "examples_executed": results,
            "available_commands": demo_commands
        }
    
    return router
