"""
Automated Discovery Service
Searches, scrapes, and catalogs integrations, tools, APIs, AI services, and MCP servers
"""
import logging
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime, timezone
import re
from ..intelligence_agent.exa_service import ExaService
from ..intelligence_agent.tavily_service import TavilyService
from ..intelligence_agent.firecrawl_service import FirecrawlService

logger = logging.getLogger(__name__)


class DiscoveryEngine:
    def __init__(self):
        self.exa = ExaService()
        self.tavily = TavilyService()
        self.firecrawl = FirecrawlService()
    
    async def discover_apis(self, query: str, category: str = "general") -> Dict[str, Any]:
        """
        Discover APIs based on search query
        
        Args:
            query: Search query (e.g., "payment APIs", "AI image generation")
            category: Category filter (payment, ai, communication, etc.)
        """
        logger.info(f"Discovering APIs: {query}")
        
        # Search with Exa for high-quality results
        exa_results = await self.exa.search(
            query=f"{query} API documentation features pricing",
            num_results=15,
            search_type="deep"
        )
        
        # Extract and enrich results
        discovered = []
        results = exa_results.get('results', [])
        
        for result in results:
            resource = {
                "name": self._extract_name(result.get('title', '')),
                "url": result.get('url', ''),
                "description": result.get('text', '')[:300] if result.get('text') else '',
                "highlights": result.get('highlights', []),
                "category": category,
                "type": "api",
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "source": "exa"
            }
            discovered.append(resource)
        
        return {
            "query": query,
            "category": category,
            "total_found": len(discovered),
            "resources": discovered
        }
    
    async def discover_ai_services(self, query: str) -> Dict[str, Any]:
        """
        Discover AI services and models
        
        Args:
            query: AI service type (e.g., "image generation", "text to speech")
        """
        logger.info(f"Discovering AI services: {query}")
        
        # Use Exa for AI-focused search
        results = await self.exa.search(
            query=f"{query} AI API service provider pricing models",
            num_results=20,
            search_type="deep"
        )
        
        ai_services = []
        for result in results.get('results', []):
            service = {
                "name": self._extract_name(result.get('title', '')),
                "url": result.get('url', ''),
                "description": result.get('text', '')[:300] if result.get('text') else '',
                "type": "ai_service",
                "category": self._categorize_ai_service(result.get('title', '')),
                "discovered_at": datetime.now(timezone.utc).isoformat()
            }
            ai_services.append(service)
        
        return {
            "query": query,
            "total_found": len(ai_services),
            "services": ai_services
        }
    
    async def discover_mcp_servers(self) -> Dict[str, Any]:
        """
        Discover MCP (Model Context Protocol) servers
        """
        logger.info("Discovering MCP servers")
        
        # Search for MCP servers
        results = await self.exa.search(
            query="MCP server Model Context Protocol integration tools",
            num_results=25,
            search_type="deep"
        )
        
        mcp_servers = []
        for result in results.get('results', []):
            server = {
                "name": self._extract_name(result.get('title', '')),
                "url": result.get('url', ''),
                "description": result.get('text', '')[:300] if result.get('text') else '',
                "type": "mcp_server",
                "discovered_at": datetime.now(timezone.utc).isoformat()
            }
            mcp_servers.append(server)
        
        return {
            "total_found": len(mcp_servers),
            "servers": mcp_servers
        }
    
    async def scrape_resource_details(self, url: str) -> Dict[str, Any]:
        """
        Scrape detailed information from a resource URL
        
        Args:
            url: Resource URL to scrape
        """
        logger.info(f"Scraping resource details: {url}")
        
        # Use Firecrawl to scrape the page
        scraped = await self.firecrawl.scrape(
            url=url,
            formats=['markdown', 'links']
        )
        
        if not scraped.get('success'):
            return {"error": "Failed to scrape resource", "url": url}
        
        data = scraped.get('data', {})
        content = data.get('markdown', '')
        
        # Extract key information
        details = {
            "url": url,
            "title": data.get('title', ''),
            "content": content[:5000],  # First 5000 chars
            "pricing": self._extract_pricing(content),
            "features": self._extract_features(content),
            "api_endpoints": self._extract_endpoints(content),
            "authentication": self._extract_auth_methods(content),
            "links": data.get('links', [])[:20],
            "scraped_at": datetime.now(timezone.utc).isoformat()
        }
        
        return details
    
    async def discover_and_scrape(self, query: str, resource_type: str = "api") -> Dict[str, Any]:
        """
        Complete discovery + scraping pipeline
        
        Args:
            query: Search query
            resource_type: Type of resource (api, ai_service, tool, mcp_server)
        """
        logger.info(f"Full discovery pipeline for: {query} ({resource_type})")
        
        # Discover resources
        if resource_type == "api":
            discovery = await self.discover_apis(query)
        elif resource_type == "ai_service":
            discovery = await self.discover_ai_services(query)
        elif resource_type == "mcp_server":
            discovery = await self.discover_mcp_servers()
        else:
            discovery = await self.discover_apis(query)
        
        resources = discovery.get('resources', discovery.get('services', discovery.get('servers', [])))
        
        # Scrape top 5 results for detailed info
        enriched = []
        for resource in resources[:5]:
            url = resource.get('url')
            if url:
                try:
                    details = await self.scrape_resource_details(url)
                    resource['details'] = details
                except Exception as e:
                    logger.error(f"Failed to scrape {url}: {e}")
                    resource['details'] = {"error": str(e)}
            
            enriched.append(resource)
        
        return {
            "query": query,
            "resource_type": resource_type,
            "total_discovered": len(resources),
            "enriched_results": enriched,
            "all_results": resources
        }
    
    # ============== Helper Methods ==============
    
    def _extract_name(self, title: str) -> str:
        """Extract clean name from title"""
        # Remove common suffixes
        name = re.sub(r'\s*[-|:–].*$', '', title)
        name = re.sub(r'\s*(API|Documentation|Docs|Home)\s*$', '', name, flags=re.IGNORECASE)
        return name.strip()
    
    def _categorize_ai_service(self, title: str) -> str:
        """Categorize AI service based on title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['image', 'vision', 'picture', 'photo']):
            return 'image_generation'
        elif any(word in title_lower for word in ['text', 'language', 'nlp', 'gpt', 'llm']):
            return 'text_generation'
        elif any(word in title_lower for word in ['voice', 'speech', 'audio', 'tts']):
            return 'voice'
        elif any(word in title_lower for word in ['video']):
            return 'video'
        else:
            return 'general'
    
    def _extract_pricing(self, content: str) -> List[str]:
        """Extract pricing information from content"""
        pricing = []
        
        # Look for pricing patterns
        price_patterns = [
            r'\$[\d,]+(?:\.\d{2})?(?:/(?:month|mo|year|yr|request|call))?',
            r'free tier',
            r'\d+\s+(?:free|credits|requests).*(?:per|/)?\s*(?:month|day)',
        ]
        
        for pattern in price_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                pricing.append(match.group(0))
        
        return pricing[:10]  # Top 10 pricing mentions
    
    def _extract_features(self, content: str) -> List[str]:
        """Extract features from content"""
        features = []
        
        # Look for feature lists (bullet points, numbered lists)
        feature_patterns = [
            r'[•●○▪▫-]\s*(.+?)(?:\n|$)',
            r'\d+\.\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in feature_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                feature = match.group(1).strip()
                if 10 < len(feature) < 200:  # Reasonable feature length
                    features.append(feature)
        
        return features[:15]  # Top 15 features
    
    def _extract_endpoints(self, content: str) -> List[str]:
        """Extract API endpoints from content"""
        endpoints = []
        
        # Look for API endpoint patterns
        endpoint_patterns = [
            r'(?:GET|POST|PUT|DELETE|PATCH)\s+[/\w{}:-]+',
            r'/api/[\w/{}:-]+',
            r'https?://[\w.-]+/[\w/{}:-]+'
        ]
        
        for pattern in endpoint_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                endpoints.append(match.group(0))
        
        return list(set(endpoints))[:20]  # Unique endpoints, max 20
    
    def _extract_auth_methods(self, content: str) -> List[str]:
        """Extract authentication methods"""
        auth_keywords = [
            'API key', 'Bearer token', 'OAuth', 'JWT', 'Basic Auth',
            'Authentication', 'Authorization', 'Access token'
        ]
        
        found_methods = []
        content_lower = content.lower()
        
        for keyword in auth_keywords:
            if keyword.lower() in content_lower:
                found_methods.append(keyword)
        
        return found_methods
