"""
Exa AI Service - AI-native search for creators and companies
Free tier: 1,000 requests/month
"""
import httpx
import logging
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)

EXA_API_KEY = os.getenv('EXA_API_KEY', '')
EXA_BASE_URL = 'https://api.exa.ai'


class ExaService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or EXA_API_KEY
        self.base_url = EXA_BASE_URL
        self.headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    async def search(self, query: str, num_results: int = 10, category: Optional[str] = None, search_type: str = "auto") -> Dict[str, Any]:
        """
        AI-native semantic search
        
        Args:
            query: Search query
            num_results: Number of results
            category: Optional category filter ('company', 'person', 'news', 'research paper', etc.)
            search_type: 'auto', 'fast', 'deep', or 'deep-reasoning'
        """
        if not self.api_key:
            return {"error": "Exa API key not configured", "results": []}
        
        try:
            payload = {
                "query": query,
                "num_results": num_results,
                "type": search_type,
                "contents": {
                    "highlights": {
                        "max_characters": 4000
                    }
                }
            }
            
            if category:
                payload["category"] = category
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Exa search failed: {response.status_code} - {response.text}")
                    return {"error": f"Search failed: {response.status_code}", "results": []}
                    
        except Exception as e:
            logger.error(f"Exa search error: {e}")
            return {"error": str(e), "results": []}
    
    async def find_similar(self, url: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Find similar content to a given URL
        
        Args:
            url: Reference URL
            num_results: Number of similar results
        """
        if not self.api_key:
            return {"error": "Exa API key not configured", "results": []}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/findSimilar",
                    headers=self.headers,
                    json={
                        "url": url,
                        "num_results": num_results,
                        "contents": {
                            "highlights": {
                                "max_characters": 4000
                            }
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"Find similar failed: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Exa find similar error: {e}")
            return {"error": str(e)}
    
    async def get_contents(self, urls: List[str]) -> Dict[str, Any]:
        """
        Get full content for specific URLs
        
        Args:
            urls: List of URLs to get content from
        """
        if not self.api_key:
            return {"error": "Exa API key not configured", "results": []}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/contents",
                    headers=self.headers,
                    json={
                        "urls": urls,
                        "text": {
                            "max_characters": 20000
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"Get contents failed: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Exa get contents error: {e}")
            return {"error": str(e)}
    
    async def research_company(self, company_name: str) -> Dict[str, Any]:
        """
        Deep research on a company
        
        Args:
            company_name: Name of company to research
        """
        return await self.search(
            query=f"{company_name}",
            num_results=10,
            category="company",
            search_type="deep"
        )
    
    async def research_person(self, person_name: str) -> Dict[str, Any]:
        """
        Research a person/creator
        
        Args:
            person_name: Name of person to research
        """
        return await self.search(
            query=f"{person_name}",
            num_results=10,
            category="person",
            search_type="deep"
        )
