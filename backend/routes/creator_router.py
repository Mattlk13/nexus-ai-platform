"""
Creator Platform API Routes - Full Implementation
Endpoints for creator profiles, marketplace, recommendations, and revenue analytics
"""
from fastapi import APIRouter, HTTPException, Request, Query
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
from uuid import uuid4

from services.creator import (
    CreatorService,
    MarketplaceService,
    RecommendationEngine,
    RevenueService
)

import logging
logger = logging.getLogger(__name__)


def get_creator_router():
    """Get creator platform router with full implementation"""
    router = APIRouter(prefix="/api/creator", tags=["creator"])
    
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Initialize services
    creator_service = CreatorService(db)
    marketplace_service = MarketplaceService(db)
    recommendation_engine = RecommendationEngine(db)
    revenue_service = RevenueService(db)
    
    # Helper to get user_id from request
    def get_user_id(request: Request) -> str:
        return getattr(request.state, 'user_id', 'demo_user')
    
    # ============== Status & Health ==============
    
    @router.get("/status")
    async def creator_platform_status():
        """Creator platform status check"""
        return {
            "status": "active",
            "features": {
                "profiles": "available",
                "portfolio": "available",
                "marketplace_search": "available",
                "ai_recommendations": "available",
                "revenue_analytics": "available"
            },
            "version": "1.0.0"
        }
    
    # ============== Creator Profile Endpoints ==============
    
    @router.post("/profile")
    async def create_creator_profile(profile_data: dict, request: Request):
        """Create a new creator profile"""
        user_id = get_user_id(request)
        
        try:
            profile = await creator_service.create_profile(user_id, profile_data)
            return {"success": True, "profile": profile}
        except Exception as e:
            logger.error(f"Profile creation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/profile/{user_id}")
    async def get_creator_profile(user_id: str):
        """Get creator profile by user ID"""
        profile = await creator_service.get_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return profile
    
    @router.get("/profile")
    async def get_my_profile(request: Request):
        """Get current user's creator profile"""
        user_id = get_user_id(request)
        profile = await creator_service.get_profile(user_id)
        
        if not profile:
            # Return empty profile structure
            return {
                "user_id": user_id,
                "display_name": "",
                "bio": "",
                "portfolio_items": [],
                "skills": [],
                "social_links": {},
                "is_verified": False
            }
        
        return profile
    
    @router.put("/profile")
    async def update_creator_profile(updates: dict, request: Request):
        """Update creator profile"""
        user_id = get_user_id(request)
        
        try:
            profile = await creator_service.update_profile(user_id, updates)
            return {"success": True, "profile": profile}
        except Exception as e:
            logger.error(f"Profile update failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/profiles")
    async def list_creators(limit: int = Query(50, le=100)):
        """List all creator profiles"""
        creators = await creator_service.get_all_creators(limit)
        return {"creators": creators, "count": len(creators)}
    
    # ============== Portfolio Endpoints ==============
    
    @router.post("/portfolio/item")
    async def add_portfolio_item(item_data: dict, request: Request):
        """Add item to creator's portfolio"""
        user_id = get_user_id(request)
        
        try:
            item = await creator_service.add_portfolio_item(user_id, item_data)
            return {"success": True, "item": item}
        except Exception as e:
            logger.error(f"Portfolio item addition failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.delete("/portfolio/item/{item_id}")
    async def delete_portfolio_item(item_id: str, request: Request):
        """Remove item from portfolio"""
        user_id = get_user_id(request)
        
        success = await creator_service.remove_portfolio_item(user_id, item_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {"success": True, "message": "Item removed"}
    
    # ============== Marketplace Search Endpoints ==============
    
    @router.get("/marketplace/search")
    async def search_marketplace(
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        rating_min: Optional[float] = None,
        sort_by: str = "relevance",
        tags: str = "",
        limit: int = Query(50, le=100)
    ):
        """Enhanced marketplace search with filters"""
        
        tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
        
        try:
            tools = await marketplace_service.search_tools(
                query=query,
                category=category,
                min_price=min_price,
                max_price=max_price,
                rating_min=rating_min,
                sort_by=sort_by,
                tags=tag_list,
                limit=limit
            )
            
            return {
                "tools": tools,
                "count": len(tools),
                "filters_applied": {
                    "query": query,
                    "category": category,
                    "price_range": [min_price, max_price],
                    "min_rating": rating_min,
                    "sort_by": sort_by,
                    "tags": tag_list
                }
            }
        except Exception as e:
            logger.error(f"Marketplace search failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/marketplace/trending")
    async def get_trending_tools(limit: int = Query(10, le=50)):
        """Get trending AI tools"""
        try:
            tools = await marketplace_service.get_trending_tools(limit)
            return {"tools": tools, "count": len(tools)}
        except Exception as e:
            logger.error(f"Trending tools fetch failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/marketplace/categories")
    async def get_categories():
        """Get all available categories"""
        try:
            categories = await marketplace_service.get_categories()
            return {"categories": categories, "count": len(categories)}
        except Exception as e:
            logger.error(f"Categories fetch failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ============== AI Recommendations Endpoints ==============
    
    @router.get("/recommendations")
    async def get_tool_recommendations(request: Request, limit: int = Query(10, le=20)):
        """Get personalized AI tool recommendations"""
        user_id = get_user_id(request)
        
        try:
            recommendations = await recommendation_engine.get_recommendations(user_id, limit)
            
            return {
                "recommendations": recommendations,
                "count": len(recommendations),
                "personalized": True,
                "user_id": user_id
            }
        except Exception as e:
            logger.error(f"Recommendations fetch failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/preferences")
    async def update_user_preferences(preferences: dict, request: Request):
        """Update user preferences for recommendations"""
        user_id = get_user_id(request)
        
        try:
            updated = await recommendation_engine.update_preferences(user_id, preferences)
            return {"success": True, "preferences": updated}
        except Exception as e:
            logger.error(f"Preferences update failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/track-interaction/{tool_id}")
    async def track_tool_interaction(tool_id: str, request: Request):
        """Track user interaction with a tool"""
        user_id = get_user_id(request)
        
        try:
            await recommendation_engine.track_interaction(user_id, tool_id)
            return {"success": True, "message": "Interaction tracked"}
        except Exception as e:
            logger.error(f"Interaction tracking failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ============== Revenue Analytics Endpoints ==============
    
    @router.get("/revenue/analytics")
    async def get_revenue_analytics(
        request: Request,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None
    ):
        """Get comprehensive revenue analytics"""
        user_id = get_user_id(request)
        
        try:
            analytics = await revenue_service.get_creator_revenue(
                user_id,
                period_start,
                period_end
            )
            return analytics
        except Exception as e:
            logger.error(f"Revenue analytics fetch failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/revenue/metrics")
    async def get_revenue_metrics(request: Request):
        """Get detailed revenue metrics"""
        user_id = get_user_id(request)
        
        try:
            metrics = await revenue_service.get_revenue_metrics(user_id)
            return metrics
        except Exception as e:
            logger.error(f"Revenue metrics fetch failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ============== Demo Data Seeding ==============
    
    @router.post("/seed-demo-data")
    async def seed_demo_data():
        """Seed demo data for testing"""
        
        try:
            # Create demo tools
            demo_tools = [
                {
                    "id": f"tool-{i}",
                    "name": name,
                    "description": desc,
                    "category": cat,
                    "price": price,
                    "rating": rating,
                    "total_reviews": reviews,
                    "tags": tags,
                    "creator_id": creator,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "is_trending": trending
                }
                for i, (name, desc, cat, price, rating, reviews, tags, creator, trending) in enumerate([
                    ("AI Content Generator", "Generate high-quality content using advanced AI", "Content Creation", 29.99, 4.8, 156, ["ai", "content", "writing"], "creator-1", True),
                    ("Image AI Studio", "Create stunning images with AI-powered tools", "Design", 49.99, 4.9, 203, ["ai", "images", "design"], "creator-2", True),
                    ("Code Assistant Pro", "AI-powered coding assistant", "Development", 39.99, 4.7, 189, ["ai", "code", "dev"], "creator-1", False),
                    ("Data Analyzer AI", "Analyze data and generate insights", "Analytics", 59.99, 4.6, 98, ["ai", "data", "analytics"], "creator-3", False),
                    ("SEO Optimizer", "Optimize content for search engines", "Marketing", 34.99, 4.5, 142, ["ai", "seo", "marketing"], "creator-2", True),
                ], 1)
            ]
            
            for tool in demo_tools:
                await db.ai_tools.update_one({"id": tool["id"]}, {"$set": tool}, upsert=True)
            
            # Create demo transactions
            demo_transactions = [
                {
                    "id": f"txn-{i}",
                    "buyer_id": f"user-{i}",
                    "seller_id": "demo_user",
                    "tool_id": f"tool-{(i % 3) + 1}",
                    "amount": [29.99, 39.99, 29.99][i % 3],
                    "currency": "USD",
                    "status": "completed",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                for i in range(1, 6)
            ]
            
            for txn in demo_transactions:
                await db.transactions.update_one({"id": txn["id"]}, {"$set": txn}, upsert=True)
            
            return {
                "success": True,
                "message": "Demo data seeded successfully",
                "tools_created": len(demo_tools),
                "transactions_created": len(demo_transactions)
            }
        except Exception as e:
            logger.error(f"Demo data seeding failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
