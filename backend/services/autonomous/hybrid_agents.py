"""
Specialized Hybrid AI Agents for NEXUS
Advanced AI-powered agents for Code Review, Database Optimization, Cost Management, etc.
"""
import logging
import os
import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from .orchestrator import AutonomousAgent, AgentPriority
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import re

logger = logging.getLogger(__name__)

# Initialize Emergent LLM Key
EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY", "sk-emergent-a79Ba891bC89777B1C")


class CodeReviewAgent(AutonomousAgent):
    """
    Automated Code Review Agent - Reviews PRs, suggests improvements, finds issues
    Uses AI to analyze code quality, security, performance, and best practices
    """
    def __init__(self):
        super().__init__(
            agent_id="code-review",
            name="Code Review Agent",
            description="AI-powered automatic code review for PRs and commits"
        )
        self.priority = AgentPriority.HIGH
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review code and provide detailed feedback
        
        Context params:
        - code: The code to review (string)
        - language: Programming language (optional)
        - pr_description: PR description (optional)
        """
        code = context.get("code", "")
        language = context.get("language", "python")
        pr_description = context.get("pr_description", "")
        
        if not code:
            return {"error": "No code provided for review"}
        
        try:
            # AI-powered code review
            prompt = f"""You are an expert code reviewer. Review the following {language} code and provide:

1. **Security Issues**: Any security vulnerabilities or risks
2. **Performance Issues**: Performance bottlenecks or inefficiencies
3. **Code Quality**: Best practices, readability, maintainability concerns
4. **Bugs**: Potential bugs or logic errors
5. **Suggestions**: Specific improvements with code examples

Code to review:
```{language}
{code}
```

{f"PR Description: {pr_description}" if pr_description else ""}

