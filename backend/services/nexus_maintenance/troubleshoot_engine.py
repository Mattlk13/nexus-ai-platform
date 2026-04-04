"""
Nexus Troubleshooting Engine
9-Step systematic troubleshooting framework
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class TroubleshootingStep(str, Enum):
    DEFINE_FAILURE = "define_failure"
    MAP_SYSTEM = "map_system"
    GATHER_DATA = "gather_data"
    REDUCE_SCOPE = "reduce_scope"
    CHANGE_ONE_VARIABLE = "change_one_variable"
    FOLLOW_FAILURE_PATH = "follow_failure_path"
    CHECK_CONFIGURATION = "check_configuration"
    DOCUMENT = "document"
    REVIEW_AND_RESOLVE = "review_and_resolve"


class TroubleshootingSession(BaseModel):
    id: str = str(uuid.uuid4())
    component: str
    issue_description: str
    current_step: TroubleshootingStep = TroubleshootingStep.DEFINE_FAILURE
    started_at: datetime = datetime.now(timezone.utc)
    completed_at: Optional[datetime] = None
    resolved: bool = False
    resolution: Optional[str] = None
    steps_completed: List[Dict] = []
    evidence_gathered: List[Dict] = []
    actions_taken: List[Dict] = []
    root_cause: Optional[str] = None


class TroubleshootingEngine:
    """9-Step troubleshooting framework engine"""
    
    def __init__(self, db):
        self.db = db
        self.step_guides = self._load_step_guides()
    
    def _load_step_guides(self) -> Dict:
        """Load troubleshooting step guides"""
        return {
            TroubleshootingStep.DEFINE_FAILURE: {
                "title": "Define the Failure Precisely",
                "questions": [
                    "What exactly is broken?",
                    "When did it start?",
                    "Who is affected (everyone, specific users, one person)?",
                    "What error messages are shown?",
                    "Can you reproduce the issue?"
                ],
                "guidance": "Be specific. 'It doesn't work' is too vague. 'API returns 500 error on POST /api/data' is precise."
            },
            TroubleshootingStep.MAP_SYSTEM: {
                "title": "Map the System Before Touching Anything",
                "questions": [
                    "What are the dependencies?",
                    "What changed recently?",
                    "What is the normal flow?",
                    "Which components are involved?"
                ],
                "guidance": "Understand the full context. Draw a diagram if needed. Don't skip this!"
            },
            TroubleshootingStep.GATHER_DATA: {
                "title": "Trust Data Over Intuition",
                "questions": [
                    "What do the logs say?",
                    "What metrics are abnormal?",
                    "What does monitoring show?",
                    "Can you see the failure in real-time?"
                ],
                "guidance": "Collect evidence. Don't guess. Check logs, metrics, database queries, network traffic."
            },
            TroubleshootingStep.REDUCE_SCOPE: {
                "title": "Reduce Scope Relentlessly",
                "questions": [
                    "Is it everyone or specific users?",
                    "Is it all features or one specific feature?",
                    "Is it one server or all servers?",
                    "Can you isolate the problem?"
                ],
                "guidance": "Narrow from broad to specific. Binary search through the problem space."
            },
            TroubleshootingStep.CHANGE_ONE_VARIABLE: {
                "title": "Change One Variable at a Time",
                "questions": [
                    "What will you test?",
                    "What do you expect to happen?",
                    "How will you measure the result?",
                    "Can you roll back if it fails?"
                ],
                "guidance": "Treat each change as a controlled experiment. Document before/after state."
            },
            TroubleshootingStep.FOLLOW_FAILURE_PATH: {
                "title": "Follow Failure Directionally",
                "questions": [
                    "Where does the error originate?",
                    "What is the failure chain?",
                    "Which component failed first?",
                    "What triggered the cascade?"
                ],
                "guidance": "Trace the problem from symptom to root cause. Follow the breadcrumbs."
            },
            TroubleshootingStep.CHECK_CONFIGURATION: {
                "title": "Assume System Works as Configured",
                "questions": [
                    "What configuration changed?",
                    "Were any updates applied?",
                    "Are environment variables correct?",
                    "Did someone modify settings?"
                ],
                "guidance": "Question changes, not defaults. Check recent commits, deployments, config changes."
            },
            TroubleshootingStep.DOCUMENT: {
                "title": "Document While You Troubleshoot",
                "questions": [
                    "What have you tried?",
                    "What were the results?",
                    "What evidence did you gather?",
                    "What conclusions have you drawn?"
                ],
                "guidance": "Keep a log. Future you (or your team) will thank you."
            },
            TroubleshootingStep.REVIEW_AND_RESOLVE: {
                "title": "Review, Resolve, and Prevent",
                "questions": [
                    "What was the root cause?",
                    "What fixed it?",
                    "How can we prevent this?",
                    "What should we monitor?"
                ],
                "guidance": "Don't just fix it—understand why it happened and prevent recurrence."
            }
        }
    
    async def start_session(
        self,
        component: str,
        issue_description: str,
        user_id: str
    ) -> Dict:
        """Start a new troubleshooting session"""
        session = TroubleshootingSession(
            component=component,
            issue_description=issue_description
        )
        
        session_dict = session.model_dump()
        session_dict['started_at'] = session_dict['started_at'].isoformat()
        session_dict['user_id'] = user_id
        
        await self.db.troubleshooting_sessions.insert_one(session_dict)
        
        logger.info(f"Troubleshooting session started: {session.id}")
        return session_dict
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get troubleshooting session"""
        return await self.db.troubleshooting_sessions.find_one(
            {"id": session_id},
            {"_id": 0}
        )
    
    async def complete_step(
        self,
        session_id: str,
        step: TroubleshootingStep,
        findings: str,
        evidence: Optional[List[str]] = None
    ) -> Dict:
        """Complete a troubleshooting step"""
        step_data = {
            "step": step,
            "findings": findings,
            "evidence": evidence or [],
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Determine next step
        steps_order = list(TroubleshootingStep)
        current_idx = steps_order.index(step)
        next_step = steps_order[current_idx + 1] if current_idx < len(steps_order) - 1 else None
        
        update = {
            "$push": {"steps_completed": step_data},
            "$set": {"current_step": next_step if next_step else step}
        }
        
        await self.db.troubleshooting_sessions.update_one(
            {"id": session_id},
            update
        )
        
        return await self.get_session(session_id)
    
    async def add_evidence(
        self,
        session_id: str,
        evidence_type: str,
        description: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """Add evidence to session"""
        evidence = {
            "type": evidence_type,
            "description": description,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.troubleshooting_sessions.update_one(
            {"id": session_id},
            {"$push": {"evidence_gathered": evidence}}
        )
        
        return await self.get_session(session_id)
    
    async def log_action(
        self,
        session_id: str,
        action: str,
        expected_result: str,
        actual_result: str
    ) -> Dict:
        """Log an action taken during troubleshooting"""
        action_log = {
            "action": action,
            "expected_result": expected_result,
            "actual_result": actual_result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.troubleshooting_sessions.update_one(
            {"id": session_id},
            {"$push": {"actions_taken": action_log}}
        )
        
        return await self.get_session(session_id)
    
    async def resolve_session(
        self,
        session_id: str,
        root_cause: str,
        resolution: str,
        preventive_measures: Optional[List[str]] = None
    ) -> Dict:
        """Resolve troubleshooting session"""
        update = {
            "resolved": True,
            "root_cause": root_cause,
            "resolution": resolution,
            "preventive_measures": preventive_measures or [],
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.troubleshooting_sessions.update_one(
            {"id": session_id},
            {"$set": update}
        )
        
        # Add to knowledge base
        await self._add_to_knowledge_base(
            session_id,
            root_cause,
            resolution,
            preventive_measures
        )
        
        logger.info(f"Troubleshooting session resolved: {session_id}")
        return await self.get_session(session_id)
    
    async def get_step_guidance(self, step: TroubleshootingStep) -> Dict:
        """Get guidance for a specific step"""
        return self.step_guides.get(step, {})
    
    async def suggest_next_action(
        self,
        component: str,
        symptoms: List[str]
    ) -> List[Dict]:
        """AI-powered suggestions based on component and symptoms"""
        # Check knowledge base for similar issues
        similar_cases = await self.db.troubleshooting_sessions.find(
            {
                "component": component,
                "resolved": True
            },
            {"_id": 0, "root_cause": 1, "resolution": 1, "issue_description": 1}
        ).limit(5).to_list(5)
        
        suggestions = []
        for case in similar_cases:
            suggestions.append({
                "issue": case.get("issue_description"),
                "root_cause": case.get("root_cause"),
                "resolution": case.get("resolution"),
                "relevance": "similar_component"
            })
        
        # Add component-specific diagnostics
        if component == "openclaw_gateway":
            suggestions.append({
                "action": "Check gateway logs",
                "command": "tail -100 /var/log/supervisor/openclaw-gateway.err.log",
                "why": "Gateway errors are usually logged here"
            })
            suggestions.append({
                "action": "Verify gateway is running",
                "command": "curl localhost:8001/api/openclaw/status",
                "why": "Confirms gateway process status"
            })
        elif component == "mongodb":
            suggestions.append({
                "action": "Check MongoDB connection",
                "command": "Check MONGO_URL in .env file",
                "why": "Connection string issues are common"
            })
        
        return suggestions
    
    async def _add_to_knowledge_base(
        self,
        session_id: str,
        root_cause: str,
        resolution: str,
        preventive_measures: Optional[List[str]]
    ):
        """Add resolved issue to knowledge base"""
        session = await self.get_session(session_id)
        if not session:
            return
        
        kb_entry = {
            "id": str(uuid.uuid4()),
            "component": session.get("component"),
            "issue": session.get("issue_description"),
            "root_cause": root_cause,
            "resolution": resolution,
            "preventive_measures": preventive_measures or [],
            "troubleshooting_session_id": session_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "helpful_count": 0,
            "tags": [session.get("component"), "troubleshooting"]
        }
        
        await self.db.knowledge_base.insert_one(kb_entry)
        logger.info(f"Added to knowledge base: {kb_entry['id']}")
