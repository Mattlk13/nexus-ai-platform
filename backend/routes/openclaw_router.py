"""
Enhanced OpenClaw Integration Router
Provides advanced OpenClaw gateway management and GitHub repo integration
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import httpx
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/openclaw", tags=["openclaw"])


# ============== Request/Response Models ==============

class OpenClawStartRequest(BaseModel):
    provider: str = "emergent"  # "emergent", "anthropic", or "openai"
    apiKey: Optional[str] = None


class OpenClawStartResponse(BaseModel):
    ok: bool
    controlUrl: str
    token: str
    message: str
    provider: str
    features: List[str]


class OpenClawStatusResponse(BaseModel):
    running: bool
    pid: Optional[int] = None
    provider: Optional[str] = None
    started_at: Optional[str] = None
    controlUrl: Optional[str] = None
    owner_user_id: Optional[str] = None
    is_owner: Optional[bool] = None
    uptime_seconds: Optional[int] = None
    health: Optional[str] = None


class OpenClawCapabilities(BaseModel):
    """OpenClaw capabilities based on GitHub repo analysis"""
    coding: List[str]
    multimodal: List[str]
    integrations: List[str]
    platforms: List[str]


class OpenClawTask(BaseModel):
    task_id: str
    description: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Dict] = None


class OpenClawTaskRequest(BaseModel):
    description: str
    context: Optional[str] = None
    files: Optional[List[str]] = None


# ============== Enhanced Endpoints ==============

@router.get("/capabilities")
async def get_openclaw_capabilities() -> OpenClawCapabilities:
    """
    Get OpenClaw capabilities (based on GitHub repo openclaw/openclaw)
    
    OpenClaw is a comprehensive AI assistant supporting:
    - Multi-platform deployment (macOS, Linux, Windows, Mobile)
    - Advanced coding assistance with MCP protocol
    - Browser automation and control
    - File system operations
    - Agent-based workflows
    """
    return OpenClawCapabilities(
        coding=[
            "Code generation and editing",
            "Multi-file refactoring",
            "Git operations",
            "Test generation",
            "Code review and optimization"
        ],
        multimodal=[
            "Text generation",
            "Vision/image analysis",
            "Document processing",
            "Browser automation",
            "Screen capture and analysis"
        ],
        integrations=[
            "MCP (Model Context Protocol)",
            "GitHub integration",
            "File system access",
            "Browser control",
            "Shell/terminal access",
            "API integrations"
        ],
        platforms=[
            "macOS (desktop app)",
            "Linux (CLI + desktop)",
            "Windows (desktop app)",
            "iOS (mobile)",
            "Android (mobile)",
            "Web (browser extension)"
        ]
    )


@router.get("/features")
async def get_openclaw_features():
    """Get current OpenClaw features available in Nexus"""
    return {
        "gateway_features": [
            "Multi-provider LLM routing (Emergent, OpenAI, Anthropic)",
            "WhatsApp integration",
            "Supervisor-managed process lifecycle",
            "Per-user authentication and access control",
            "Auto-restart on crash",
            "Health monitoring"
        ],
        "nexus_integrations": [
            "Maintenance dashboard monitoring",
            "Smart LLM routing (ERNIE 5.0 + Emergent)",
            "Multimodal AI services (InclusionAI)",
            "60+ hybrid autonomous services",
            "Real-time status tracking"
        ],
        "github_repo_info": {
            "repo": "https://github.com/openclaw/openclaw",
            "stars": "345k+",
            "commits": "24,527+",
            "contributors": "1,467+",
            "latest_version": "2026.4.2",
            "description": "Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞"
        }
    }


@router.get("/health")
async def check_openclaw_health():
    """
    Advanced health check for OpenClaw gateway
    Returns detailed health metrics
    """
    try:
        # Import from main server to access gateway state
        from server import check_gateway_running, gateway_state, MOLTBOT_PORT
        
        running = check_gateway_running()
        
        if not running:
            return {
                "status": "stopped",
                "healthy": False,
                "message": "OpenClaw gateway is not running"
            }
        
        # Check if gateway responds
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"http://127.0.0.1:{MOLTBOT_PORT}/", timeout=5.0)
                gateway_responsive = response.status_code == 200
            except Exception:
                gateway_responsive = False
        
        # Calculate uptime
        uptime_seconds = None
        if gateway_state["started_at"]:
            try:
                started = datetime.fromisoformat(gateway_state["started_at"].replace('Z', '+00:00'))
                uptime_seconds = int((datetime.now(timezone.utc) - started).total_seconds())
            except Exception:
                pass
        
        health_status = "healthy" if gateway_responsive else "degraded"
        
        return {
            "status": "running",
            "healthy": gateway_responsive,
            "health_status": health_status,
            "provider": gateway_state.get("provider"),
            "uptime_seconds": uptime_seconds,
            "started_at": gateway_state.get("started_at"),
            "owner": gateway_state.get("owner_user_id"),
            "port": MOLTBOT_PORT,
            "responsive": gateway_responsive
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "healthy": False,
            "error": str(e)
        }


@router.get("/integration-guide")
async def get_integration_guide():
    """
    Get comprehensive integration guide for OpenClaw
    Based on GitHub repo and current Nexus integration
    """
    return {
        "quick_start": {
            "step_1": "Sign in with Google at the main app",
            "step_2": "Choose provider (Emergent recommended - no API key needed)",
            "step_3": "Click 'Start OpenClaw' button",
            "step_4": "Access control UI at /api/openclaw/ui/"
        },
        "providers": {
            "emergent": {
                "recommended": True,
                "requires_api_key": False,
                "features": "Access to GPT-5.2, Claude 4, Gemini 2.5 Pro",
                "cost": "Pay-as-you-go via Emergent LLM Key"
            },
            "openai": {
                "recommended": False,
                "requires_api_key": True,
                "features": "Direct OpenAI API access",
                "cost": "Your own OpenAI API costs"
            },
            "anthropic": {
                "recommended": False,
                "requires_api_key": True,
                "features": "Direct Claude API access",
                "cost": "Your own Anthropic API costs"
            }
        },
        "endpoints": {
            "start": "POST /api/openclaw/start",
            "stop": "POST /api/openclaw/stop",
            "status": "GET /api/openclaw/status",
            "health": "GET /api/openclaw/health",
            "capabilities": "GET /api/openclaw/capabilities",
            "whatsapp": "GET /api/openclaw/whatsapp/status"
        },
        "github_repo": {
            "url": "https://github.com/openclaw/openclaw",
            "documentation": "https://github.com/openclaw/openclaw/tree/main/docs",
            "contributing": "https://github.com/openclaw/openclaw/blob/main/CONTRIBUTING.md",
            "agents_guide": "https://github.com/openclaw/openclaw/blob/main/AGENTS.md"
        },
        "nexus_enhancements": [
            "Integrated with Nexus maintenance dashboard",
            "Smart LLM routing for cost optimization",
            "Multi-provider fallback support",
            "WhatsApp business integration",
            "Supervisor-managed lifecycle (auto-restart)",
            "Per-user authentication and isolation"
        ]
    }


@router.get("/github-info")
async def get_github_info():
    """
    Get latest info about OpenClaw GitHub repository
    """
    return {
        "repository": {
            "url": "https://github.com/openclaw/openclaw",
            "name": "openclaw/openclaw",
            "description": "Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞",
            "stars": "345k+",
            "forks": "68.3k+",
            "watchers": "1.7k+",
            "contributors": "1,467+",
            "commits": "24,527+",
            "latest_version": "2026.4.2",
            "latest_release": "openclaw 2026.4.1",
            "license": "MIT"
        },
        "tech_stack": {
            "primary": "TypeScript (89.3%)",
            "mobile": ["Swift (6.1%)", "Kotlin (1.6%)"],
            "web": "JavaScript (1.2%)",
            "scripting": "Shell (1.1%)",
            "styling": "CSS (0.4%)"
        },
        "key_features": [
            "Multi-platform AI assistant (macOS, Linux, Windows, iOS, Android)",
            "MCP (Model Context Protocol) integration",
            "Browser automation and extensions",
            "File system and shell access",
            "Agent-based workflows (ClawFlow)",
            "Voice wake support",
            "Skills and extensions system",
            "Docker and sandbox support"
        ],
        "recent_updates": [
            "fix(matrix): package verification bootstrap runtime",
            "Refactor channel approval capability seams",
            "chore: bump version to 2026.4.2",
            "ClawFlow: add runtime substrate"
        ],
        "community": {
            "active_development": True,
            "last_commit": "16 minutes ago (Apr 1, 2026)",
            "sponsor_program": "Available",
            "discord": "Active community",
            "contributing_guide": "https://github.com/openclaw/openclaw/blob/main/CONTRIBUTING.md"
        }
    }


@router.get("/docs/mcp-protocol")
async def get_mcp_documentation():
    """
    Get MCP (Model Context Protocol) documentation
    OpenClaw implements the MCP standard for AI agent communication
    """
    return {
        "mcp_protocol": {
            "name": "Model Context Protocol",
            "description": "Standardized protocol for AI agents to communicate with tools and services",
            "openclaw_implementation": "Native MCP support for connecting AI models to external tools"
        },
        "features": [
            "Standardized tool/resource definitions",
            "Streaming support for real-time responses",
            "Multi-agent coordination",
            "Secure credential management",
            "Context preservation across sessions"
        ],
        "use_cases": [
            "File system operations",
            "Browser automation",
            "API integrations",
            "Database queries",
            "Shell command execution",
            "Code generation and editing"
        ],
        "nexus_integration": {
            "status": "Active",
            "gateway_port": 18789,
            "control_port": 18791,
            "protocol": "WebSocket + HTTP",
            "authentication": "Token-based (per-user)"
        }
    }


def get_openclaw_router():
    """Get the OpenClaw router"""
    return router
