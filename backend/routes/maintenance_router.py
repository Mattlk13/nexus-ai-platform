"""
Nexus Maintenance & O&M API Router
Endpoints for system health, work orders, and troubleshooting
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Get database connection
mongo_url = os.environ['MONGO_URL']
db_client = AsyncIOMotorClient(mongo_url)
db = db_client[os.environ['DB_NAME']]

# Import maintenance modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.nexus_maintenance import (
    HealthMonitor,
    WorkOrderManager,
    WorkOrder,
    WorkOrderPriority,
    WorkOrderStatus,
    WorkOrderType,
    TroubleshootingEngine,
    TroubleshootingStep
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


# Pydantic models for requests
class CreateWorkOrderRequest(BaseModel):
    title: str
    description: str
    type: WorkOrderType
    priority: WorkOrderPriority
    component: str
    estimated_duration_minutes: Optional[int] = None
    tags: List[str] = []


class UpdateWorkOrderRequest(BaseModel):
    status: Optional[WorkOrderStatus] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    priority: Optional[WorkOrderPriority] = None


class StartTroubleshootingRequest(BaseModel):
    component: str
    issue_description: str


class CompleteStepRequest(BaseModel):
    findings: str
    evidence: Optional[List[str]] = None


class AddEvidenceRequest(BaseModel):
    evidence_type: str
    description: str
    data: Optional[Dict] = None


class LogActionRequest(BaseModel):
    action: str
    expected_result: str
    actual_result: str


class ResolveSessionRequest(BaseModel):
    root_cause: str
    resolution: str
    preventive_measures: Optional[List[str]] = None


# Dependency to get user from request (simplified)
async def get_current_user_id() -> str:
    # TODO: Integrate with actual auth system
    # For now, return a default user
    return "system"


# ============== Health Monitoring Endpoints ==============

@router.get("/health")
async def get_system_health():
    """Get comprehensive system health status"""
    monitor = HealthMonitor(db)
    
    try:
        health_report = await monitor.run_full_health_check()
        return health_report
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/history")
async def get_health_history(
    request: Request,
    hours: int = 24,
    component: Optional[str] = None
):
    """Get health check history"""
    monitor = HealthMonitor(db)
    
    try:
        history = await monitor.get_health_history(hours, component)
        return {"history": history}
    except Exception as e:
        logger.error(f"Failed to get health history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/components/{component}")
async def get_component_health( component: str):
    """Get health status of a specific component"""
    monitor = HealthMonitor(db)
    
    try:
        full_report = await monitor.run_full_health_check()
        component_health = next(
            (c for c in full_report["components"] if c["component"] == component),
            None
        )
        
        if not component_health:
            raise HTTPException(status_code=404, detail=f"Component {component} not found")
        
        return component_health
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Component health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Work Order Endpoints ==============

@router.post("/work-orders")
async def create_work_order(
    request: Request,
    work_order_req: CreateWorkOrderRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new work order"""
    wom = WorkOrderManager(db)
    
    try:
        work_order = WorkOrder(
            **work_order_req.model_dump(),
            created_by=user_id
        )
        
        result = await wom.create_work_order(work_order)
        return result
    except Exception as e:
        logger.error(f"Failed to create work order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/work-orders")
async def list_work_orders(
    request: Request,
    status: Optional[WorkOrderStatus] = None,
    priority: Optional[WorkOrderPriority] = None,
    assigned_to: Optional[str] = None,
    component: Optional[str] = None,
    limit: int = 100
):
    """List work orders with filters"""
    wom = WorkOrderManager(db)
    
    try:
        work_orders = await wom.list_work_orders(
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            component=component,
            limit=limit
        )
        return {"work_orders": work_orders}
    except Exception as e:
        logger.error(f"Failed to list work orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/work-orders/{work_order_id}")
async def get_work_order( work_order_id: str):
    """Get work order by ID"""
    wom = WorkOrderManager(db)
    
    work_order = await wom.get_work_order(work_order_id)
    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    return work_order


