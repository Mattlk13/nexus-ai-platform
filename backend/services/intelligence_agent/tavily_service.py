"""
Tavily AI Service - Fast research and trend analysis
Free tier: 1,000 requests/month
"""
import httpx
import logging
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')
TAVILY_BASE_URL = 'https://api.tavily.com'


class TavilyService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or TAVILY_API_KEY
        self.base_url = TAVILY_BASE_URL
    
    async def search(self, query: str, max_results: int = 5, search_depth: str = "advanced") -> Dict[str, Any]:
        """
        Fast web search optimized for AI
        
        Args:
            query: Search query
            max_results: Number of results (default 5)
            search_depth: 'basic' or 'advanced'
        """
        if not self.api_key:
            return {"error": "Tavily API key not configured", "results": []}
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=headers,
                    json={
                        "query": query,
                        "max_results": max_results,
                        "search_depth": search_depth,
                        "include_answer": "basic",
                        "include_raw_content": False
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Tavily search failed: {response.status_code}")
                    return {"error": f"Search failed: {response.status_code}", "results": []}
                    
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return {"error": str(e), "results": []}
    
    async def research(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Deep research with multiple sources and citations
        
        Args:
            query: Research topic
            max_results: Number of sources to analyze
        """
        if not self.api_key:
            return {
                "error": "Tavily API key not configured",
                "answer": None,
                "sources": []
            }
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",  # Use /search endpoint
                    headers=headers,
                    json={
                        "query": query,
                        "max_results": max_results,
                        "include_answer": "advanced",
                        "search_depth": "advanced",
                        "include_domains": [],
                        "exclude_domains": []
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"Research failed: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Tavily research error: {e}")
            return {"error": str(e)}
    
    async def extract(self, urls: List[str]) -> Dict[str, Any]:
        """
        Extract content from URLs
        
        Args:
            urls: List of URLs to extract content from
        """
        if not self.api_key:
            return {"error": "Tavily API key not configured", "results": []}
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/extract",
                    headers=headers,
                    json={
                        "urls": urls
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"Extract failed: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Tavily extract error: {e}")
            return {"error": str(e)}
