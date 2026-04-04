"""
Creator Platform API Tests
Tests for creator profiles, marketplace, recommendations, and revenue analytics
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestCreatorStatus:
    """Creator platform status endpoint tests"""
    
    def test_creator_status(self):
        """Test creator platform status endpoint"""
        response = requests.get(f"{BASE_URL}/api/creator/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "active"
        assert "features" in data
        assert data["features"]["profiles"] == "available"
        assert data["features"]["portfolio"] == "available"
        assert data["features"]["marketplace_search"] == "available"
        assert data["features"]["ai_recommendations"] == "available"
        assert data["features"]["revenue_analytics"] == "available"
        print("✓ Creator status endpoint working")


class TestDemoDataSeeding:
    """Demo data seeding tests"""
    
    def test_seed_demo_data(self):
        """Test demo data seeding endpoint"""
        response = requests.post(f"{BASE_URL}/api/creator/seed-demo-data")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["tools_created"] == 5
        assert data["transactions_created"] == 5
        print("✓ Demo data seeding working")


class TestCreatorProfile:
    """Creator profile CRUD tests"""
    
    def test_get_profile_empty(self):
        """Test getting profile when none exists - should return empty structure"""
        response = requests.get(f"{BASE_URL}/api/creator/profile")
        assert response.status_code == 200
        
        data = response.json()
        assert "user_id" in data
        print("✓ Get profile endpoint working")
    
    def test_create_profile(self):
        """Test creating a creator profile"""
        profile_data = {
            "display_name": "TEST_Creator",
            "bio": "Test creator bio for testing",
            "skills": ["AI", "Python", "Testing"],
            "social_links": {"twitter": "https://twitter.com/test"}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/creator/profile",
            json=profile_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "profile" in data
        assert data["profile"]["display_name"] == "TEST_Creator"
        assert data["profile"]["bio"] == "Test creator bio for testing"
        assert "AI" in data["profile"]["skills"]
        print("✓ Create profile endpoint working")
    
    def test_update_profile(self):
        """Test updating a creator profile"""
        updates = {
            "display_name": "TEST_Updated_Creator",
            "bio": "Updated bio for testing"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/creator/profile",
            json=updates
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["profile"]["display_name"] == "TEST_Updated_Creator"
        print("✓ Update profile endpoint working")
    
    def test_get_profile_by_user_id(self):
        """Test getting profile by specific user ID"""
        response = requests.get(f"{BASE_URL}/api/creator/profile/demo_user")
        # May return 404 if profile doesn't exist for demo_user
        assert response.status_code in [200, 404]
        print("✓ Get profile by user_id endpoint working")
    
    def test_list_creators(self):
        """Test listing all creators"""
        response = requests.get(f"{BASE_URL}/api/creator/profiles?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "creators" in data
        assert "count" in data
        assert isinstance(data["creators"], list)
        print(f"✓ List creators endpoint working - found {data['count']} creators")


class TestPortfolioManagement:
    """Portfolio item management tests"""
    
    def test_add_portfolio_item(self):
        """Test adding a portfolio item"""
        item_data = {
            "title": "TEST_Portfolio_Item",
            "description": "A test portfolio item",
            "type": "project",
            "external_link": "https://example.com/project"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/creator/portfolio/item",
            json=item_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "item" in data
        assert data["item"]["title"] == "TEST_Portfolio_Item"
        assert "id" in data["item"]
        
        # Store item ID for deletion test
        TestPortfolioManagement.test_item_id = data["item"]["id"]
        print(f"✓ Add portfolio item working - created item {data['item']['id']}")
    
    def test_delete_portfolio_item(self):
        """Test deleting a portfolio item"""
        item_id = getattr(TestPortfolioManagement, 'test_item_id', 'nonexistent')
        
        response = requests.delete(f"{BASE_URL}/api/creator/portfolio/item/{item_id}")
        # 200 if found and deleted, 404 if not found
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] == True
            print("✓ Delete portfolio item working")
        else:
            print("✓ Delete portfolio item endpoint accessible (item not found)")


class TestMarketplaceSearch:
    """Marketplace search and filtering tests"""
    
    def test_search_all_tools(self):
        """Test searching all tools without filters"""
        response = requests.get(f"{BASE_URL}/api/creator/marketplace/search")
        assert response.status_code == 200
        
        data = response.json()
        assert "tools" in data
        assert "count" in data
        assert "filters_applied" in data
        print(f"✓ Marketplace search working - found {data['count']} tools")
    
    def test_search_with_query(self):
        """Test searching with a text query"""
        response = requests.get(f"{BASE_URL}/api/creator/marketplace/search?query=AI")
        assert response.status_code == 200
        
        data = response.json()
        assert "tools" in data
        assert data["filters_applied"]["query"] == "AI"
        print(f"✓ Search with query working - found {data['count']} tools matching 'AI'")
    
    def test_search_with_category_filter(self):
        """Test searching with category filter"""
        response = requests.get(f"{BASE_URL}/api/creator/marketplace/search?category=Design")
        assert response.status_code == 200
        
        data = response.json()
        assert "tools" in data
        assert data["filters_applied"]["category"] == "Design"
        print(f"✓ Search with category filter working - found {data['count']} Design tools")
    
    def test_search_with_price_filter(self):
        """Test searching with price range filter"""
        response = requests.get(f"{BASE_URL}/api/creator/marketplace/search?min_price=20&max_price=50")
        assert response.status_code == 200
        
        data = response.json()
        assert "tools" in data
        assert data["filters_applied"]["price_range"] == [20.0, 50.0]
        print(f"✓ Search with price filter working - found {data['count']} tools in price range")
    
    def test_search_with_rating_filter(self):
        """Test searching with minimum rating filter"""
        response = requests.get(f"{BASE_URL}/api/creator/marketplace/search?rating_min=4.5")
        assert response.status_code == 200
        
        data = response.json()
        assert "tools" in data
        assert data["filters_applied"]["min_rating"] == 4.5
        print(f"✓ Search with rating filter working - found {data['count']} highly rated tools")
    
    def test_search_with_sort(self):
        """Test searching with different sort options"""
        for sort_by in ["relevance", "price_low", "price_high", "rating", "recent"]:
            response = requests.get(f"{BASE_URL}/api/creator/marketplace/search?sort_by={sort_by}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["filters_applied"]["sort_by"] == sort_by
        print("✓ Search with all sort options working")
    
    def test_get_trending_tools(self):
        """Test getting trending tools"""
        response = requests.get(f"{BASE_URL}/api/creator/marketplace/trending")
        assert response.status_code == 200
        
        data = response.json()
        assert "tools" in data
        assert "count" in data
        
        # Verify trending tools have is_trending flag
        for tool in data["tools"]:
            assert tool.get("is_trending") == True
        print(f"✓ Trending tools endpoint working - found {data['count']} trending tools")
    
    def test_get_categories(self):
        """Test getting all categories"""
        response = requests.get(f"{BASE_URL}/api/creator/marketplace/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        assert "count" in data
        assert isinstance(data["categories"], list)
        print(f"✓ Categories endpoint working - found {data['count']} categories")


class TestAIRecommendations:
    """AI recommendation engine tests"""
    
    def test_get_recommendations(self):
        """Test getting AI-powered recommendations"""
        response = requests.get(f"{BASE_URL}/api/creator/recommendations?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "recommendations" in data
        assert "count" in data
        assert "personalized" in data
        assert "user_id" in data
        
        # Verify recommendation structure
        for rec in data["recommendations"]:
            assert "tool_id" in rec
            assert "tool_name" in rec
            assert "score" in rec
            assert "reason" in rec
            assert 0 <= rec["score"] <= 1
        print(f"✓ AI recommendations working - got {data['count']} recommendations")
    
    def test_update_preferences(self):
        """Test updating user preferences"""
        preferences = {
            "interests": ["AI", "automation", "content"],
            "skill_level": "intermediate",
            "budget_range": "mid",
            "preferred_categories": ["Content Creation", "Design"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/creator/preferences",
            json=preferences
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "preferences" in data
        assert data["preferences"]["interests"] == ["AI", "automation", "content"]
        print("✓ Update preferences endpoint working")
    
    def test_track_interaction(self):
        """Test tracking tool interaction"""
        response = requests.post(f"{BASE_URL}/api/creator/track-interaction/tool-1")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        print("✓ Track interaction endpoint working")


class TestRevenueAnalytics:
    """Revenue analytics tests"""
    
    def test_get_revenue_analytics(self):
        """Test getting revenue analytics"""
        response = requests.get(f"{BASE_URL}/api/creator/revenue/analytics")
        assert response.status_code == 200
        
        data = response.json()
        assert "creator_id" in data
        assert "total_revenue" in data
        assert "total_sales" in data
        assert "avg_sale_value" in data
        assert "monthly_revenue" in data
        assert "top_selling_tools" in data
        
        # Verify numeric values
        assert isinstance(data["total_revenue"], (int, float))
        assert isinstance(data["total_sales"], int)
        print(f"✓ Revenue analytics working - total revenue: ${data['total_revenue']:.2f}")
    
    def test_get_revenue_metrics(self):
        """Test getting detailed revenue metrics"""
        response = requests.get(f"{BASE_URL}/api/creator/revenue/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_earnings" in data
        assert "pending_earnings" in data
        assert "available_balance" in data
        assert "total_transactions" in data
        assert "successful_transactions" in data
        assert "refunded_transactions" in data
        assert "avg_transaction_value" in data
        assert "recent_transactions" in data
        
        # Verify recent transactions structure
        for txn in data["recent_transactions"]:
            assert "id" in txn
            assert "amount" in txn
            assert "status" in txn
        print(f"✓ Revenue metrics working - {data['total_transactions']} total transactions")
    
    def test_revenue_analytics_with_date_filter(self):
        """Test revenue analytics with date filters"""
        response = requests.get(
            f"{BASE_URL}/api/creator/revenue/analytics?period_start=2024-01-01&period_end=2026-12-31"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "creator_id" in data
        print("✓ Revenue analytics with date filter working")


class TestEdgeCases:
    """Edge case and error handling tests"""
    
    def test_search_with_invalid_category(self):
        """Test search with non-existent category"""
        response = requests.get(f"{BASE_URL}/api/creator/marketplace/search?category=NonExistent")
        assert response.status_code == 200
        
        data = response.json()
        assert data["count"] == 0
        print("✓ Search with invalid category returns empty results")
    
    def test_delete_nonexistent_portfolio_item(self):
        """Test deleting a non-existent portfolio item"""
        response = requests.delete(f"{BASE_URL}/api/creator/portfolio/item/nonexistent-id")
        assert response.status_code == 404
        print("✓ Delete non-existent item returns 404")
    
    def test_get_nonexistent_profile(self):
        """Test getting a non-existent profile"""
        response = requests.get(f"{BASE_URL}/api/creator/profile/nonexistent-user-12345")
        assert response.status_code == 404
        print("✓ Get non-existent profile returns 404")
    
    def test_recommendations_limit(self):
        """Test recommendations with different limits"""
        for limit in [1, 5, 10, 20]:
            response = requests.get(f"{BASE_URL}/api/creator/recommendations?limit={limit}")
            assert response.status_code == 200
            
            data = response.json()
            assert len(data["recommendations"]) <= limit
        print("✓ Recommendations limit parameter working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
