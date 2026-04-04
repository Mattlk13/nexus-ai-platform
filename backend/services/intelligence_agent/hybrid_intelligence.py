"""
Hybrid Intelligence Orchestrator
Combines Tavily, Exa, and Firecrawl for comprehensive business intelligence
"""
import logging
from typing import Dict, List, Optional, Any
import asyncio
from .tavily_service import TavilyService
from .exa_service import ExaService
from .firecrawl_service import FirecrawlService

logger = logging.getLogger(__name__)


class HybridIntelligence:
    def __init__(self):
        self.tavily = TavilyService()
        self.exa = ExaService()
        self.firecrawl = FirecrawlService()
    
    async def marketing_competitive_analysis(self, competitor_name: str) -> Dict[str, Any]:
        """
        Full competitive analysis combining multiple sources
        
        Args:
            competitor_name: Competitor platform/company name
        """
        logger.info(f"Running competitive analysis for: {competitor_name}")
        
        # Run searches in parallel
        tavily_task = self.tavily.search(
            f"{competitor_name} features pricing business model strategy",
            max_results=5,
            search_depth="advanced"
        )
        
        exa_task = self.exa.research_company(competitor_name)
        
        tavily_results, exa_results = await asyncio.gather(
            tavily_task, exa_task,
            return_exceptions=True
        )
        
        return {
            "competitor": competitor_name,
            "tavily_insights": tavily_results if not isinstance(tavily_results, Exception) else {"error": str(tavily_results)},
            "exa_insights": exa_results if not isinstance(exa_results, Exception) else {"error": str(exa_results)},
            "analysis_type": "competitive_analysis"
        }
    
    async def trend_analysis(self, topic: str, industry: str = "creator economy") -> Dict[str, Any]:
        """
        Comprehensive trend analysis
        
        Args:
            topic: Trend topic to analyze
            industry: Industry context
        """
        logger.info(f"Analyzing trends for: {topic} in {industry}")
        
        # Deep research with Tavily
        research = await self.tavily.research(
            f"{topic} trends in {industry} 2026",
            max_results=10
        )
        
        # Find latest news with Exa
        news = await self.exa.search(
            f"{topic} {industry} news trends latest",
            num_results=10,
            category="news"
        )
        
        return {
            "topic": topic,
            "industry": industry,
            "research": research,
            "latest_news": news,
            "analysis_type": "trend_analysis"
        }
    
    async def creator_research(self, creator_name: str) -> Dict[str, Any]:
        """
        Deep research on a creator
        
        Args:
            creator_name: Creator/influencer name
        """
        logger.info(f"Researching creator: {creator_name}")
        
        # Use Exa for person research
        exa_results = await self.exa.research_person(creator_name)
        
        # Use Tavily for broader context
        tavily_results = await self.tavily.search(
            f"{creator_name} content platform audience monetization",
            max_results=5
        )
        
        return {
            "creator": creator_name,
            "profile": exa_results,
            "context": tavily_results,
            "analysis_type": "creator_research"
        }
    
    async def market_opportunity_analysis(self, niche: str) -> Dict[str, Any]:
        """
        Analyze market opportunities in a niche
        
        Args:
            niche: Market niche to analyze
        """
        logger.info(f"Analyzing market opportunity in: {niche}")
        
        # Research with Tavily
        market_research = await self.tavily.research(
            f"{niche} market size growth opportunities trends 2026",
            max_results=10
        )
        
        # Find companies/players with Exa
        players = await self.exa.search(
            f"{niche} startups companies platforms",
            num_results=10,
            category="company"
        )
        
        return {
            "niche": niche,
            "market_research": market_research,
            "key_players": players,
            "analysis_type": "market_opportunity"
        }
    
    async def extract_competitor_data(self, competitor_url: str) -> Dict[str, Any]:
        """
        Extract structured data from competitor website
        
        Args:
            competitor_url: Competitor website URL
        """
        logger.info(f"Extracting data from: {competitor_url}")
        
        # Scrape with Firecrawl
        scraped = await self.firecrawl.scrape(
            competitor_url,
            formats=['markdown', 'html', 'links']
        )
        
        # Map the site structure
        site_map = await self.firecrawl.map(competitor_url, limit=50)
        
        return {
            "url": competitor_url,
            "scraped_content": scraped,
            "site_structure": site_map,
            "analysis_type": "data_extraction"
        }
    
    async def content_discovery(self, topic: str, content_type: str = "articles") -> Dict[str, Any]:
        """
        Discover trending content on a topic
        
        Args:
            topic: Content topic
            content_type: Type of content to find
        """
        logger.info(f"Discovering {content_type} about: {topic}")
        
        # Search with Firecrawl
        firecrawl_results = await self.firecrawl.search(
            f"{topic} {content_type}",
            limit=10
        )
        
        # Cross-reference with Exa
        exa_results = await self.exa.search(
            f"{topic} {content_type}",
            num_results=10
        )
        
        return {
            "topic": topic,
            "content_type": content_type,
            "firecrawl_results": firecrawl_results,
            "exa_results": exa_results,
            "analysis_type": "content_discovery"
        }
    
    async def advertising_intelligence(self, platform: str) -> Dict[str, Any]:
        """
        Research advertising strategies and revenue models
        
        Args:
            platform: Platform to analyze
        """
        logger.info(f"Analyzing advertising intelligence for: {platform}")
        
        research = await self.tavily.research(
            f"{platform} advertising revenue model monetization strategy 2026",
            max_results=10
        )
        
        return {
            "platform": platform,
            "advertising_intel": research,
            "analysis_type": "advertising_intelligence"
        }
    
    async def investment_research(self, sector: str) -> Dict[str, Any]:
        """
        Research investment trends and funding in a sector
        
        Args:
            sector: Industry sector
        """
        logger.info(f"Researching investment trends in: {sector}")
        
        # Research funding trends
        funding = await self.tavily.search(
            f"{sector} venture capital funding investments 2026 trends",
            max_results=10,
            search_depth="advanced"
        )
        
        # Find funded companies
        companies = await self.exa.search(
            f"{sector} startups funding series A B C",
            num_results=10,
            category="company"
        )
        
        return {
            "sector": sector,
            "funding_trends": funding,
            "funded_companies": companies,
            "analysis_type": "investment_research"
        }
    
    async def ask_intelligence(self, question: str) -> Dict[str, Any]:
        """
        General intelligence query - routes to best service(s)
        
        Args:
            question: Any business intelligence question
        """
        logger.info(f"General intelligence query: {question}")
        
        # Use Tavily research for comprehensive answer
        answer = await self.tavily.research(question, max_results=10)
        
        return {
            "question": question,
            "answer": answer,
            "analysis_type": "general_inquiry"
        }
