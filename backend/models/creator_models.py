"""
Creator Platform Models
Database schemas for creator profiles, portfolios, and analytics
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class PortfolioItemType(str, Enum):
    """Types of portfolio items"""
    PROJECT = "project"
    IMAGE = "image"
    VIDEO = "video"
    LINK = "link"
    DOCUMENT = "document"


class PortfolioItem(BaseModel):
    """Individual portfolio item"""
    id: str
    title: str
    description: Optional[str] = None
    type: PortfolioItemType
    thumbnail_url: Optional[str] = None
    media_url: Optional[str] = None
    external_link: Optional[str] = None
    tags: List[str] = []
    created_at: str
    order: int = 0


class CreatorProfile(BaseModel):
    """Creator profile with portfolio"""
    user_id: str
    display_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    skills: List[str] = []
    portfolio_items: List[PortfolioItem] = []
    social_links: Dict[str, str] = {}
    created_at: str
    updated_at: str
    is_verified: bool = False


class MarketplaceFilter(BaseModel):
    """Search and filter options for marketplace"""
    query: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    rating_min: Optional[float] = None
    sort_by: str = "relevance"  # relevance, price_low, price_high, rating, recent
    tags: List[str] = []


class AITool(BaseModel):
    """AI Tool in marketplace"""
    id: str
    name: str
    description: str
    category: str
    price: float
    rating: Optional[float] = None
    total_reviews: int = 0
    thumbnail_url: Optional[str] = None
    tags: List[str] = []
    creator_id: str
    created_at: str
    is_trending: bool = False


class ToolRecommendation(BaseModel):
    """AI-generated tool recommendation"""
    tool_id: str
    tool_name: str
    score: float  # 0-1 relevance score
    reason: str
    matched_preferences: List[str] = []


class UserPreferences(BaseModel):
    """User preferences for recommendations"""
    user_id: str
    interests: List[str] = []
    skill_level: str = "intermediate"  # beginner, intermediate, advanced
    budget_range: str = "mid"  # low, mid, high
    preferred_categories: List[str] = []
    interaction_history: List[str] = []  # tool IDs user has viewed/used
    updated_at: str


class Transaction(BaseModel):
    """Purchase/sale transaction"""
    id: str
    buyer_id: str
    seller_id: str
    tool_id: str
    amount: float
    currency: str = "USD"
    status: str  # pending, completed, refunded
    created_at: str
    completed_at: Optional[str] = None


class RevenueAnalytics(BaseModel):
    """Creator revenue analytics"""
    creator_id: str
    total_revenue: float
    total_sales: int
    avg_sale_value: float
    monthly_revenue: Dict[str, float] = {}  # YYYY-MM: amount
    top_selling_tools: List[Dict[str, Any]] = []
    revenue_by_category: Dict[str, float] = {}
    growth_rate: Optional[float] = None
    period_start: str
    period_end: str


class RevenueMetrics(BaseModel):
    """Detailed revenue metrics"""
    total_earnings: float
    pending_earnings: float
    available_balance: float
    total_transactions: int
    successful_transactions: int
    refunded_transactions: int
    avg_transaction_value: float
    highest_earning_tool: Optional[Dict[str, Any]] = None
    recent_transactions: List[Transaction] = []
