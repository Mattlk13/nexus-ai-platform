"""
Pytest Configuration and Fixtures
Testing framework for NEXUS Platform - 60+ Hybrid Services
"""
import pytest
import asyncio
from typing import Generator
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def api_base_url():
    """Base URL for API testing"""
    return os.getenv("TEST_API_URL", "http://localhost:8001")


@pytest.fixture
def emergent_llm_key():
    """Emergent LLM Key for testing"""
    return os.getenv("EMERGENT_LLM_KEY", "sk-emergent-a79Ba891bC89777B1C")


@pytest.fixture
async def test_context():
    """Common test context"""
    return {
        "test_mode": True,
        "timeout": 10
    }


# Hybrid Agent Fixtures
@pytest.fixture
async def code_review_agent():
    """Code Review Agent instance"""
    from services.autonomous.hybrid_agents import CodeReviewAgent
    return CodeReviewAgent()


@pytest.fixture
async def database_optimization_agent():
    """Database Optimization Agent instance"""
    from services.autonomous.hybrid_agents import DatabaseOptimizationAgent
    return DatabaseOptimizationAgent()


@pytest.fixture
async def bug_detection_agent():
    """Bug Detection Agent instance"""
    from services.autonomous.hybrid_agents import BugDetectionAgent
    return BugDetectionAgent()


@pytest.fixture
async def testing_agent():
    """Testing Agent instance"""
    from services.autonomous.hybrid_agents import TestingAgent
    return TestingAgent()


# Atoms Integration Fixtures
@pytest.fixture
async def iris_agent():
    """Iris Research Agent"""
    from services.atoms_integration import IrisAgent
    return IrisAgent()


@pytest.fixture
async def emma_agent():
    """Emma PM Agent"""
    from services.atoms_integration import EmmaAgent
    return EmmaAgent()


@pytest.fixture
async def bob_agent():
    """Bob Architect Agent"""
    from services.atoms_integration import BobAgent
    return BobAgent()


# Mock Data Fixtures
@pytest.fixture
def sample_code():
    """Sample code for testing"""
    return """
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total
"""


@pytest.fixture
def sample_sql_query():
    """Sample SQL query for testing"""
    return "SELECT * FROM users WHERE email LIKE '%@example.com' AND created_at > '2024-01-01'"


@pytest.fixture
def sample_project_spec():
    """Sample project specification"""
    return {
        "project": "AI-powered task management app",
        "target_audience": "remote teams",
        "key_features": ["real-time collaboration", "AI task prioritization", "integrations"]
    }


# Test markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "agents: AI agent tests")
