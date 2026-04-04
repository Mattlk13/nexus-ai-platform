"""
Nexus Work Order Management System
Create, assign, track, and resolve maintenance work orders
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class WorkOrderPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class WorkOrderStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class WorkOrderType(str, Enum):
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    INSPECTION = "inspection"
    EMERGENCY = "emergency"


class WorkOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    type: WorkOrderType
    priority: WorkOrderPriority
    status: WorkOrderStatus = WorkOrderStatus.OPEN
    component: str  # Which system component
    assigned_to: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    actual_duration_minutes: Optional[int] = None
    tags: List[str] = []
    attachments: List[str] = []


class WorkOrderManager:
    """Manage maintenance work orders"""
    
    def __init__(self, db):
        self.db = db
    
    async def create_work_order(self, work_order: WorkOrder) -> Dict:
        """Create a new work order"""
        try:
            wo_dict = work_order.model_dump()
            wo_dict['created_at'] = wo_dict['created_at'].isoformat()
            wo_dict['updated_at'] = wo_dict['updated_at'].isoformat()
            
            await self.db.work_orders.insert_one(wo_dict)
            
            # Create activity log
            await self._log_activity(
                work_order.id,
                "created",
                work_order.created_by,
                f"Work order created: {work_order.title}"
            )
            
            logger.info(f"Work order created: {work_order.id} - {work_order.title}")
            return wo_dict
        except Exception as e:
            logger.error(f"Failed to create work order: {e}")
            raise
    
    async def get_work_order(self, work_order_id: str) -> Optional[Dict]:
        """Get work order by ID"""
        return await self.db.work_orders.find_one(
            {"id": work_order_id},
            {"_id": 0}
        )
    
    async def list_work_orders(
        self,
        status: Optional[WorkOrderStatus] = None,
        priority: Optional[WorkOrderPriority] = None,
        assigned_to: Optional[str] = None,
        component: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """List work orders with filters"""
        query = {}
        
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        if assigned_to:
            query["assigned_to"] = assigned_to
        if component:
            query["component"] = component
        
        work_orders = await self.db.work_orders.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return work_orders
    
    async def update_work_order(
        self,
        work_order_id: str,
        user_id: str,
        updates: Dict
    ) -> Dict:
        """Update work order"""
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Handle status transitions
        if "status" in updates:
            if updates["status"] == WorkOrderStatus.IN_PROGRESS and "started_at" not in updates:
                updates["started_at"] = datetime.now(timezone.utc).isoformat()
            elif updates["status"] == WorkOrderStatus.RESOLVED and "resolved_at" not in updates:
                updates["resolved_at"] = datetime.now(timezone.utc).isoformat()
                
                # Calculate actual duration
                wo = await self.get_work_order(work_order_id)
                if wo and wo.get("started_at"):
                    started = datetime.fromisoformat(wo["started_at"])
                    resolved = datetime.fromisoformat(updates["resolved_at"])
                    duration = (resolved - started).total_seconds() / 60
                    updates["actual_duration_minutes"] = int(duration)
        
        result = await self.db.work_orders.update_one(
            {"id": work_order_id},
            {"$set": updates}
        )
        
        if result.modified_count > 0:
            # Log activity
            changes = ", ".join([f"{k}: {v}" for k, v in updates.items() if k != "updated_at"])
            await self._log_activity(
                work_order_id,
                "updated",
                user_id,
                f"Updated: {changes}"
            )
        
        return await self.get_work_order(work_order_id)
    
    async def assign_work_order(
        self,
        work_order_id: str,
        assigned_to: str,
        assigned_by: str
    ) -> Dict:
        """Assign work order to a user"""
        return await self.update_work_order(
            work_order_id,
            assigned_by,
            {"assigned_to": assigned_to}
        )
    
    async def resolve_work_order(
        self,
        work_order_id: str,
        user_id: str,
        resolution: str
    ) -> Dict:
        """Mark work order as resolved"""
        return await self.update_work_order(
            work_order_id,
            user_id,
            {
                "status": WorkOrderStatus.RESOLVED,
                "resolution": resolution
            }
        )
    
    async def get_work_order_stats(self) -> Dict:
        """Get work order statistics"""
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        status_counts = {}
        async for doc in self.db.work_orders.aggregate(pipeline):
            status_counts[doc["_id"]] = doc["count"]
        
        # Get average resolution time
        resolved = await self.db.work_orders.find(
            {"status": WorkOrderStatus.RESOLVED},
            {"actual_duration_minutes": 1, "_id": 0}
        ).to_list(1000)
        
        durations = [r["actual_duration_minutes"] for r in resolved if r.get("actual_duration_minutes")]
        avg_resolution_time = sum(durations) / len(durations) if durations else 0
        
        return {
            "total": sum(status_counts.values()),
            "by_status": status_counts,
            "avg_resolution_time_minutes": round(avg_resolution_time, 2)
        }
    
    async def _log_activity(
        self,
        work_order_id: str,
        action: str,
        user_id: str,
        description: str
    ):
        """Log work order activity"""
        await self.db.work_order_activities.insert_one({
            "work_order_id": work_order_id,
            "action": action,
            "user_id": user_id,
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    async def create_auto_work_order_from_health_check(
        self,
        component: str,
        issue: str,
        priority: WorkOrderPriority = WorkOrderPriority.HIGH
    ) -> Dict:
        """Automatically create work order from health check failure"""
        work_order = WorkOrder(
            title=f"Auto-detected issue: {component}",
            description=f"Health check detected issue with {component}: {issue}",
            type=WorkOrderType.CORRECTIVE,
            priority=priority,
            component=component,
            created_by="system",
            tags=["auto-generated", "health-check"]
        )
        
        return await self.create_work_order(work_order)
