"""
OpenClaw Automation API Tests
Tests for automation endpoints: quick actions, autonomous mode, and presets
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAutomationQuickActions:
    """Tests for Quick Action endpoints"""
    
    def test_quick_start_endpoint(self):
        """Test /api/openclaw/automation/quick-start endpoint"""
        response = requests.post(f"{BASE_URL}/api/openclaw/automation/quick-start")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "message" in data
        # Quick start should complete with some actions
        if data["success"]:
            assert "actions_completed" in data
            assert "total_actions" in data
            assert data["actions_completed"] >= 0
    
    def test_optimize_now_endpoint(self):
        """Test /api/openclaw/automation/optimize-now endpoint"""
        response = requests.post(f"{BASE_URL}/api/openclaw/automation/optimize-now")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "message" in data
        # May fail if gateway not responding, but endpoint should work
    
    def test_auto_heal_now_endpoint(self):
        """Test /api/openclaw/automation/auto-heal-now endpoint"""
        response = requests.post(f"{BASE_URL}/api/openclaw/automation/auto-heal-now")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "message" in data
        # May fail if gateway not responding, but endpoint should work


class TestAutonomousMode:
    """Tests for Autonomous Mode endpoints"""
    
    def test_get_autonomous_status(self):
        """Test /api/openclaw/automation/autonomous-status endpoint"""
        response = requests.get(f"{BASE_URL}/api/openclaw/automation/autonomous-status")
        assert response.status_code == 200
        
        data = response.json()
        assert "enabled" in data
        assert "mode" in data
        assert isinstance(data["enabled"], bool)
        assert data["mode"] in ["manual", "reactive", "fully_autonomous"]
    
    def test_enable_autonomous(self):
        """Test /api/openclaw/automation/enable-autonomous endpoint"""
        response = requests.post(f"{BASE_URL}/api/openclaw/automation/enable-autonomous")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["mode"] == "fully_autonomous"
        assert "features" in data
        assert isinstance(data["features"], list)
        
        # Verify status changed
        status_response = requests.get(f"{BASE_URL}/api/openclaw/automation/autonomous-status")
        status_data = status_response.json()
        assert status_data["enabled"] == True
        assert status_data["mode"] == "fully_autonomous"
    
    def test_disable_autonomous(self):
        """Test /api/openclaw/automation/disable-autonomous endpoint"""
        response = requests.post(f"{BASE_URL}/api/openclaw/automation/disable-autonomous")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["mode"] == "manual"
        
        # Verify status changed
        status_response = requests.get(f"{BASE_URL}/api/openclaw/automation/autonomous-status")
        status_data = status_response.json()
        assert status_data["enabled"] == False
        assert status_data["mode"] == "manual"


class TestAutomationPresets:
    """Tests for Configuration Presets endpoints"""
    
    def test_get_presets(self):
        """Test /api/openclaw/automation/presets endpoint"""
        response = requests.get(f"{BASE_URL}/api/openclaw/automation/presets")
        assert response.status_code == 200
        
        data = response.json()
        assert "presets" in data
        assert isinstance(data["presets"], list)
        assert len(data["presets"]) >= 3  # At least development, production, testing
        
        # Verify preset structure
        for preset in data["presets"]:
            assert "id" in preset
            assert "name" in preset
            assert "description" in preset
    
    def test_apply_development_preset(self):
        """Test applying development preset"""
        response = requests.post(f"{BASE_URL}/api/openclaw/automation/presets/development/apply")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["preset_id"] == "development"
    
    def test_apply_production_preset(self):
        """Test applying production preset"""
        response = requests.post(f"{BASE_URL}/api/openclaw/automation/presets/production/apply")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["preset_id"] == "production"
    
    def test_apply_testing_preset(self):
        """Test applying testing preset"""
        response = requests.post(f"{BASE_URL}/api/openclaw/automation/presets/testing/apply")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["preset_id"] == "testing"


class TestWebDashboardEndpoints:
    """Tests for Web Dashboard endpoints used by frontend"""
    
    def test_dashboard_info(self):
        """Test /api/openclaw/web/dashboard/info endpoint"""
        response = requests.get(f"{BASE_URL}/api/openclaw/web/dashboard/info")
        assert response.status_code == 200
        
        data = response.json()
        assert "gateway_url" in data
        assert "control_ui_url" in data
    
    def test_dashboard_quick_stats(self):
        """Test /api/openclaw/web/dashboard/quick-stats endpoint"""
        response = requests.get(f"{BASE_URL}/api/openclaw/web/dashboard/quick-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "active_sessions" in data
        assert "gateway_healthy" in data
    
    def test_system_info(self):
        """Test /api/openclaw/web/system/info endpoint"""
        response = requests.get(f"{BASE_URL}/api/openclaw/web/system/info")
        assert response.status_code == 200
        
        data = response.json()
        assert "healthy" in data


class TestOpenClawStatus:
    """Tests for OpenClaw gateway status"""
    
    def test_openclaw_status(self):
        """Test /api/openclaw/status endpoint"""
        response = requests.get(f"{BASE_URL}/api/openclaw/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "running" in data
        assert isinstance(data["running"], bool)
        
        if data["running"]:
            assert "provider" in data
            assert "controlUrl" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
