"""
ERNIE - Emergent Runtime Nexus Intelligence Engine
Primary AI Agent Orchestrator for emergent.sh agent commands

ERNIE coordinates and executes all AI agent operations across the NEXUS platform:
- Hybrid AI Agents (Code Review, DB Optimization, etc.)
- Hybrid Integrations (Grok, Qwen, GPT-Codex, Nano Banana, etc.)
- Atoms.dev Integration (Multi-agent workflows)
- Creator Platform Agents (Recommendations, Analytics)
- OpenClaw Gateway Integration
"""
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from uuid import uuid4
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY", "sk-emergent-a79Ba891bC89777B1C")


class ERNIEOrchestrator:
    """
    ERNIE - Primary AI Agent Orchestrator
    
    Responsibilities:
    1. Route agent commands to appropriate specialized agents
    2. Coordinate multi-agent workflows
    3. Manage agent state and context
    4. Aggregate and synthesize agent responses
    5. Provide unified interface for emergent.sh commands
    """
    
    def __init__(self, db=None):
        self.db = db
        self.session_id = str(uuid4())
        self.agent_registry = {}
        self.active_sessions = {}
        
        # Initialize LLM for orchestration
        self.llm = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=self.session_id,
            system_message=(
                "You are ERNIE, the Emergent Runtime Nexus Intelligence Engine. "
                "You are the primary AI orchestrator coordinating all agent operations. "
                "You route commands to specialized agents, synthesize their responses, "
                "and provide clear, actionable outputs to users."
            )
        ).with_model("openai", "gpt-5.1")
        
        logger.info(f"ERNIE Orchestrator initialized (session: {self.session_id})")
    
    def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        capabilities: List[str],
        handler: callable
    ):
        """Register a specialized agent with ERNIE"""
        self.agent_registry[agent_id] = {
            "type": agent_type,
            "capabilities": capabilities,
            "handler": handler,
            "registered_at": datetime.now(timezone.utc).isoformat()
        }
        logger.info(f"ERNIE: Registered agent '{agent_id}' ({agent_type})")
    
    async def execute_command(
        self,
        command: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute an emergent.sh agent command
        
        Args:
            command: The agent command to execute
            context: Additional context for the command
            user_id: User executing the command
            
        Returns:
            Dict with execution results
        """
        execution_id = str(uuid4())
        start_time = datetime.now(timezone.utc)
        
        logger.info(f"ERNIE: Executing command '{command}' (ID: {execution_id})")
        
        try:
            # Parse command and determine routing
            route_decision = await self._route_command(command, context)
            
            # Execute via appropriate agent(s)
            result = await self._execute_routed_command(
                route_decision,
                command,
                context,
                user_id
            )
            
            # Synthesize and return response
            return {
                "success": True,
                "execution_id": execution_id,
                "command": command,
                "orchestrator": "ERNIE",
                "agent_used": route_decision.get("agent_id"),
                "result": result,
                "execution_time": (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"ERNIE: Command execution failed: {e}")
            return {
                "success": False,
                "execution_id": execution_id,
                "command": command,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _route_command(
        self,
        command: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Determine which agent should handle the command"""
        
        # Command routing logic
        command_lower = command.lower()
        
        # Code review commands
        if any(kw in command_lower for kw in ['review', 'code quality', 'analyze code']):
            return {
                "agent_id": "code_review_agent",
                "agent_type": "hybrid",
                "reasoning": "Code review request detected"
            }
        
        # Database optimization
        if any(kw in command_lower for kw in ['database', 'optimize db', 'query performance']):
            return {
                "agent_id": "db_optimization_agent",
                "agent_type": "hybrid",
                "reasoning": "Database optimization request detected"
            }
        
        # Creator platform commands
        if any(kw in command_lower for kw in ['creator', 'portfolio', 'marketplace']):
            return {
                "agent_id": "creator_agent",
                "agent_type": "creator_platform",
                "reasoning": "Creator platform request detected"
            }
        
        # AI recommendations
        if any(kw in command_lower for kw in ['recommend', 'suggest tools', 'personalized']):
            return {
                "agent_id": "recommendation_agent",
                "agent_type": "creator_platform",
                "reasoning": "Recommendation request detected"
            }
        
        # Atoms.dev multi-agent workflows
        if any(kw in command_lower for kw in ['workflow', 'multi-agent', 'atoms']):
            return {
                "agent_id": "atoms_orchestrator",
                "agent_type": "atoms",
                "reasoning": "Multi-agent workflow detected"
            }
        
        # Hybrid Integrations - Code Generation
        if any(kw in command_lower for kw in ['generate code', 'write code', 'codex', 'programming']):
            return {
                "agent_id": "hybrid_code_gen",
                "agent_type": "hybrid_integration",
                "reasoning": "Code generation request detected"
            }
        
        # Hybrid Integrations - Image Generation
        if any(kw in command_lower for kw in ['generate image', 'create image', 'nano banana', 'image gen']):
            return {
                "agent_id": "hybrid_image_gen",
                "agent_type": "hybrid_integration",
                "reasoning": "Image generation request detected"
            }
        
        # Hybrid Integrations - Multilingual
        if any(kw in command_lower for kw in ['translate', 'multilingual', 'qwen', 'language']):
            return {
                "agent_id": "hybrid_multilingual",
                "agent_type": "hybrid_integration",
                "reasoning": "Multilingual task detected"
            }
        
        # Hybrid Integrations - Advanced Reasoning
        if any(kw in command_lower for kw in ['reason', 'analyze deeply', 'claude', 'complex problem']):
            return {
                "agent_id": "hybrid_reasoning",
                "agent_type": "hybrid_integration",
                "reasoning": "Advanced reasoning request detected"
            }
        
        # Default: Use ERNIE's LLM for general tasks
        return {
            "agent_id": "ernie_llm",
            "agent_type": "orchestrator",
            "reasoning": "General-purpose AI task"
        }
    
    async def _execute_routed_command(
        self,
        route: Dict[str, Any],
        command: str,
        context: Optional[Dict[str, Any]],
        user_id: Optional[str]
    ) -> Any:
        """Execute command via routed agent"""
        
        agent_id = route.get("agent_id")
        agent_type = route.get("agent_type")
        
        # Check if agent is registered
        if agent_id in self.agent_registry:
            handler = self.agent_registry[agent_id]["handler"]
            return await handler(command, context, user_id)
        
        # Fallback: Execute via ERNIE's LLM
        if agent_id == "ernie_llm" or agent_type == "orchestrator":
            return await self._execute_via_llm(command, context)
        
        # Agent not found
        logger.warning(f"ERNIE: Agent '{agent_id}' not registered, using LLM fallback")
        return await self._execute_via_llm(command, context)
    
    async def _execute_via_llm(
        self,
        command: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute command using ERNIE's LLM capabilities"""
        
        try:
            # Build context-aware prompt
            prompt = f"""Command: {command}

Context: {context if context else 'None provided'}

Execute this command and provide a clear, actionable response."""
            
            # Get LLM response
            response_text = await self.llm.send_message(UserMessage(text=prompt))
            
            return {
                "response": response_text,
                "processed_by": "ERNIE LLM",
                "model": "gpt-5.1"
            }
            
        except Exception as e:
            logger.error(f"ERNIE LLM execution failed: {e}")
            return {
                "response": f"Error processing command: {str(e)}",
                "processed_by": "ERNIE LLM",
                "error": True
            }
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all registered agents"""
        return {
            "orchestrator": "ERNIE",
            "session_id": self.session_id,
            "registered_agents": len(self.agent_registry),
            "agents": [
                {
                    "id": agent_id,
                    "type": info["type"],
                    "capabilities": info["capabilities"],
                    "registered_at": info["registered_at"]
                }
                for agent_id, info in self.agent_registry.items()
            ]
        }
    
    async def multi_agent_workflow(
        self,
        workflow: str,
        steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute a multi-agent workflow
        
        Args:
            workflow: Workflow name/description
            steps: List of workflow steps with agent assignments
            
        Returns:
            Aggregated workflow results
        """
        workflow_id = str(uuid4())
        logger.info(f"ERNIE: Starting multi-agent workflow '{workflow}' (ID: {workflow_id})")
        
        results = []
        
        for step_idx, step in enumerate(steps):
            step_result = await self.execute_command(
                command=step.get("command"),
                context=step.get("context"),
                user_id=step.get("user_id")
            )
            
            results.append({
                "step": step_idx + 1,
                "command": step.get("command"),
                "result": step_result
            })
        
        return {
            "workflow_id": workflow_id,
            "workflow": workflow,
            "steps_executed": len(results),
            "results": results,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }


# Singleton instance
_ernie_instance = None

def get_ernie_orchestrator(db=None) -> ERNIEOrchestrator:
    """Get or create ERNIE orchestrator singleton"""
    global _ernie_instance
    if _ernie_instance is None:
        _ernie_instance = ERNIEOrchestrator(db)
    return _ernie_instance
