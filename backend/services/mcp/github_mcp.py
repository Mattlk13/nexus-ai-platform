"""
GitHub MCP Integration for NEXUS
Real GitHub operations using GitHub API
"""
import os
import logging
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class GitHubMCP:
    """
    GitHub MCP Server using GitHub API
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub MCP
        
        Args:
            token: GitHub Personal Access Token
        """
        self.token = token or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)
        logger.info("GitHub MCP initialized")
    
    async def get_user(self) -> Dict[str, Any]:
        """Get authenticated user info"""
        try:
            response = await self.client.get(f"{self.api_base}/user")
            response.raise_for_status()
            return {
                "success": True,
                "user": response.json(),
                "mode": "REAL_GITHUB"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_repositories(
        self,
        username: Optional[str] = None,
        visibility: str = "all"
    ) -> Dict[str, Any]:
        """List user repositories"""
        try:
            if username:
                url = f"{self.api_base}/users/{username}/repos"
            else:
                url = f"{self.api_base}/user/repos"
            
            response = await self.client.get(url, params={"visibility": visibility})
            response.raise_for_status()
            repos = response.json()
            
            return {
                "success": True,
                "repositories": [
                    {
                        "name": repo["name"],
                        "full_name": repo["full_name"],
                        "private": repo["private"],
                        "description": repo.get("description"),
                        "url": repo["html_url"],
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"]
                    }
                    for repo in repos
                ],
                "count": len(repos),
                "mode": "REAL_GITHUB"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_repository(
        self,
        name: str,
        description: Optional[str] = None,
        private: bool = True,
        auto_init: bool = True
    ) -> Dict[str, Any]:
        """Create a new repository"""
        try:
            data = {
                "name": name,
                "description": description or f"NEXUS AI Platform - Created {datetime.now(timezone.utc).date()}",
                "private": private,
                "auto_init": auto_init
            }
            
            response = await self.client.post(
                f"{self.api_base}/user/repos",
                json=data
            )
            response.raise_for_status()
            repo = response.json()
            
            return {
                "success": True,
                "repository": {
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "url": repo["html_url"],
                    "clone_url": repo["clone_url"],
                    "private": repo["private"]
                },
                "mode": "REAL_GITHUB"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_repository(
        self,
        owner: str,
        repo: str
    ) -> Dict[str, Any]:
        """Get repository details"""
        try:
            response = await self.client.get(
                f"{self.api_base}/repos/{owner}/{repo}"
            )
            response.raise_for_status()
            repo_data = response.json()
            
            return {
                "success": True,
                "repository": {
                    "name": repo_data["name"],
                    "full_name": repo_data["full_name"],
                    "description": repo_data.get("description"),
                    "private": repo_data["private"],
                    "url": repo_data["html_url"],
                    "clone_url": repo_data["clone_url"],
                    "stars": repo_data["stargazers_count"],
                    "forks": repo_data["forks_count"],
                    "created_at": repo_data["created_at"],
                    "updated_at": repo_data["updated_at"]
                },
                "mode": "REAL_GITHUB"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create an issue"""
        try:
            data = {
                "title": title,
                "body": body or "",
                "labels": labels or []
            }
            
            response = await self.client.post(
                f"{self.api_base}/repos/{owner}/{repo}/issues",
                json=data
            )
            response.raise_for_status()
            issue = response.json()
            
            return {
                "success": True,
                "issue": {
                    "number": issue["number"],
                    "title": issue["title"],
                    "url": issue["html_url"],
                    "state": issue["state"]
                },
                "mode": "REAL_GITHUB"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open"
    ) -> Dict[str, Any]:
        """List repository issues"""
        try:
            response = await self.client.get(
                f"{self.api_base}/repos/{owner}/{repo}/issues",
                params={"state": state}
            )
            response.raise_for_status()
            issues = response.json()
            
            return {
                "success": True,
                "issues": [
                    {
                        "number": issue["number"],
                        "title": issue["title"],
                        "state": issue["state"],
                        "url": issue["html_url"],
                        "created_at": issue["created_at"]
                    }
                    for issue in issues
                ],
                "count": len(issues),
                "mode": "REAL_GITHUB"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def search_repositories(
        self,
        query: str,
        sort: str = "stars"
    ) -> Dict[str, Any]:
        """Search GitHub repositories"""
        try:
            response = await self.client.get(
                f"{self.api_base}/search/repositories",
                params={"q": query, "sort": sort}
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "total_count": data["total_count"],
                "repositories": [
                    {
                        "name": repo["name"],
                        "full_name": repo["full_name"],
                        "description": repo.get("description"),
                        "url": repo["html_url"],
                        "stars": repo["stargazers_count"]
                    }
                    for repo in data["items"][:10]  # Top 10
                ],
                "mode": "REAL_GITHUB"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def cleanup(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton
_github_mcp = None

def get_github_mcp() -> GitHubMCP:
    """Get GitHub MCP singleton"""
    global _github_mcp
    if _github_mcp is None:
        _github_mcp = GitHubMCP()
    return _github_mcp
