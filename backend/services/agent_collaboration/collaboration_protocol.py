"""
Enhanced Agent Communication Protocol
Enables sophisticated agent-to-agent collaboration and workflow orchestration
"""
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum
import json

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Agent role types for specialized tasks"""
    RESEARCHER = "researcher"  # Iris
    PRODUCT_MANAGER = "product_manager"  # Emma
    ARCHITECT = "architect"  # Bob
    SEO_SPECIALIST = "seo_specialist"  # Sarah
    DATA_ANALYST = "data_analyst"  # David
    CODE_REVIEWER = "code_reviewer"  # Code Review Agent
    DATABASE_OPTIMIZER = "database_optimizer"
    BUG_DETECTOR = "bug_detector"
    TESTING_SPECIALIST = "testing_specialist"
    DOCUMENTATION_WRITER = "documentation_writer"
    COST_OPTIMIZER = "cost_optimizer"
    USER_SUPPORT = "user_support"
    GROWTH_HACKER = "growth_hacker"
    TEAM_LEADER = "team_leader"  # Mike


class MessageType(Enum):
    """Types of inter-agent messages"""
    REQUEST = "request"
    RESPONSE = "response"
    DELEGATION = "delegation"
    CONSULTATION = "consultation"
    NOTIFICATION = "notification"
    ERROR = "error"


class AgentMessage:
    """Structured message for agent-to-agent communication"""
    
    def __init__(
        self,
        from_agent: AgentRole,
        to_agent: AgentRole,
        message_type: MessageType,
        content: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        priority: int = 5
    ):
        self.message_id = str(uuid.uuid4())
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.content = content
        self.context = context or {}
        self.priority = priority
        self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent.value,
            "to_agent": self.to_agent.value,
            "message_type": self.message_type.value,
            "content": self.content,
            "context": self.context,
            "priority": self.priority,
            "timestamp": self.timestamp
        }


class AgentCollaborationHub:
    """
    Central hub for managing agent collaboration and communication
    Enables sophisticated multi-agent workflows
    """
    
    def __init__(self):
        self.message_queue: List[AgentMessage] = []
        self.workflow_history: List[Dict[str, Any]] = []
        self.agent_registry: Dict[str, Any] = {}
    
    def register_agent(self, agent_role: AgentRole, agent_instance: Any):
        """Register an agent in the collaboration hub"""
        self.agent_registry[agent_role.value] = {
            "instance": agent_instance,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "message_count": 0
        }
        logger.info(f"Registered agent: {agent_role.value}")
    
    def send_message(self, message: AgentMessage) -> str:
        """Send a message to another agent"""
        self.message_queue.append(message)
        
        if message.from_agent.value in self.agent_registry:
            self.agent_registry[message.from_agent.value]["message_count"] += 1
        
        logger.info(
            f"Message sent: {message.from_agent.value} -> {message.to_agent.value} "
            f"[{message.message_type.value}]"
        )
        
        return message.message_id
    
    def get_messages_for_agent(self, agent_role: AgentRole) -> List[AgentMessage]:
        """Retrieve messages for a specific agent"""
        messages = [
            msg for msg in self.message_queue 
            if msg.to_agent == agent_role
        ]
        return sorted(messages, key=lambda x: x.priority, reverse=True)
    
    async def delegate_task(
        self,
        from_agent: AgentRole,
        to_agent: AgentRole,
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Delegate a task from one agent to another"""
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.DELEGATION,
            content={"task": task, "details": context},
            context=context,
            priority=8
        )
        
        message_id = self.send_message(message)
        
        # Execute delegation
        target_agent = self.agent_registry.get(to_agent.value)
        if target_agent and target_agent["instance"]:
            try:
                result = await target_agent["instance"].execute(context)
                
                # Send response back
                response_message = AgentMessage(
                    from_agent=to_agent,
                    to_agent=from_agent,
                    message_type=MessageType.RESPONSE,
                    content={"result": result, "original_message_id": message_id},
                    context=context
                )
                self.send_message(response_message)
                
                return {
                    "success": True,
                    "delegation_id": message_id,
                    "result": result
                }
            except Exception as e:
                logger.error(f"Delegation failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "delegation_id": message_id
                }
        
        return {
            "success": False,
            "error": f"Target agent {to_agent.value} not registered"
        }
    
    async def consult_agent(
        self,
        from_agent: AgentRole,
        to_agent: AgentRole,
        question: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Consult another agent for expertise"""
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.CONSULTATION,
            content={"question": question, "context": context},
            context=context,
            priority=6
        )
        
        message_id = self.send_message(message)
        
        # Execute consultation
        target_agent = self.agent_registry.get(to_agent.value)
        if target_agent and target_agent["instance"]:
            try:
                result = await target_agent["instance"].execute({
                    "query": question,
                    **context
                })
                
                return {
                    "success": True,
                    "consultation_id": message_id,
                    "advice": result
                }
            except Exception as e:
                logger.error(f"Consultation failed: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": False,
            "error": f"Agent {to_agent.value} not available"
        }
    
    def get_workflow_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent workflow execution history"""
        return self.workflow_history[-limit:]
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics about agent activity"""
        return {
            "total_agents": len(self.agent_registry),
            "total_messages": len(self.message_queue),
            "agents": {
                role: {
                    "message_count": info["message_count"],
                    "registered_at": info["registered_at"]
                }
                for role, info in self.agent_registry.items()
            }
        }


class EnhancedPromptTemplate:
    """
    Sophisticated prompt templates with context injection
    Improves agent response quality and consistency
    """
    
    @staticmethod
    def code_review_prompt(
        code: str,
        language: str,
        context: Dict[str, Any]
    ) -> str:
        """Enhanced code review prompt with multi-dimensional analysis"""
        return f"""You are a senior code review expert with 15+ years of experience across multiple domains.

**Code to Review:**
```{language}
{code}
```

**Review Context:**
- Language: {language}
- Project Type: {context.get('project_type', 'Unknown')}
- Team Size: {context.get('team_size', 'Unknown')}
- Critical Path: {context.get('is_critical', 'No')}

**Comprehensive Review Framework:**

1. **Security Analysis** (Weight: 10/10)
   - Identify vulnerabilities (SQL injection, XSS, CSRF, etc.)
   - Check authentication and authorization
   - Assess data validation and sanitization
   - Review cryptographic implementations
   - Rate: CRITICAL/HIGH/MEDIUM/LOW

2. **Performance Analysis** (Weight: 9/10)
   - Identify algorithmic complexity issues
   - Detect memory leaks and inefficient allocations
   - Check database query optimization
   - Assess caching opportunities
   - Estimate performance impact: <1ms / <10ms / <100ms / >100ms

3. **Code Quality** (Weight: 8/10)
   - SOLID principles adherence
   - DRY (Don't Repeat Yourself) violations
   - Readability and maintainability score (1-10)
   - Test coverage implications
   - Documentation quality

4. **Bug Detection** (Weight: 10/10)
   - Logic errors and edge cases
   - Race conditions and concurrency issues
   - Null pointer risks
   - Type mismatches
   - Off-by-one errors

5. **Best Practices** (Weight: 7/10)
   - Language-specific idioms
   - Framework conventions
   - Error handling patterns
   - Logging and monitoring

**Output Format (JSON):**
{{
  "overall_score": 0-100,
  "security": {{
    "issues": [{{severity, description, line, fix}}],
    "score": 0-100
  }},
  "performance": {{
    "bottlenecks": [{{impact, description, solution}}],
    "score": 0-100
  }},
  "quality": {{
    "issues": [{{type, description, refactoring}}],
    "score": 0-100
  }},
  "bugs": [{{severity, line, description, fix}}],
  "recommendations": [{{priority, action, benefit}}],
  "approval_status": "APPROVED|CHANGES_REQUESTED|REJECTED"
}}"""

    @staticmethod
    def database_optimization_prompt(
        query: str,
        database_type: str,
        schema: Optional[str]
    ) -> str:
        """Enhanced database optimization prompt"""
        return f"""You are a database performance expert specializing in {database_type} optimization.

**Query to Optimize:**
```sql
{query}
```

**Database Context:**
- Type: {database_type}
- Schema: {schema if schema else 'Not provided - infer from query'}

**Optimization Framework:**

1. **Query Analysis**
   - Current execution plan (estimated)
   - Complexity assessment: O(1), O(log n), O(n), O(n²)
   - Joins analysis (type, order, cost)
   - Subquery evaluation

2. **Performance Issues**
   - Table scans (full table vs index scan)
   - Missing indexes
   - Inefficient joins
   - N+1 query patterns
   - Lock contention risks

3. **Optimized Solution**
   - Rewritten query with explanations
   - Index recommendations with CREATE statements
   - Query hints and optimizer directives
   - Estimated performance improvement: %

4. **Best Practices**
   - Pagination strategy
   - Caching opportunities
   - Read replica usage
   - Query parameterization

**Output Format (JSON):**
{{
  "original_query_score": 0-100,
  "issues": [{{severity, type, impact}}],
  "optimized_query": "SQL here",
  "indexes": [{{
    "table": "name",
    "columns": ["col1", "col2"],
    "type": "BTREE|HASH|GIN",
    "sql": "CREATE INDEX statement"
  }}],
  "performance_gain": "2x|5x|10x|50x",
  "implementation_priority": "IMMEDIATE|HIGH|MEDIUM|LOW"
}}"""

    @staticmethod
    def research_prompt(task: str, context: Dict[str, Any]) -> str:
        """Enhanced research prompt with systematic methodology"""
        return f"""You are Iris, a deep research specialist with expertise in market analysis and opportunity identification.

**Research Task:** {task}

**Context:**
- Industry: {context.get('industry', 'General')}
- Target Audience: {context.get('target_audience', 'Unknown')}
- Time Frame: {context.get('time_frame', 'Current')}
- Geographic Focus: {context.get('geographic_focus', 'Global')}

**Research Methodology:**

1. **Market Demand Analysis**
   - Current market size and growth rate
   - Demand signals and trends
   - Pain points and unmet needs
   - Customer segments and personas

2. **Opportunity Identification**
   - Market gaps and white spaces
   - Emerging trends and technologies
   - Competitive advantages
   - Entry barriers and moats

3. **Target Audience Profiling**
   - Demographics and psychographics
   - Behaviors and preferences
   - Willingness to pay
   - Acquisition channels

4. **Competitive Landscape**
   - Direct and indirect competitors
   - Market positioning
   - Strengths and weaknesses
   - Differentiation opportunities

5. **Validation Metrics**
   - TAM/SAM/SOM analysis
   - Search volume and trends
   - Social media signals
   - Investment and funding data

**Output Format (JSON):**
{{
  "demand_analysis": {{
    "market_size": "value + source",
    "growth_rate": "%",
    "trends": [{{name, strength, timeline}}]
  }},
  "opportunities": [{{
    "opportunity": "description",
    "market_gap": "what's missing",
    "potential_revenue": "estimate",
    "timeframe": "short|medium|long term",
    "confidence": "high|medium|low"
  }}],
  "target_audience": {{
    "segments": [{{name, size, characteristics}}],
    "personas": [{{name, goals, pains, gains}}]
  }},
  "competitors": [{{
    "name": "company",
    "positioning": "how they compete",
    "weakness": "what to exploit"
  }}],
  "metrics": {{
    "tam": "value",
    "sam": "value",
    "som": "value"
  }},
  "recommendation": "GO|PIVOT|NO-GO",
  "confidence_score": 0-100
}}"""


# Global collaboration hub instance
collaboration_hub = AgentCollaborationHub()
