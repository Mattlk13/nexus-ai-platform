"""
GitHub MCP API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging

from services.mcp.github_mcp import get_github_mcp

logger = logging.getLogger(__name__)


class CreateRepoRequest(BaseModel):
    name: str
    description: Optional[str] = None
    private: bool = True


class CreateIssueRequest(BaseModel):
    owner: str
    repo: str
    title: str
    body: Optional[str] = None
    labels: Optional[List[str]] = None


def get_github_mcp_router():
    """Get GitHub MCP router"""
    router = APIRouter(prefix="/api/mcp/github", tags=["mcp-github"])
    
    github = get_github_mcp()
    
    @router.get("/user")
    async def get_user():
        """Get authenticated user info"""
        result = await github.get_user()
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    @router.get("/repositories")
    async def list_repositories(username: Optional[str] = None):
        """List user repositories"""
        result = await github.list_repositories(username)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    @router.post("/repositories")
    async def create_repository(request: CreateRepoRequest):
        """Create a new repository"""
        result = await github.create_repository(
            request.name,
            request.description,
            request.private
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    @router.get("/repositories/{owner}/{repo}")
    async def get_repository(owner: str, repo: str):
        """Get repository details"""
        result = await github.get_repository(owner, repo)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    
    @router.post("/issues")
    async def create_issue(request: CreateIssueRequest):
        """Create an issue"""
        result = await github.create_issue(
            request.owner,
            request.repo,
            request.title,
            request.body,
            request.labels
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    @router.get("/issues/{owner}/{repo}")
    async def list_issues(owner: str, repo: str, state: str = "open"):
        """List repository issues"""
        result = await github.list_issues(owner, repo, state)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    @router.get("/search")
    async def search_repositories(q: str, sort: str = "stars"):
        """Search GitHub repositories"""
        result = await github.search_repositories(q, sort)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    
    @router.get("/status")
    async def github_status():
        """Get GitHub MCP status"""
        return {
            "status": "connected",
            "mode": "REAL_GITHUB",
            "tools": [
                "get_user",
                "list_repositories",
                "create_repository",
                "get_repository",
                "create_issue",
                "list_issues",
                "search_repositories"
            ],
            "authenticated": True
        }
    
    return router
