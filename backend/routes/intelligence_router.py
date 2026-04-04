"""
NEXUS Hybrid Intelligence API
Admin-only business intelligence endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from services.intelligence_agent.hybrid_intelligence import HybridIntelligence

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])

# Initialize hybrid intelligence
intelligence = HybridIntelligence()


class IntelligenceQuery(BaseModel):
    query: str
    context: Optional[str] = None


class CompetitorAnalysisRequest(BaseModel):
    competitor_name: str


class TrendAnalysisRequest(BaseModel):
    topic: str
    industry: str = "creator economy"


class CreatorResearchRequest(BaseModel):
    creator_name: str


class MarketOpportunityRequest(BaseModel):
    niche: str


class DataExtractionRequest(BaseModel):
    url: str


class ContentDiscoveryRequest(BaseModel):
    topic: str
    content_type: str = "articles"


class AdvertisingIntelRequest(BaseModel):
    platform: str


class InvestmentResearchRequest(BaseModel):
    sector: str


# ============== Marketing Intelligence ==============

@router.post("/marketing/competitor-analysis")
async def competitor_analysis(request: CompetitorAnalysisRequest):
    """
    🎯 Comprehensive competitive analysis
    Combines Tavily + Exa for deep competitor insights
    """
    try:
        result = await intelligence.marketing_competitive_analysis(request.competitor_name)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Competitor analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/marketing/advertising-intel")
async def advertising_intelligence(request: AdvertisingIntelRequest):
    """
    💰 Advertising & monetization intelligence
    Research ad strategies and revenue models
    """
    try:
        result = await intelligence.advertising_intelligence(request.platform)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Advertising intelligence failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Trend Analysis ==============

@router.post("/trends/analyze")
async def analyze_trends(request: TrendAnalysisRequest):
    """
    📈 Comprehensive trend analysis
    Real-time market trends with Tavily + Exa
    """
    try:
        result = await intelligence.trend_analysis(request.topic, request.industry)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Trend analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Investment Research ==============

@router.post("/investment/research")
async def investment_research(request: InvestmentResearchRequest):
    """
    💸 Investment & funding research
    Track VC trends and funded companies
    """
    try:
        result = await intelligence.investment_research(request.sector)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Investment research failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/investment/market-opportunity")
async def market_opportunity(request: MarketOpportunityRequest):
    """
    🎯 Market opportunity analysis
    Identify growth opportunities in niches
    """
    try:
        result = await intelligence.market_opportunity_analysis(request.niche)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Market opportunity analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Research & Analytics ==============

@router.post("/research/creator")
async def research_creator(request: CreatorResearchRequest):
    """
    🔍 Creator research
    Deep-dive into creator background and reach
    """
    try:
        result = await intelligence.creator_research(request.creator_name)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Creator research failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research/extract-data")
async def extract_data(request: DataExtractionRequest):
    """
    📊 Data extraction from URLs
    Scrape and structure competitor data
    """
    try:
        result = await intelligence.extract_competitor_data(request.url)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Data extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research/discover-content")
async def discover_content(request: ContentDiscoveryRequest):
    """
    🎨 Content discovery
    Find trending content on any topic
    """
    try:
        result = await intelligence.content_discovery(request.topic, request.content_type)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Content discovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== General Intelligence ==============

@router.post("/ask")
async def ask_intelligence(request: IntelligenceQuery):
    """
    💡 Ask anything
    General business intelligence query
    """
    try:
        result = await intelligence.ask_intelligence(request.query)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Intelligence query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== API Status ==============

@router.get("/status")
async def get_intelligence_status():
    """
    Get status of all intelligence services
    """
    return {
        "services": {
            "tavily": {
                "name": "Tavily AI",
                "status": "configured" if intelligence.tavily.api_key else "not_configured",
                "features": ["search", "research", "extract"],
                "free_tier": "1,000 requests/month"
            },
            "exa": {
                "name": "Exa AI",
                "status": "configured" if intelligence.exa.api_key else "not_configured",
                "features": ["search", "company_research", "person_research", "find_similar"],
                "free_tier": "1,000 requests/month"
            },
            "firecrawl": {
                "name": "Firecrawl",
                "status": "configured" if intelligence.firecrawl.api_key else "not_configured",
                "features": ["scrape", "search", "map", "crawl"],
                "free_tier": "500 credits (one-time)"
            }
        },
        "hybrid_features": [
            "marketing_competitive_analysis",
            "trend_analysis",
            "creator_research",
            "market_opportunity_analysis",
            "data_extraction",
            "content_discovery",
            "advertising_intelligence",
            "investment_research"
        ]
    }


def get_intelligence_router():
    """Get the intelligence router"""
    return router