Provide a structured JSON response with: security_issues, performance_issues, quality_issues, bugs, suggestions, overall_rating (1-10)."""

            # Use Emergent LLM integration
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"code-review-{uuid.uuid4()}",
                system_message="You are an expert code reviewer with deep knowledge of software engineering best practices, security, and performance optimization."
            ).with_model("openai", "gpt-5.1")
            
            user_message = UserMessage(text=prompt)
            review_text = await chat.send_message(user_message)
            
            # Try to parse JSON response
            try:
                review_data = json.loads(review_text)
            except:
                # If not JSON, structure the text response
                review_data = {
                    "review": review_text,
                    "overall_rating": self._extract_rating(review_text)
                }
            
            return {
                "success": True,
                "language": language,
                "review": review_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent": "code-review"
            }
            
        except Exception as e:
            logger.error(f"Code review failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_rating(self, text: str) -> int:
        """Extract numeric rating from text"""
        match = re.search(r'rating[:\s]+(\d+)', text, re.IGNORECASE)
        return int(match.group(1)) if match else 7


class DatabaseOptimizationAgent(AutonomousAgent):
    """
    Database Optimization Agent - Analyzes and optimizes SQL queries
    Suggests indexes, rewrites queries, identifies N+1 problems
    """
    def __init__(self):
        super().__init__(
            agent_id="database-optimization",
            name="Database Optimization Agent",
            description="AI-powered database query optimization and tuning"
        )
        self.priority = AgentPriority.HIGH
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize database queries
        
        Context params:
        - query: SQL query to optimize
        - database_type: mysql, postgresql, mongodb, etc.
        - schema: Database schema (optional)
        """
        query = context.get("query", "")
        db_type = context.get("database_type", "postgresql")
        schema = context.get("schema", "")
        
        if not query:
            return {"error": "No query provided for optimization"}
        
        try:
            prompt = f"""You are a database optimization expert. Analyze and optimize this {db_type} query:

Query:
```sql
{query}
```

{f"Schema: {schema}" if schema else ""}

Provide:
1. **Performance Analysis**: Current query issues
2. **Optimized Query**: Improved version of the query
3. **Index Recommendations**: Suggested indexes with CREATE INDEX statements
4. **Execution Plan Insights**: Expected performance improvement
5. **Best Practices**: General recommendations

Return as JSON with: performance_issues, optimized_query, index_recommendations, improvement_estimate, best_practices"""

            response = ai_client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": "You are a database performance expert specializing in query optimization, indexing strategies, and database tuning."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            optimization = response.choices[0].message.content
            
            try:
                optimization_data = json.loads(optimization)
            except:
                optimization_data = {"analysis": optimization}
            
            return {
                "success": True,
                "database_type": db_type,
                "original_query": query,
                "optimization": optimization_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            return {"success": False, "error": str(e)}


class CostOptimizationAgent(AutonomousAgent):
    """
    Cost Optimization Agent - Reduces cloud infrastructure costs
    Analyzes resource usage, suggests cost-saving measures
    """
    def __init__(self):
        super().__init__(
            agent_id="cost-optimization",
            name="Cost Optimization Agent",
            description="AI-powered cloud cost reduction and resource optimization"
        )
        self.priority = AgentPriority.MEDIUM
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze costs and suggest optimizations
        
        Context params:
        - platform: aws, azure, gcp, etc.
        - current_cost: Current monthly cost
        - resources: List of resources being used
        """
        platform = context.get("platform", "aws")
        current_cost = context.get("current_cost", 0)
        resources = context.get("resources", [])
        
        try:
            prompt = f"""You are a cloud cost optimization expert for {platform}. 

Current monthly cost: ${current_cost}
Resources in use: {json.dumps(resources, indent=2) if resources else "Not provided"}

Analyze and provide:
1. **Cost Analysis**: Breakdown of current spending
2. **Optimization Opportunities**: Specific cost-saving recommendations
3. **Right-Sizing**: Instance/resource size recommendations
4. **Reserved Instances**: Reservation recommendations
5. **Estimated Savings**: Projected monthly savings

Return as JSON with: cost_analysis, optimizations (list), estimated_monthly_savings, implementation_priority"""

            response = ai_client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": f"You are a {platform} cloud cost optimization expert with deep knowledge of pricing models, resource optimization, and FinOps best practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            optimization = response.choices[0].message.content
            
            try:
                optimization_data = json.loads(optimization)
            except:
                optimization_data = {"recommendations": optimization}
            
            return {
                "success": True,
                "platform": platform,
                "current_cost": current_cost,
                "optimization": optimization_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Cost optimization failed: {e}")
            return {"success": False, "error": str(e)}


class UserSupportAgent(AutonomousAgent):
    """
    AI Customer Support Agent - Handles user queries automatically
    Provides intelligent, context-aware support responses
    """
    def __init__(self):
        super().__init__(
            agent_id="user-support",
            name="User Support Agent",
            description="AI-powered customer support and query resolution"
        )
        self.priority = AgentPriority.HIGH
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle customer support query
        
        Context params:
        - query: User's question or issue
        - user_context: Additional user info (optional)
        - conversation_history: Previous messages (optional)
        """
        query = context.get("query", "")
        user_context = context.get("user_context", {})
        history = context.get("conversation_history", [])
        
        if not query:
            return {"error": "No support query provided"}
        
        try:
            messages = [
                {"role": "system", "content": """You are a helpful, professional customer support agent for NEXUS AI Social Marketplace & Creator Hub. 

Your role:
- Answer user questions clearly and concisely
- Troubleshoot technical issues
- Guide users through features
- Escalate complex issues when needed
- Be empathetic and solution-oriented

Platform features: AI tools, creator marketplace, social features, intelligence suite, autonomous agents, integrations."""}
            ]
            
            # Add conversation history
            for msg in history[-5:]:  # Last 5 messages
                messages.append(msg)
            
            # Add current query
            user_msg = f"{query}"
            if user_context:
                user_msg += f"\n\nUser Context: {json.dumps(user_context)}"
            
            messages.append({"role": "user", "content": user_msg})
            
            response = ai_client.chat.completions.create(
                model="gpt-5.1",
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            support_response = response.choices[0].message.content
            
            return {
                "success": True,
                "query": query,
                "response": support_response,
                "sentiment": "neutral",  # Could add sentiment analysis
                "escalate": self._should_escalate(support_response),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"User support failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _should_escalate(self, response: str) -> bool:
        """Determine if issue should be escalated to human"""
        escalation_keywords = ["sorry, i cannot", "beyond my capabilities", "contact support", "escalate"]
        return any(keyword in response.lower() for keyword in escalation_keywords)


class GrowthHackingAgent(AutonomousAgent):
    """
    Growth Hacking Agent - Generates viral marketing strategies
    Creates data-driven growth tactics and campaigns
    """
    def __init__(self):
        super().__init__(
            agent_id="growth-hacking",
            name="Growth Hacking Agent",
            description="AI-powered viral marketing and growth strategy generation"
        )
        self.priority = AgentPriority.MEDIUM
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate growth hacking strategies
        
        Context params:
        - product: Product/feature to promote
        - target_audience: Target user demographics
        - current_metrics: Current growth metrics
        - goals: Specific goals (optional)
        """
        product = context.get("product", "NEXUS Platform")
        target_audience = context.get("target_audience", "creators and developers")
        metrics = context.get("current_metrics", {})
        goals = context.get("goals", "increase user acquisition")
        
        try:
            prompt = f"""You are a growth hacking expert. Create viral marketing strategies for:

Product: {product}
Target Audience: {target_audience}
Current Metrics: {json.dumps(metrics, indent=2) if metrics else "Not provided"}
Goals: {goals}

Generate:
1. **Viral Strategies**: 3-5 creative growth hacking tactics
2. **Content Ideas**: Viral content concepts
3. **Channel Strategy**: Best platforms and approaches
4. **A/B Test Ideas**: Experiments to run
5. **Metrics to Track**: KPIs for success

Return as JSON with: strategies (list), content_ideas (list), channels (list), ab_tests (list), kpis (list)"""

            response = ai_client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": "You are a growth hacking expert with deep experience in viral marketing, user acquisition, and data-driven growth strategies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1500
            )
            
            strategies = response.choices[0].message.content
            
            try:
                strategies_data = json.loads(strategies)
            except:
                strategies_data = {"strategies": strategies}
            
            return {
                "success": True,
                "product": product,
                "growth_strategies": strategies_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Growth hacking agent failed: {e}")
            return {"success": False, "error": str(e)}


class BugDetectionAgent(AutonomousAgent):
    """
    Bug Detection Agent - Automatically finds bugs in code
    Uses AI + static analysis to identify potential issues
    """
    def __init__(self):
        super().__init__(
            agent_id="bug-detection",
            name="Bug Detection Agent",
            description="AI-powered automatic bug and vulnerability detection"
        )
        self.priority = AgentPriority.CRITICAL
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect bugs in code
        
        Context params:
        - code: Code to analyze
        - language: Programming language
        - context: Additional context (optional)
        """
        code = context.get("code", "")
        language = context.get("language", "python")
        code_context = context.get("context", "")
        
        if not code:
            return {"error": "No code provided for bug detection"}
        
        try:
            prompt = f"""You are an expert bug detection AI. Analyze this {language} code for bugs, vulnerabilities, and potential issues:

Code:
```{language}
{code}
```

{f"Context: {code_context}" if code_context else ""}

Identify:
1. **Critical Bugs**: Severe bugs that will cause failures
2. **Security Vulnerabilities**: Security risks and exploits
3. **Logic Errors**: Incorrect logic or edge cases not handled
4. **Memory Issues**: Memory leaks, inefficient allocations
5. **Race Conditions**: Concurrency issues
6. **Type Errors**: Type mismatches or incorrect assumptions

For each issue provide: severity (critical/high/medium/low), line_number (if identifiable), description, fix_suggestion

Return as JSON with: critical_bugs (list), security_vulnerabilities (list), logic_errors (list), other_issues (list), overall_risk_level"""

            response = ai_client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": "You are a bug detection expert with deep knowledge of common bugs, security vulnerabilities, and code quality issues across multiple programming languages."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            bugs = response.choices[0].message.content
            
            try:
                bugs_data = json.loads(bugs)
            except:
                bugs_data = {"analysis": bugs}
            
            return {
                "success": True,
                "language": language,
                "bugs_detected": bugs_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Bug detection failed: {e}")
            return {"success": False, "error": str(e)}


class DocumentationAgent(AutonomousAgent):
    """
    Documentation Agent - Automatically generates documentation
    Creates comprehensive docs from code, APIs, and specifications
    """
    def __init__(self):
        super().__init__(
            agent_id="documentation",
            name="Documentation Agent",
            description="AI-powered automatic documentation generation"
        )
        self.priority = AgentPriority.MEDIUM
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate documentation
        
        Context params:
        - code: Code to document (optional)
        - api_spec: API specification (optional)
        - doc_type: readme, api, function, class, etc.
        - style: documentation style (optional)
        """
        code = context.get("code", "")
        api_spec = context.get("api_spec", "")
        doc_type = context.get("doc_type", "readme")
        style = context.get("style", "clear and professional")
        
        if not code and not api_spec:
            return {"error": "No code or API specification provided"}
        
        try:
            content = code or api_spec
            content_type = "code" if code else "API specification"
            
            prompt = f"""You are a technical documentation expert. Generate {doc_type} documentation for this {content_type}:

{content_type}:
```
{content}
```

Create {style} documentation including:
1. **Overview**: What this does
2. **Usage**: How to use it with examples
3. **Parameters**: Input parameters and types
4. **Returns**: Return values and types
5. **Examples**: Code examples
6. **Notes**: Important considerations

For {doc_type} format, use appropriate structure (markdown for README, detailed for API docs, etc.)"""

            response = ai_client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": "You are a technical documentation expert who creates clear, comprehensive, and user-friendly documentation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            documentation = response.choices[0].message.content
            
            return {
                "success": True,
                "doc_type": doc_type,
                "documentation": documentation,
                "format": "markdown",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Documentation generation failed: {e}")
            return {"success": False, "error": str(e)}


class TestingAgent(AutonomousAgent):
    """
    Testing Agent - Automatically writes test cases
    Generates unit tests, integration tests, and test data
    """
    def __init__(self):
        super().__init__(
            agent_id="testing",
            name="Testing Agent",
            description="AI-powered automatic test generation and testing"
        )
        self.priority = AgentPriority.HIGH
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate tests
        
        Context params:
        - code: Code to test
        - language: Programming language
        - test_framework: pytest, jest, unittest, etc.
        - test_type: unit, integration, e2e
        """
        code = context.get("code", "")
        language = context.get("language", "python")
        framework = context.get("test_framework", "pytest" if language == "python" else "jest")
        test_type = context.get("test_type", "unit")
        
        if not code:
            return {"error": "No code provided for test generation"}
        
        try:
            prompt = f"""You are a test automation expert. Generate {test_type} tests using {framework} for this {language} code:

Code to test:
```{language}
{code}
```

Generate comprehensive tests including:
1. **Happy Path Tests**: Normal operation scenarios
2. **Edge Cases**: Boundary conditions and limits
3. **Error Cases**: Invalid inputs and error handling
4. **Mock/Fixture Data**: Test data setup
5. **Assertions**: Proper test assertions

Write production-ready {framework} tests with:
- Clear test names describing what's being tested
- Proper setup and teardown
- Good test coverage (aim for 80%+)
- Comments explaining complex test scenarios

Return complete, runnable test code."""

            response = ai_client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": f"You are a test automation expert specializing in {language} and {framework}. You write comprehensive, maintainable tests."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=2500
            )
            
            tests = response.choices[0].message.content
            
            # Extract code from markdown if present
            if "```" in tests:
                code_match = re.search(r'```(?:' + language + r')?\n(.*?)\n```', tests, re.DOTALL)
                if code_match:
                    tests = code_match.group(1)
            
            return {
                "success": True,
                "language": language,
                "framework": framework,
                "test_type": test_type,
                "tests": tests,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Test generation failed: {e}")
            return {"success": False, "error": str(e)}


# Initialize hybrid agents function
def initialize_hybrid_agents():
    """
    Initialize and register all hybrid AI agents
    """
    from .orchestrator import orchestrator
    
    agents = [
        CodeReviewAgent(),
        DatabaseOptimizationAgent(),
        CostOptimizationAgent(),
        UserSupportAgent(),
        GrowthHackingAgent(),
        BugDetectionAgent(),
        DocumentationAgent(),
        TestingAgent()
    ]
    
    for agent in agents:
        orchestrator.register_agent(agent)
    
    logger.info(f"Initialized {len(agents)} hybrid AI agents")
    return agents
