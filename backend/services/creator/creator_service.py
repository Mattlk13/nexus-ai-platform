"""
Creator Platform Services
Business logic for creator profiles, portfolios, and recommendations
"""
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from uuid import uuid4
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY", "sk-emergent-a79Ba891bC89777B1C")


class CreatorService:
    """Service for creator profile and portfolio management"""
    
    def __init__(self, db):
        self.db = db
    
    async def create_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new creator profile"""
        profile = {
            "user_id": user_id,
            "display_name": profile_data.get("display_name"),
            "bio": profile_data.get("bio", ""),
            "avatar_url": profile_data.get("avatar_url"),
            "cover_image_url": profile_data.get("cover_image_url"),
            "skills": profile_data.get("skills", []),
            "portfolio_items": [],
            "social_links": profile_data.get("social_links", {}),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "is_verified": False
        }
        
        await self.db.creator_profiles.insert_one(profile)
        # Remove MongoDB _id before returning (not JSON serializable)
        profile.pop("_id", None)
        return profile
    
    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get creator profile by user ID"""
        profile = await self.db.creator_profiles.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        return profile
    
    async def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update creator profile"""
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await self.db.creator_profiles.update_one(
            {"user_id": user_id},
            {"$set": updates}
        )
        
        return await self.get_profile(user_id)
    
    async def add_portfolio_item(
        self,
        user_id: str,
        item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add item to creator's portfolio"""
        item = {
            "id": str(uuid4()),
            "title": item_data.get("title"),
            "description": item_data.get("description"),
            "type": item_data.get("type"),
            "thumbnail_url": item_data.get("thumbnail_url"),
            "media_url": item_data.get("media_url"),
            "external_link": item_data.get("external_link"),
            "tags": item_data.get("tags", []),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "order": item_data.get("order", 0)
        }
        
        await self.db.creator_profiles.update_one(
            {"user_id": user_id},
            {"$push": {"portfolio_items": item}}
        )
        
        return item
    
    async def remove_portfolio_item(self, user_id: str, item_id: str) -> bool:
        """Remove item from portfolio"""
        result = await self.db.creator_profiles.update_one(
            {"user_id": user_id},
            {"$pull": {"portfolio_items": {"id": item_id}}}
        )
        return result.modified_count > 0
    
    async def get_all_creators(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all creator profiles"""
        creators = await self.db.creator_profiles.find(
            {},
            {"_id": 0}
        ).limit(limit).to_list(limit)
        return creators


class MarketplaceService:
    """Service for marketplace search and filtering"""
    
    def __init__(self, db):
        self.db = db
    
    async def search_tools(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        rating_min: Optional[float] = None,
        sort_by: str = "relevance",
        tags: List[str] = [],
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Enhanced marketplace search with filters"""
        
        # Build query
        search_filter = {}
        
        if query:
            search_filter["$or"] = [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"tags": {"$regex": query, "$options": "i"}}
            ]
        
        if category:
            search_filter["category"] = category
        
        if min_price is not None or max_price is not None:
            search_filter["price"] = {}
            if min_price is not None:
                search_filter["price"]["$gte"] = min_price
            if max_price is not None:
                search_filter["price"]["$lte"] = max_price
        
        if rating_min:
            search_filter["rating"] = {"$gte": rating_min}
        
        if tags:
            search_filter["tags"] = {"$in": tags}
        
        # Determine sort order
        sort_order = []
        if sort_by == "price_low":
            sort_order = [("price", 1)]
        elif sort_by == "price_high":
            sort_order = [("price", -1)]
        elif sort_by == "rating":
            sort_order = [("rating", -1)]
        elif sort_by == "recent":
            sort_order = [("created_at", -1)]
        else:  # relevance or default
            sort_order = [("is_trending", -1), ("rating", -1)]
        
        # Execute search
        cursor = self.db.ai_tools.find(search_filter, {"_id": 0})
        
        for field, order in sort_order:
            cursor = cursor.sort(field, order)
        
        tools = await cursor.limit(limit).to_list(limit)
        return tools
    
    async def get_trending_tools(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending tools"""
        tools = await self.db.ai_tools.find(
            {"is_trending": True},
            {"_id": 0}
        ).sort("rating", -1).limit(limit).to_list(limit)
        return tools
    
    async def get_categories(self) -> List[str]:
        """Get all unique categories"""
        categories = await self.db.ai_tools.distinct("category")
        return categories


class RecommendationEngine:
    """AI-powered tool recommendation engine"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get personalized tool recommendations using AI"""
        
        # Get user preferences
        prefs = await self.db.user_preferences.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        if not prefs:
            # Return trending tools for new users
            return await self._get_trending_recommendations(limit)
        
        # Get available tools
        all_tools = await self.db.ai_tools.find({}, {"_id": 0}).limit(100).to_list(100)
        
        # Filter out tools user already interacted with
        interaction_history = set(prefs.get("interaction_history", []))
        candidate_tools = [
            tool for tool in all_tools
            if tool["id"] not in interaction_history
        ]
        
        if not candidate_tools:
            return await self._get_trending_recommendations(limit)
        
        # Use AI to generate recommendations
        recommendations = await self._generate_ai_recommendations(
            prefs,
            candidate_tools,
            limit
        )
        
        return recommendations
    
    async def _get_trending_recommendations(self, limit: int) -> List[Dict[str, Any]]:
        """Fallback: return trending tools"""
        tools = await self.db.ai_tools.find(
            {},
            {"_id": 0}
        ).sort([("is_trending", -1), ("rating", -1)]).limit(limit).to_list(limit)
        
        return [
            {
                "tool_id": tool["id"],
                "tool_name": tool["name"],
                "score": 0.8,
                "reason": "Popular and highly rated tool",
                "matched_preferences": []
            }
            for tool in tools
        ]
    
    async def _generate_ai_recommendations(
        self,
        preferences: Dict[str, Any],
        tools: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Use AI to match tools to user preferences"""
        
        try:
            # Prepare context
            user_context = {
                "interests": preferences.get("interests", []),
                "skill_level": preferences.get("skill_level", "intermediate"),
                "budget_range": preferences.get("budget_range", "mid"),
                "preferred_categories": preferences.get("preferred_categories", [])
            }
            
            tools_summary = [
                {
                    "id": tool["id"],
                    "name": tool["name"],
                    "category": tool["category"],
                    "price": tool["price"],
                    "description": tool["description"][:200],
                    "tags": tool.get("tags", [])
                }
                for tool in tools[:30]  # Limit context size
            ]
            
            prompt = f"""You are an AI recommendation engine. Based on user preferences and available tools, recommend the top {limit} most suitable tools.

User Preferences:
{user_context}

Available Tools:
{tools_summary}

For each recommendation, provide:
1. tool_id
2. score (0-1 relevance)
3. reason (1-2 sentences)
4. matched_preferences (list of matched interests/categories)

Return ONLY a JSON array with {limit} recommendations, ordered by relevance score (highest first)."""

            # Use Emergent LLM
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"recommend-{uuid4()}",
                system_message="You are an expert recommendation engine that matches users with AI tools."
            ).with_model("openai", "gpt-5.1")
            
            response_text = await chat.send_message(UserMessage(text=prompt))
            
            # Parse response
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                
                # Enhance with tool names
                tool_map = {tool["id"]: tool["name"] for tool in tools}
                for rec in recommendations:
                    rec["tool_name"] = tool_map.get(rec["tool_id"], "Unknown")
                
                return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"AI recommendation failed: {e}")
        
        # Fallback to simple matching
        return await self._simple_matching(preferences, tools, limit)
    
    async def _simple_matching(
        self,
        preferences: Dict[str, Any],
        tools: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Simple rule-based matching fallback"""
        
        user_interests = set(preferences.get("interests", []))
        preferred_cats = set(preferences.get("preferred_categories", []))
        
        scored_tools = []
        for tool in tools:
            score = 0.0
            matched = []
            
            # Category match
            if tool["category"] in preferred_cats:
                score += 0.4
                matched.append(tool["category"])
            
            # Tag/interest match
            tool_tags = set(tool.get("tags", []))
            common_tags = user_interests & tool_tags
            if common_tags:
                score += 0.3 * len(common_tags)
                matched.extend(list(common_tags))
            
            # Rating boost
            if tool.get("rating", 0) >= 4.5:
                score += 0.2
            
            # Trending boost
            if tool.get("is_trending"):
                score += 0.1
            
            scored_tools.append({
                "tool_id": tool["id"],
                "tool_name": tool["name"],
                "score": min(score, 1.0),
                "reason": f"Matches your interests in {', '.join(matched[:3])}" if matched else "Popular tool in relevant category",
                "matched_preferences": matched
            })
        
        # Sort by score and return top N
        scored_tools.sort(key=lambda x: x["score"], reverse=True)
        return scored_tools[:limit]
    
    async def update_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user preferences"""
        pref_doc = {
            "user_id": user_id,
            **preferences,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.db.user_preferences.update_one(
            {"user_id": user_id},
            {"$set": pref_doc},
            upsert=True
        )
        
        return pref_doc
    
    async def track_interaction(self, user_id: str, tool_id: str):
        """Track user interaction with a tool"""
        await self.db.user_preferences.update_one(
            {"user_id": user_id},
            {
                "$addToSet": {"interaction_history": tool_id},
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            },
            upsert=True
        )


class RevenueService:
    """Service for revenue analytics and tracking"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_creator_revenue(
        self,
        creator_id: str,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive revenue analytics for creator"""
        
        # Build time filter
        time_filter = {"seller_id": creator_id, "status": "completed"}
        
        if period_start:
            time_filter["created_at"] = {"$gte": period_start}
        if period_end:
            if "created_at" in time_filter:
                time_filter["created_at"]["$lte"] = period_end
            else:
                time_filter["created_at"] = {"$lte": period_end}
        
        # Get all transactions
        transactions = await self.db.transactions.find(
            time_filter,
            {"_id": 0}
        ).to_list(1000)
        
        if not transactions:
            return self._empty_analytics(creator_id, period_start, period_end)
        
        # Calculate metrics
        total_revenue = sum(t["amount"] for t in transactions)
        total_sales = len(transactions)
        avg_sale_value = total_revenue / total_sales if total_sales > 0 else 0
        
        # Monthly breakdown
        monthly_revenue = {}
        for t in transactions:
            month = t["created_at"][:7]  # YYYY-MM
            monthly_revenue[month] = monthly_revenue.get(month, 0) + t["amount"]
        
        # Top selling tools
        tool_sales = {}
        for t in transactions:
            tool_id = t["tool_id"]
            if tool_id not in tool_sales:
                tool_sales[tool_id] = {"count": 0, "revenue": 0}
            tool_sales[tool_id]["count"] += 1
            tool_sales[tool_id]["revenue"] += t["amount"]
        
        top_tools = sorted(
            [{"tool_id": k, **v} for k, v in tool_sales.items()],
            key=lambda x: x["revenue"],
            reverse=True
        )[:5]
        
        # Revenue by category (would need tool data)
        revenue_by_category = {}
        
        return {
            "creator_id": creator_id,
            "total_revenue": total_revenue,
            "total_sales": total_sales,
            "avg_sale_value": avg_sale_value,
            "monthly_revenue": monthly_revenue,
            "top_selling_tools": top_tools,
            "revenue_by_category": revenue_by_category,
            "growth_rate": self._calculate_growth(monthly_revenue),
            "period_start": period_start or transactions[0]["created_at"] if transactions else "",
            "period_end": period_end or transactions[-1]["created_at"] if transactions else ""
        }
    
    def _empty_analytics(
        self,
        creator_id: str,
        period_start: Optional[str],
        period_end: Optional[str]
    ) -> Dict[str, Any]:
        """Return empty analytics structure"""
        return {
            "creator_id": creator_id,
            "total_revenue": 0.0,
            "total_sales": 0,
            "avg_sale_value": 0.0,
            "monthly_revenue": {},
            "top_selling_tools": [],
            "revenue_by_category": {},
            "growth_rate": 0.0,
            "period_start": period_start or "",
            "period_end": period_end or ""
        }
    
    def _calculate_growth(self, monthly_revenue: Dict[str, float]) -> Optional[float]:
        """Calculate month-over-month growth rate"""
        if len(monthly_revenue) < 2:
            return None
        
        months = sorted(monthly_revenue.keys())
        current = monthly_revenue[months[-1]]
        previous = monthly_revenue[months[-2]]
        
        if previous == 0:
            return None
        
        growth = ((current - previous) / previous) * 100
        return round(growth, 2)
    
    async def get_revenue_metrics(self, creator_id: str) -> Dict[str, Any]:
        """Get detailed revenue metrics"""
        
        # Get all transactions
        all_transactions = await self.db.transactions.find(
            {"seller_id": creator_id},
            {"_id": 0}
        ).to_list(1000)
        
        completed = [t for t in all_transactions if t["status"] == "completed"]
        pending = [t for t in all_transactions if t["status"] == "pending"]
        refunded = [t for t in all_transactions if t["status"] == "refunded"]
        
        total_earnings = sum(t["amount"] for t in completed)
        pending_earnings = sum(t["amount"] for t in pending)
        
        # Get recent transactions
        recent = sorted(
            all_transactions,
            key=lambda x: x["created_at"],
            reverse=True
        )[:10]
        
        # Find highest earning tool
        tool_earnings = {}
        for t in completed:
            tool_id = t["tool_id"]
            tool_earnings[tool_id] = tool_earnings.get(tool_id, 0) + t["amount"]
        
        highest_tool = None
        if tool_earnings:
            top_tool_id = max(tool_earnings, key=tool_earnings.get)
            highest_tool = {
                "tool_id": top_tool_id,
                "earnings": tool_earnings[top_tool_id]
            }
        
        return {
            "total_earnings": total_earnings,
            "pending_earnings": pending_earnings,
            "available_balance": total_earnings * 0.95,  # Assume 5% platform fee
            "total_transactions": len(all_transactions),
            "successful_transactions": len(completed),
            "refunded_transactions": len(refunded),
            "avg_transaction_value": total_earnings / len(completed) if completed else 0,
            "highest_earning_tool": highest_tool,
            "recent_transactions": recent
        }
