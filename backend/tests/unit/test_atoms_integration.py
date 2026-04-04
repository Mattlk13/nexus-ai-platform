"""
Unit Tests for Atoms Integration Agents
Tests for Iris, Emma, Bob, Sarah, David, Mike, and Race Mode
"""
import pytest
from services.atoms_integration import (
    IrisAgent,
    EmmaAgent,
    BobAgent,
    SarahAgent,
    DavidAgent,
    MikeAgent,
    RaceMode
)


@pytest.mark.unit
@pytest.mark.agents
class TestIrisAgent:
    """Test suite for Iris - Deep Research Agent"""
    
    @pytest.mark.asyncio
    async def test_iris_initialization(self):
        """Test Iris agent initialization"""
        agent = IrisAgent()
        assert agent.agent_id == "iris-research"
        assert agent.name == "Iris"
        assert agent.role == "Deep Researcher"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_iris_market_research(self, iris_agent):
        """Test market research functionality"""
        result = await iris_agent.execute(
            "AI productivity tools for developers",
            {"industry": "software"}
        )
        
        assert result is not None
        assert result.get("agent") == "Iris"


@pytest.mark.unit
@pytest.mark.agents
class TestEmmaAgent:
    """Test suite for Emma - Product Manager Agent"""
    
    @pytest.mark.asyncio
    async def test_emma_initialization(self):
        """Test Emma agent initialization"""
        agent = EmmaAgent()
        assert agent.agent_id == "emma-pm"
        assert agent.name == "Emma"
        assert agent.role == "Product Manager"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_emma_product_spec(self, emma_agent, sample_project_spec):
        """Test product specification generation"""
        result = await emma_agent.execute(
            sample_project_spec["project"],
            sample_project_spec
        )
        
        assert result is not None
        assert result.get("agent") == "Emma"


@pytest.mark.unit
@pytest.mark.agents
class TestBobAgent:
    """Test suite for Bob - Systems Architect Agent"""
    
    @pytest.mark.asyncio
    async def test_bob_initialization(self):
        """Test Bob agent initialization"""
        agent = BobAgent()
        assert agent.agent_id == "bob-architect"
        assert agent.name == "Bob"
        assert agent.role == "Architect"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_bob_architecture_design(self, bob_agent):
        """Test architecture design functionality"""
        result = await bob_agent.execute(
            "Real-time chat platform with 10k concurrent users",
            {}
        )
        
        assert result is not None
        assert result.get("agent") == "Bob"


@pytest.mark.unit
@pytest.mark.agents
class TestSarahAgent:
    """Test suite for Sarah - SEO Specialist Agent"""
    
    @pytest.mark.asyncio
    async def test_sarah_initialization(self):
        """Test Sarah agent initialization"""
        agent = SarahAgent()
        assert agent.agent_id == "sarah-seo"
        assert agent.name == "Sarah"
        assert agent.role == "SEO Specialist"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_sarah_seo_strategy(self, sample_project_spec):
        """Test SEO strategy generation"""
        agent = SarahAgent()
        result = await agent.execute(
            f"Optimize SEO for {sample_project_spec['project']}",
            sample_project_spec
        )
        
        assert result is not None
        assert result.get("agent") == "Sarah"


@pytest.mark.unit
@pytest.mark.agents
class TestDavidAgent:
    """Test suite for David - Data Analyst Agent"""
    
    @pytest.mark.asyncio
    async def test_david_initialization(self):
        """Test David agent initialization"""
        agent = DavidAgent()
        assert agent.agent_id == "david-analyst"
        assert agent.name == "David"
        assert agent.role == "Data Analyst"
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_david_data_analysis(self):
        """Test data analysis functionality"""
        agent = DavidAgent()
        result = await agent.execute(
            "Analyze user engagement metrics",
            {"metrics": {"dau": 1000, "retention": 0.6}}
        )
        
        assert result is not None
        assert result.get("agent") == "David"


@pytest.mark.unit
@pytest.mark.agents
class TestMikeAgent:
    """Test suite for Mike - Team Leader Agent"""
    
    @pytest.mark.asyncio
    async def test_mike_initialization(self):
        """Test Mike agent initialization"""
        agent = MikeAgent()
        assert agent.agent_id == "mike-leader"
        assert agent.name == "Mike"
        assert agent.role == "Team Leader"
        assert len(agent.agents) == 5  # Iris, Emma, Bob, Sarah, David
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_mike_full_workflow(self, sample_project_spec):
        """Test full multi-agent workflow"""
        agent = MikeAgent()
        result = await agent.execute(
            sample_project_spec["project"],
            sample_project_spec
        )
        
        assert result is not None
        assert result.get("agent") == "Mike"
        # Should have 5 phases
        if result.get("success"):
            assert len(result["workflow"]["phases"]) == 5


@pytest.mark.unit
@pytest.mark.agents
class TestRaceMode:
    """Test suite for Race Mode"""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_race_mode_multiple_solutions(self):
        """Test generating multiple solutions"""
        result = await RaceMode.race(
            "How to improve app performance?",
            count=3
        )
        
        assert result is not None
        assert result.get("success") is True
        if result.get("success"):
            assert len(result["solutions"]) == 3