@router.patch("/work-orders/{work_order_id}")
async def update_work_order(
    request: Request,
    work_order_id: str,
    updates: UpdateWorkOrderRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Update work order"""
    wom = WorkOrderManager(db)
    
    try:
        update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
        result = await wom.update_work_order(work_order_id, user_id, update_dict)
        
        if not result:
            raise HTTPException(status_code=404, detail="Work order not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update work order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/work-orders/{work_order_id}/resolve")
async def resolve_work_order(
    request: Request,
    work_order_id: str,
    resolution: str,
    user_id: str = Depends(get_current_user_id)
):
    """Resolve work order"""
    wom = WorkOrderManager(db)
    
    try:
        result = await wom.resolve_work_order(work_order_id, user_id, resolution)
        return result
    except Exception as e:
        logger.error(f"Failed to resolve work order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/work-orders/stats/summary")
async def get_work_order_stats():
    """Get work order statistics"""
    wom = WorkOrderManager(db)
    
    try:
        stats = await wom.get_work_order_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get work order stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Troubleshooting Endpoints ==============

@router.post("/troubleshooting/start")
async def start_troubleshooting(
    request: Request,
    req: StartTroubleshootingRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Start a new troubleshooting session"""
    engine = TroubleshootingEngine(db)
    
    try:
        session = await engine.start_session(
            req.component,
            req.issue_description,
            user_id
        )
        return session
    except Exception as e:
        logger.error(f"Failed to start troubleshooting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/troubleshooting/{session_id}")
async def get_troubleshooting_session( session_id: str):
    """Get troubleshooting session"""
    engine = TroubleshootingEngine(db)
    
    session = await engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.post("/troubleshooting/{session_id}/step/{step}")
async def complete_troubleshooting_step(
    request: Request,
    session_id: str,
    step: TroubleshootingStep,
    req: CompleteStepRequest
):
    """Complete a troubleshooting step"""
    engine = TroubleshootingEngine(db)
    
    try:
        session = await engine.complete_step(
            session_id,
            step,
            req.findings,
            req.evidence
        )
        return session
    except Exception as e:
        logger.error(f"Failed to complete step: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/troubleshooting/{session_id}/evidence")
async def add_troubleshooting_evidence(
    request: Request,
    session_id: str,
    req: AddEvidenceRequest
):
    """Add evidence to troubleshooting session"""
    engine = TroubleshootingEngine(db)
    
    try:
        session = await engine.add_evidence(
            session_id,
            req.evidence_type,
            req.description,
            req.data
        )
        return session
    except Exception as e:
        logger.error(f"Failed to add evidence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/troubleshooting/{session_id}/action")
async def log_troubleshooting_action(
    request: Request,
    session_id: str,
    req: LogActionRequest
):
    """Log an action taken during troubleshooting"""
    engine = TroubleshootingEngine(db)
    
    try:
        session = await engine.log_action(
            session_id,
            req.action,
            req.expected_result,
            req.actual_result
        )
        return session
    except Exception as e:
        logger.error(f"Failed to log action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/troubleshooting/{session_id}/resolve")
async def resolve_troubleshooting(
    request: Request,
    session_id: str,
    req: ResolveSessionRequest
):
    """Resolve troubleshooting session"""
    engine = TroubleshootingEngine(db)
    
    try:
        session = await engine.resolve_session(
            session_id,
            req.root_cause,
            req.resolution,
            req.preventive_measures
        )
        return session
    except Exception as e:
        logger.error(f"Failed to resolve session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/troubleshooting/guide/{step}")
async def get_step_guidance( step: TroubleshootingStep):
    """Get guidance for a troubleshooting step"""
    engine = TroubleshootingEngine(db)
    
    try:
        guidance = await engine.get_step_guidance(step)
        return guidance
    except Exception as e:
        logger.error(f"Failed to get step guidance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/troubleshooting/suggestions")
async def get_troubleshooting_suggestions(
    request: Request,
    component: str,
    symptoms: List[str] = []
):
    """Get AI-powered troubleshooting suggestions"""
    engine = TroubleshootingEngine(db)
    
    try:
        suggestions = await engine.suggest_next_action(component, symptoms)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Knowledge Base Endpoints ==============

@router.get("/knowledge-base")
async def search_knowledge_base(
    request: Request,
    component: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20
):
    """Search knowledge base"""
    
    try:
        query = {}
        if component:
            query["component"] = component
        if search:
            query["$text"] = {"$search": search}
        
        articles = await db.knowledge_base.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return {"articles": articles}
    except Exception as e:
        logger.error(f"Failed to search knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-base/{article_id}")
async def get_knowledge_base_article( article_id: str):
    """Get knowledge base article"""
    
    article = await db.knowledge_base.find_one(
        {"id": article_id},
        {"_id": 0}
    )
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return article


def get_maintenance_router():
    """Get the maintenance router"""
    return router
