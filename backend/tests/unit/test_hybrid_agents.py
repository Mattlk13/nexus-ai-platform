"""
Unit Tests for Hybrid AI Agents
Tests for Code Review, Database Optimization, Bug Detection, Testing, and other agents
"""
import pytest
import asyncio
from services.autonomous.hybrid_agents import (
    CodeReviewAgent,
    DatabaseOptimizationAgent,
    BugDetectionAgent,
    TestingAgent,
    UserSupportAgent,
    GrowthHackingAgent,
    DocumentationAgent,
    CostOptimizationAgent
)


@pytest.mark.unit
@pytest.mark.agents
class TestCodeReviewAgent:
    """Test suite for Code Review Agent"""
    
    @pytest.mark.asyncio
    async def test_code_review_agent_initialization(self):
        """Test agent initialization"""
        agent = CodeReviewAgent()
        assert agent.agent_id == "code-review"
        assert agent.name == "Code Review Agent"
    
    @pytest.mark.asyncio
    async def test_code_review_with_simple_function(self, code_review_agent, sample_code):
        """Test code review with sample code"""
        result = await code_review_agent.execute({
            "code": sample_code,
            "language": "python"
        })
        
        assert result is not None
        assert isinstance(result, dict)
        # Note: Actual AI response validation would require mocking


@pytest.mark.unit
@pytest.mark.agents
class TestDatabaseOptimizationAgent:
    """Test suite for Database Optimization Agent"""
    
    @pytest.mark.asyncio
    async def test_db_agent_initialization(self):
        """Test agent initialization"""
        agent = DatabaseOptimizationAgent()
        assert agent.agent_id == "database-optimization"
    
    @pytest.mark.asyncio
    async def test_query_optimization(self, database_optimization_agent, sample_sql_query):
        """Test SQL query optimization"""
        result = await database_optimization_agent.execute({
            "query": sample_sql_query,
            "database_type": "postgresql"
        })
        
        assert result is not None
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.agents
class TestBugDetectionAgent:
    """Test suite for Bug Detection Agent"""
    
    @pytest.mark.asyncio
    async def test_bug_agent_initialization(self):
        """Test agent initialization"""
        agent = BugDetectionAgent()
        assert agent.agent_id == "bug-detection"
        assert agent.priority.value == "critical"
    
    @pytest.mark.asyncio
    async def test_bug_detection_with_code(self, bug_detection_agent, sample_code):
        """Test bug detection functionality"""
        result = await bug_detection_agent.execute({
            "code": sample_code,
            "language": "python"
        })
        
        assert result is not None
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.agents
class TestTestingAgent:
    """Test suite for Testing Agent (meta!)"""
    
    @pytest.mark.asyncio
    async def test_testing_agent_initialization(self):
        """Test agent initialization"""
        agent = TestingAgent()
        assert agent.agent_id == "testing"
    
    @pytest.mark.asyncio
    async def test_generate_tests(self, testing_agent, sample_code):
        """Test test generation functionality"""
        result = await testing_agent.execute({
            "code": sample_code,
            "language": "python",
            "test_framework": "pytest"
        })
        
        assert result is not None
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.agents
class TestUserSupportAgent:
    """Test suite for User Support Agent"""
    
    @pytest.mark.asyncio
    async def test_support_agent_initialization(self):
        """Test agent initialization"""
        agent = UserSupportAgent()
        assert agent.agent_id == "user-support"
    
    @pytest.mark.asyncio
    async def test_support_query(self):
        """Test customer support query handling"""
        agent = UserSupportAgent()
        result = await agent.execute({
            "query": "How do I reset my password?"
        })
        
        assert result is not None
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.agents
class TestGrowthHackingAgent:
    """Test suite for Growth Hacking Agent"""
    
    @pytest.mark.asyncio
    async def test_growth_agent_initialization(self):
        """Test agent initialization"""
        agent = GrowthHackingAgent()
        assert agent.agent_id == "growth-hacking"
    
    @pytest.mark.asyncio
    async def test_growth_strategy_generation(self):
        """Test growth strategy generation"""
        agent = GrowthHackingAgent()
        result = await agent.execute({
            "product": "Task management app",
            "target_audience": "remote teams"
        })
        
        assert result is not None
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.agents
class TestDocumentationAgent:
    """Test suite for Documentation Agent"""
    
    @pytest.mark.asyncio
    async def test_doc_agent_initialization(self):
        """Test agent initialization"""
        agent = DocumentationAgent()
        assert agent.agent_id == "documentation"
    
    @pytest.mark.asyncio
    async def test_doc_generation(self, sample_code):
        """Test documentation generation"""
        agent = DocumentationAgent()
        result = await agent.execute({
            "code": sample_code,
            "doc_type": "readme"
        })
        
        assert result is not None
        assert isinstance(result, dict)


@pytest.mark.unit
@pytest.mark.agents
class TestCostOptimizationAgent:
    """Test suite for Cost Optimization Agent"""
    
    @pytest.mark.asyncio
    async def test_cost_agent_initialization(self):
        """Test agent initialization"""
        agent = CostOptimizationAgent()
        assert agent.agent_id == "cost-optimization"
    
    @pytest.mark.asyncio
    async def test_cost_analysis(self):
        """Test cost optimization analysis"""
        agent = CostOptimizationAgent()
        result = await agent.execute({
            "platform": "aws",
            "current_cost": 5000,
            "resources": ["EC2", "RDS", "S3"]
        })
        
        assert result is not None
        assert isinstance(result, dict)
