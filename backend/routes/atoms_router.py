"""
Atoms.dev Integration API Router
Endpoints for multi-agent AI workflows
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from services.atoms_integration import atoms_agents, RaceMode

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/atoms", tags=["atoms-integration"])


class AgentTaskRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None


class WorkflowRequest(BaseModel):
    project: str
    context: Optional[Dict[str, Any]] = None


class RaceModeRequest(BaseModel):
    prompt: str
    model_count: Optional[int] = 3


@router.get("/agents")
async def list_agents():
    """List all available Atoms agents"""
    return {
        "success": True,
        "agents": [
            {
                "id": "iris",
                "name": "Iris",
                "role": "Deep Researcher",
                "description": "Finds real demand and niches with deep research",
                "capabilities": ["market_research", "opportunity_identification", "competitive_analysis"]
            },
            {
                "id": "emma",
                "name": "Emma",
                "role": "Product Manager",
                "description": "Turns ideas into clear specs and scope",
                "capabilities": ["product_specs", "feature_prioritization", "user_stories", "scope_definition"]
            },
            {
                "id": "bob",
                "name": "Bob",
                "role": "Systems Architect",
                "description": "Designs system blueprints for scalability",
                "capabilities": ["architecture_design", "tech_stack", "data_modeling", "api_design"]
            },
            {
                "id": "sarah",
                "name": "Sarah",
                "role": "SEO Specialist",
                "description": "Launches SEO pages and automates optimizations",
                "capabilities": ["keyword_strategy", "on_page_seo", "technical_seo", "content_strategy"]
            },
            {
                "id": "david",
                "name": "David",
                "role": "Data Analyst",
                "description": "Analyzes data to spot opportunities",
                "capabilities": ["data_analysis", "trend_identification", "insights", "visualization"]
            },
            {
                "id": "mike",
                "name": "Mike",
                "role": "Team Leader",
                "description": "Coordinates all agents end-to-end",
                "capabilities": ["workflow_orchestration", "multi_agent_coordination", "project_management"]
            }
        ]
    }


@router.post("/agents/iris")
async def run_iris_research(request: AgentTaskRequest):
    """
    Run Iris - Deep Research Agent
    Performs market research and identifies opportunities
    """
    try:
        result = await atoms_agents["iris"].execute(request.task, request.context)
        return result
    except Exception as e:
        logger.error(f"Iris agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/emma")
async def run_emma_pm(request: AgentTaskRequest):
    """
    Run Emma - Product Manager Agent
    Creates product specifications and scope
    """
    try:
        result = await atoms_agents["emma"].execute(request.task, request.context)
        return result
    except Exception as e:
        logger.error(f"Emma agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/bob")
async def run_bob_architect(request: AgentTaskRequest):
    """
    Run Bob - Systems Architect Agent
    Designs system architecture and tech stack
    """
    try:
        result = await atoms_agents["bob"].execute(request.task, request.context)
        return result
    except Exception as e:
        logger.error(f"Bob agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/sarah")
async def run_sarah_seo(request: AgentTaskRequest):
    """
    Run Sarah - SEO Specialist Agent
    Generates SEO strategy and optimizations
    """
    try:
        result = await atoms_agents["sarah"].execute(request.task, request.context)
        return result
    except Exception as e:
        logger.error(f"Sarah agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/david")
async def run_david_analyst(request: AgentTaskRequest):
    """
    Run David - Data Analyst Agent
    Performs data analysis and surfaces insights
    """
    try:
        result = await atoms_agents["david"].execute(request.task, request.context)
        return result
    except Exception as e:
        logger.error(f"David agent failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow")
async def run_full_workflow(request: WorkflowRequest):
    """
    Run Mike - Full Multi-Agent Workflow
    Coordinates all agents: Iris → Emma → Bob → Sarah → David
    """
    try:
        result = await atoms_agents["mike"].execute(request.project, request.context)
        return result
    except Exception as e:
        logger.error(f"Mike workflow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/race-mode")
async def run_race_mode(request: RaceModeRequest):
    """
    Run Race Mode - Generate multiple solutions in parallel
    Returns multiple solutions for comparison
    """
    try:
        result = await RaceMode.race(request.prompt, count=request.model_count)
        return result
    except Exception as e:
        logger.error(f"Race mode failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_atoms_router():
    """Get the Atoms integration router"""
    return router
