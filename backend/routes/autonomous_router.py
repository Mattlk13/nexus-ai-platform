"""
Autonomous Agents API Router
Manage and monitor all autonomous AI agents
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from services.autonomous.orchestrator import orchestrator, AgentPriority
from services.autonomous.agents import initialize_default_agents
from services.autonomous.hybrid_agents import initialize_hybrid_agents

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/autonomous", tags=["autonomous-agents"])

# Initialize agents on startup
agents_initialized = False


class TaskRequest(BaseModel):
    agent_id: str
    context: Dict[str, Any]
    priority: Optional[str] = "medium"


class AgentControl(BaseModel):
    action: str  # start, stop, pause, resume


# Hybrid Agent specific request models
class CodeReviewRequest(BaseModel):
    code: str
    language: Optional[str] = "python"
    pr_description: Optional[str] = ""


class DatabaseOptimizationRequest(BaseModel):
    query: str
    database_type: Optional[str] = "postgresql"
    schema: Optional[str] = ""


class CostOptimizationRequest(BaseModel):
    platform: Optional[str] = "aws"
    current_cost: float
    resources: Optional[list] = []


class UserSupportRequest(BaseModel):
    query: str
    user_context: Optional[Dict[str, Any]] = {}
    conversation_history: Optional[list] = []


class GrowthHackingRequest(BaseModel):
    product: str
    target_audience: str
    current_metrics: Optional[Dict[str, Any]] = {}
    goals: Optional[str] = "increase user acquisition"


class BugDetectionRequest(BaseModel):
    code: str
    language: Optional[str] = "python"
    context: Optional[str] = ""


class DocumentationRequest(BaseModel):
    code: Optional[str] = ""
    api_spec: Optional[str] = ""
    doc_type: Optional[str] = "readme"
    style: Optional[str] = "clear and professional"


class TestGenerationRequest(BaseModel):
    code: str
    language: Optional[str] = "python"
    test_framework: Optional[str] = "pytest"
    test_type: Optional[str] = "unit"


# ============== Agent Management ==============

@router.post("/initialize")
async def initialize_agents():
    """
    Initialize all autonomous agents (standard + hybrid AI agents)
    """
    global agents_initialized
    
    if agents_initialized:
        return {
            "success": True,
            "message": "Agents already initialized"
        }
    
    try:
        # Initialize standard agents
        standard_agents = initialize_default_agents()
        # Initialize hybrid AI agents
        hybrid_agents = initialize_hybrid_agents()
        
        total_agents = standard_agents + hybrid_agents
        agents_initialized = True
        
        return {
            "success": True,
            "message": f"Initialized {len(total_agents)} autonomous agents",
            "standard_agents": [agent.name for agent in standard_agents],
            "hybrid_agents": [agent.name for agent in hybrid_agents]
        }
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agents():
    """
    List all registered autonomous agents
    """
    agents = orchestrator.get_all_agents_status()
    return {
        "success": True,
        "total_agents": len(agents),
        "agents": agents
    }


@router.get("/agents/{agent_id}")
async def get_agent_status(agent_id: str):
    """
    Get detailed status of a specific agent
    """
    status = orchestrator.get_agent_status(agent_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "success": True,
        "agent": status
    }


@router.post("/agents/{agent_id}/control")
async def control_agent(agent_id: str, control: AgentControl):
    """
    Control an agent (start, stop, pause, resume)
    """
    agent = orchestrator.agents.get(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    action = control.action.lower()
    
    if action == "pause":
        agent.status = "paused"
    elif action == "resume":
        agent.status = "idle"
    else:
        return {"success": False, "error": "Invalid action"}
    
    return {
        "success": True,
        "agent_id": agent_id,
        "action": action,
        "new_status": agent.status
    }


# ============== Task Management ==============

@router.post("/tasks")
async def schedule_task(task: TaskRequest):
    """
    Schedule a task for an agent
    """
    # Convert priority string to enum
    priority_map = {
        "critical": AgentPriority.CRITICAL,
        "high": AgentPriority.HIGH,
        "medium": AgentPriority.MEDIUM,
        "low": AgentPriority.LOW
    }
    
    priority = priority_map.get(task.priority.lower(), AgentPriority.MEDIUM)
    
    try:
        task_id = await orchestrator.schedule_task(
            agent_id=task.agent_id,
            context=task.context,
            priority=priority
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "agent_id": task.agent_id,
            "status": "scheduled"
        }
    except Exception as e:
        logger.error(f"Failed to schedule task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks")
async def get_task_queue():
    """
    Get current task queue
    """
    return {
        "success": True,
        "queue_size": len(orchestrator.task_queue),
        "tasks": orchestrator.task_queue
    }


@router.get("/execution-log")
async def get_execution_log(limit: int = 100):
    """
    Get recent agent execution log
    """
    log = orchestrator.get_execution_log(limit=limit)
    return {
        "success": True,
        "total_executions": len(log),
        "log": log
    }


# ============== Quick Actions ==============

@router.post("/actions/health-check")
async def run_health_check():
    """
    Run system health check agent immediately
    """
    task_id = await orchestrator.schedule_task(
        agent_id="system-health",
        context={},
        priority=AgentPriority.CRITICAL
    )
    
    return {
        "success": True,
        "task_id": task_id,
        "message": "Health check scheduled"
    }


@router.post("/actions/market-research")
async def run_market_research(topic: str = "creator economy"):
    """
    Run market research agent
    """
    task_id = await orchestrator.schedule_task(
        agent_id="market-research",
        context={"topic": topic},
        priority=AgentPriority.HIGH
    )
    
    return {
        "success": True,
        "task_id": task_id,
        "message": f"Market research scheduled for: {topic}"
    }


@router.post("/actions/discover-integrations")
async def discover_integrations(query: str = "creator tools"):
    """
    Run integration discovery agent
    """
    task_id = await orchestrator.schedule_task(
        agent_id="integration-discovery",
        context={"query": query},
        priority=AgentPriority.MEDIUM
    )
    
    return {
        "success": True,
        "task_id": task_id,
        "message": f"Integration discovery scheduled for: {query}"
    }


# ============== Orchestrator Control ==============

@router.post("/orchestrator/start")
async def start_orchestrator(background_tasks: BackgroundTasks):
    """
    Start the agent orchestrator
    """
    if orchestrator.running:
        return {
            "success": False,
            "message": "Orchestrator already running"
        }
    
    background_tasks.add_task(orchestrator.run_orchestrator)
    
    return {
        "success": True,
        "message": "Orchestrator started"
    }


@router.post("/orchestrator/stop")
async def stop_orchestrator():
    """
    Stop the agent orchestrator
    """


# ============== HYBRID AI AGENT ENDPOINTS ==============

@router.post("/hybrid/code-review")
async def code_review(request: CodeReviewRequest):
    """
    AI-powered code review
    
    Automatically reviews code and provides:
    - Security issues
    - Performance problems
    - Code quality concerns
    - Bug detection
    - Improvement suggestions
    """
    try:
        task_id = await orchestrator.schedule_task(
            agent_id="code-review",
            context={
                "code": request.code,
                "language": request.language,
                "pr_description": request.pr_description
            },
            priority=AgentPriority.HIGH
        )
        
        # Execute immediately and wait for result
        task = next((t for t in orchestrator.task_queue if t["task_id"] == task_id), None)
        if task:
            result = await orchestrator.execute_task(task)
            return result
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "Code review scheduled"
        }
    except Exception as e:
        logger.error(f"Code review failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid/database-optimization")
async def database_optimization(request: DatabaseOptimizationRequest):
    """
    AI-powered database query optimization
    
    Analyzes SQL queries and provides:
    - Performance analysis
    - Optimized query versions
    - Index recommendations
    - Execution plan insights
    """
    try:
        task_id = await orchestrator.schedule_task(
            agent_id="database-optimization",
            context={
                "query": request.query,
                "database_type": request.database_type,
                "schema": request.schema
            },
            priority=AgentPriority.HIGH
        )
        
        # Execute immediately
        task = next((t for t in orchestrator.task_queue if t["task_id"] == task_id), None)
        if task:
            result = await orchestrator.execute_task(task)
            return result
        
        return {"success": True, "task_id": task_id}
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid/cost-optimization")
async def cost_optimization(request: CostOptimizationRequest):
    """
    AI-powered cloud cost optimization
    
    Analyzes infrastructure costs and provides:
    - Cost breakdown analysis
    - Optimization opportunities
    - Right-sizing recommendations
    - Estimated savings
    """
    try:
        task_id = await orchestrator.schedule_task(
            agent_id="cost-optimization",
            context={
                "platform": request.platform,
                "current_cost": request.current_cost,
                "resources": request.resources
            },
            priority=AgentPriority.MEDIUM
        )
        
        task = next((t for t in orchestrator.task_queue if t["task_id"] == task_id), None)
        if task:
            result = await orchestrator.execute_task(task)
            return result
        
        return {"success": True, "task_id": task_id}
    except Exception as e:
        logger.error(f"Cost optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid/user-support")
async def user_support(request: UserSupportRequest):
    """
    AI-powered customer support
    
    Provides intelligent support responses:
    - Answer user questions
    - Troubleshoot issues
    - Guide through features
    - Escalate when needed
    """
    try:
        task_id = await orchestrator.schedule_task(
            agent_id="user-support",
            context={
                "query": request.query,
                "user_context": request.user_context,
                "conversation_history": request.conversation_history
            },
            priority=AgentPriority.HIGH
        )
        
        task = next((t for t in orchestrator.task_queue if t["task_id"] == task_id), None)
        if task:
            result = await orchestrator.execute_task(task)
            return result
        
        return {"success": True, "task_id": task_id}
    except Exception as e:
        logger.error(f"User support failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid/growth-hacking")
async def growth_hacking(request: GrowthHackingRequest):
    """
    AI-powered growth hacking strategies
    
    Generates viral marketing strategies:
    - Growth tactics
    - Viral content ideas
    - Channel strategies
    - A/B test recommendations
    """
    try:
        task_id = await orchestrator.schedule_task(
            agent_id="growth-hacking",
            context={
                "product": request.product,
                "target_audience": request.target_audience,
                "current_metrics": request.current_metrics,
                "goals": request.goals
            },
            priority=AgentPriority.MEDIUM
        )
        
        task = next((t for t in orchestrator.task_queue if t["task_id"] == task_id), None)
        if task:
            result = await orchestrator.execute_task(task)
            return result
        
        return {"success": True, "task_id": task_id}
    except Exception as e:
        logger.error(f"Growth hacking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid/bug-detection")
async def bug_detection(request: BugDetectionRequest):
    """
    AI-powered bug detection
    
    Automatically finds bugs:
    - Critical bugs
    - Security vulnerabilities
    - Logic errors
    - Memory issues
    - Race conditions
    """
    try:
        task_id = await orchestrator.schedule_task(
            agent_id="bug-detection",
            context={
                "code": request.code,
                "language": request.language,
                "context": request.context
            },
            priority=AgentPriority.CRITICAL
        )
        
        task = next((t for t in orchestrator.task_queue if t["task_id"] == task_id), None)
        if task:
            result = await orchestrator.execute_task(task)
            return result
        
        return {"success": True, "task_id": task_id}
    except Exception as e:
        logger.error(f"Bug detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid/documentation")
async def documentation_generation(request: DocumentationRequest):
    """
    AI-powered documentation generation
    
    Automatically generates docs:
    - README files
    - API documentation
    - Function/class docs
    - Usage examples
    """
    try:
        task_id = await orchestrator.schedule_task(
            agent_id="documentation",
            context={
                "code": request.code,
                "api_spec": request.api_spec,
                "doc_type": request.doc_type,
                "style": request.style
            },
            priority=AgentPriority.MEDIUM
        )
        
        task = next((t for t in orchestrator.task_queue if t["task_id"] == task_id), None)
        if task:
            result = await orchestrator.execute_task(task)
            return result
        
        return {"success": True, "task_id": task_id}
    except Exception as e:
        logger.error(f"Documentation generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hybrid/testing")
async def test_generation(request: TestGenerationRequest):
    """
    AI-powered test generation
    
    Automatically writes tests:
    - Unit tests
    - Integration tests
    - Edge cases
    - Mock data
    """
    try:
        task_id = await orchestrator.schedule_task(
            agent_id="testing",
            context={
                "code": request.code,
                "language": request.language,
                "test_framework": request.test_framework,
                "test_type": request.test_type
            },
            priority=AgentPriority.HIGH
        )
        
        task = next((t for t in orchestrator.task_queue if t["task_id"] == task_id), None)
        if task:
            result = await orchestrator.execute_task(task)
            return result
        
        return {"success": True, "task_id": task_id}
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hybrid/agents")
async def list_hybrid_agents():
    """
    List all hybrid AI agents
    """
    hybrid_agent_ids = [
        "code-review",
        "database-optimization",
        "cost-optimization",
        "user-support",
        "growth-hacking",
        "bug-detection",
        "documentation",
        "testing"
    ]
    
    hybrid_agents = [
        orchestrator.get_agent_status(agent_id) 
        for agent_id in hybrid_agent_ids 
        if agent_id in orchestrator.agents
    ]
    
    return {
        "success": True,
        "total_hybrid_agents": len(hybrid_agents),
        "agents": hybrid_agents
    }

    orchestrator.stop_orchestrator()
    
    return {
        "success": True,
        "message": "Orchestrator stopped"
    }


@router.get("/orchestrator/status")
async def get_orchestrator_status():
    """
    Get orchestrator status
    """
    return {
        "success": True,
        "running": orchestrator.running,
        "total_agents": len(orchestrator.agents),
        "queue_size": len(orchestrator.task_queue),
        "total_executions": len(orchestrator.execution_log)
    }


# ============== Dashboard Stats ==============

@router.get("/dashboard")
async def get_autonomous_dashboard():
    """
    Get comprehensive autonomous system dashboard
    """
    agents = orchestrator.get_all_agents_status()
    
    # Calculate stats
    total_runs = sum(a["run_count"] for a in agents)
    total_successes = sum(a["success_count"] for a in agents)
    total_errors = sum(a["error_count"] for a in agents)
    
    success_rate = (total_successes / total_runs * 100) if total_runs > 0 else 0
    
    return {
        "success": True,
        "orchestrator": {
            "running": orchestrator.running,
            "queue_size": len(orchestrator.task_queue)
        },
        "agents": {
            "total": len(agents),
            "active": len([a for a in agents if a["status"] == "running"]),
            "idle": len([a for a in agents if a["status"] == "idle"]),
            "error": len([a for a in agents if a["status"] == "error"])
        },
        "performance": {
            "total_runs": total_runs,
            "total_successes": total_successes,
            "total_errors": total_errors,
            "success_rate": round(success_rate, 2)
        },
        "agent_list": agents
    }


def get_autonomous_router():
    """Get the autonomous agents router"""
    return router
