"""
Firecrawl Service - Content scraping and extraction
Free tier: 500 credits (one-time)
"""
import httpx
import logging
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY', '')
FIRECRAWL_BASE_URL = 'https://api.firecrawl.dev/v1'


class FirecrawlService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or FIRECRAWL_API_KEY
        self.base_url = FIRECRAWL_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    async def scrape(self, url: str, formats: List[str] = None) -> Dict[str, Any]:
        """
        Scrape a single URL
        
        Args:
            url: URL to scrape
            formats: Output formats - ['markdown', 'html', 'rawHtml', 'screenshot', 'links']
        """
        if not self.api_key:
            return {"error": "Firecrawl API key not configured", "success": False}
        
        if formats is None:
            formats = ['markdown', 'html']
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/scrape",
                    headers=self.headers,
                    json={
                        "url": url,
                        "formats": formats,
                        "onlyMainContent": True,
                        "waitFor": 0
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Firecrawl scrape failed: {response.status_code}")
                    return {"error": f"Scrape failed: {response.status_code}", "success": False}
                    
        except Exception as e:
            logger.error(f"Firecrawl scrape error: {e}")
            return {"error": str(e), "success": False}
    
    async def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search the web and optionally scrape results
        
        Args:
            query: Search query
            limit: Max number of results
        """
        if not self.api_key:
            return {"error": "Firecrawl API key not configured", "success": False}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json={
                        "query": query,
                        "limit": limit,
                        "scrapeOptions": {
                            "formats": ["markdown"],
                            "onlyMainContent": True
                        }
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"Search failed: {response.status_code}", "success": False}
                    
        except Exception as e:
            logger.error(f"Firecrawl search error: {e}")
            return {"error": str(e), "success": False}
    
    async def map(self, url: str, limit: int = 100) -> Dict[str, Any]:
        """
        Map a website to discover URLs
        
        Args:
            url: Base URL to map
            limit: Max URLs to discover
        """
        if not self.api_key:
            return {"error": "Firecrawl API key not configured", "success": False}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/map",
                    headers=self.headers,
                    json={
                        "url": url,
                        "limit": limit
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"Map failed: {response.status_code}", "success": False}
                    
        except Exception as e:
            logger.error(f"Firecrawl map error: {e}")
            return {"error": str(e), "success": False}
    
    async def crawl(self, url: str, max_depth: int = 2, limit: int = 100) -> Dict[str, Any]:
        """
        Crawl a website recursively
        
        Args:
            url: Starting URL
            max_depth: Maximum crawl depth
            limit: Max pages to crawl
        """
        if not self.api_key:
            return {"error": "Firecrawl API key not configured", "success": False}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/crawl",
                    headers=self.headers,
                    json={
                        "url": url,
                        "maxDepth": max_depth,
                        "limit": limit,
                        "scrapeOptions": {
                            "formats": ["markdown"],
                            "onlyMainContent": True
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"Crawl failed: {response.status_code}", "success": False}
                    
        except Exception as e:
            logger.error(f"Firecrawl crawl error: {e}")
            return {"error": str(e), "success": False}
