"""
Automated Discovery API Router
Endpoints for discovering and cataloging integrations, tools, APIs, AI services, and MCP servers
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from services.discovery.discovery_engine import DiscoveryEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/discovery", tags=["discovery"])

# Initialize discovery engine
discovery = DiscoveryEngine()


class DiscoveryRequest(BaseModel):
    query: str
    category: Optional[str] = "general"


class ResourceType(BaseModel):
    resource_type: str  # api, ai_service, tool, mcp_server


class ScrapeRequest(BaseModel):
    url: str


class FullDiscoveryRequest(BaseModel):
    query: str
    resource_type: str = "api"


# ============== Discovery Endpoints ==============

@router.post("/apis")
async def discover_apis(request: DiscoveryRequest):
    """
    🔍 Discover APIs
    Search and catalog APIs based on query
    """
    try:
        result = await discovery.discover_apis(request.query, request.category)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"API discovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-services")
async def discover_ai_services(request: DiscoveryRequest):
    """
    🤖 Discover AI Services
    Find AI APIs, models, and services
    """
    try:
        result = await discovery.discover_ai_services(request.query)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"AI service discovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mcp-servers")
async def discover_mcp_servers():
    """
    🔧 Discover MCP Servers
    Find Model Context Protocol servers
    """
    try:
        result = await discovery.discover_mcp_servers()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"MCP server discovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape")
async def scrape_resource(request: ScrapeRequest):
    """
    🕸️ Scrape Resource Details
    Extract detailed information from a resource URL
    """
    try:
        result = await discovery.scrape_resource_details(request.url)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Resource scraping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full-discovery")
async def full_discovery_pipeline(request: FullDiscoveryRequest):
    """
    🚀 Full Discovery Pipeline
    Complete discovery + scraping for resources
    
    - Searches for resources using AI
    - Scrapes top results for detailed info
    - Extracts pricing, features, API endpoints, auth methods
    """
    try:
        result = await discovery.discover_and_scrape(
            request.query,
            request.resource_type
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Full discovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Quick Discovery Presets ==============

@router.get("/presets/payment-apis")
async def discover_payment_apis():
    """
    💳 Discover Payment APIs
    Find payment processing APIs (Stripe, PayPal, etc.)
    """
    try:
        result = await discovery.discover_apis(
            "payment processing APIs Stripe PayPal Square",
            category="payment"
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets/ai-image-generation")
async def discover_ai_image_generation():
    """
    🎨 Discover AI Image Generation APIs
    Find image generation services (DALL-E, Midjourney, Stable Diffusion, etc.)
    """
    try:
        result = await discovery.discover_ai_services(
            "AI image generation text to image"
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets/llm-apis")
async def discover_llm_apis():
    """
    🧠 Discover LLM APIs
    Find language model APIs (OpenAI, Anthropic, Google, etc.)
    """
    try:
        result = await discovery.discover_ai_services(
            "large language model API GPT Claude Gemini"
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets/communication-apis")
async def discover_communication_apis():
    """
    📬 Discover Communication APIs
    Find email, SMS, messaging APIs (Twilio, SendGrid, etc.)
    """
    try:
        result = await discovery.discover_apis(
            "email SMS messaging communication API Twilio SendGrid",
            category="communication"
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Search Categories ==============

@router.get("/categories")
async def get_discovery_categories():
    """
    Get available discovery categories
    """
    categories = [
        {
            "id": "payment",
            "name": "Payment APIs",
            "description": "Payment processing, billing, subscriptions",
            "icon": "💳"
        },
        {
            "id": "ai",
            "name": "AI Services",
            "description": "Machine learning, NLP, computer vision",
            "icon": "🤖"
        },
        {
            "id": "communication",
            "name": "Communication",
            "description": "Email, SMS, messaging, notifications",
            "icon": "📬"
        },
        {
            "id": "storage",
            "name": "Storage & CDN",
            "description": "File storage, CDN, media hosting",
            "icon": "📁"
        },
        {
            "id": "authentication",
            "name": "Authentication",
            "description": "OAuth, SSO, identity management",
            "icon": "🔐"
        },
        {
            "id": "analytics",
            "name": "Analytics",
            "description": "User tracking, metrics, insights",
            "icon": "📊"
        },
        {
            "id": "search",
            "name": "Search APIs",
            "description": "Web search, site search, indexing",
            "icon": "🔍"
        },
        {
            "id": "mcp",
            "name": "MCP Servers",
            "description": "Model Context Protocol servers",
            "icon": "🔧"
        }
    ]
    
    return {"categories": categories}


# ============== Status ==============

@router.get("/status")
async def get_discovery_status():
    """
    Get discovery engine status
    """
    return {
        "status": "operational",
        "services": {
            "exa": "configured" if discovery.exa.api_key else "not_configured",
            "tavily": "configured" if discovery.tavily.api_key else "not_configured",
            "firecrawl": "configured" if discovery.firecrawl.api_key else "not_configured"
        },
        "capabilities": [
            "API discovery",
            "AI service discovery",
            "MCP server discovery",
            "Automated scraping",
            "Pricing extraction",
            "Feature extraction",
            "Endpoint extraction",
            "Auth method detection"
        ]
    }


def get_discovery_router():
    """Get the discovery router"""
    return router
