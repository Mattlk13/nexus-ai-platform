"""
Nexus AI Platform API Tests
Tests for O&M Dashboard, Multimodal AI, and OpenClaw endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthEndpoints:
    """Test root and health check endpoints"""
    
    def test_root_api(self):
        """Test root API endpoint returns expected message"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "OpenClaw Hosting API"
        print("✓ Root API endpoint working")
    
    def test_auth_instance_status(self):
        """Test auth instance status endpoint"""
        response = requests.get(f"{BASE_URL}/api/auth/instance")
        assert response.status_code == 200
        data = response.json()
        assert "locked" in data
        print(f"✓ Auth instance status: locked={data['locked']}")


class TestMaintenanceHealthMonitor:
    """Test O&M Dashboard health monitoring endpoints"""
    
    def test_system_health_endpoint(self):
        """Test comprehensive system health check"""
        response = requests.get(f"{BASE_URL}/api/maintenance/health")
        assert response.status_code == 200
        data = response.json()
        
        # Verify overall status
        assert "overall_status" in data
        assert data["overall_status"] in ["healthy", "degraded", "critical", "warning"]
        
        # Verify timestamp
        assert "timestamp" in data
        
        # Verify components array
        assert "components" in data
        assert isinstance(data["components"], list)
        assert len(data["components"]) == 4  # 4 components expected
        
        # Verify each component has required fields
        component_names = []
        for component in data["components"]:
            assert "component" in component
            assert "status" in component
            assert "timestamp" in component
            component_names.append(component["component"])
        
        # Verify all 4 expected components are present
        expected_components = ["openclaw_gateway", "mongodb", "system_resources", "api_endpoints"]
        for expected in expected_components:
            assert expected in component_names, f"Missing component: {expected}"
        
        print(f"✓ System health check: overall_status={data['overall_status']}")
        print(f"  Components: {component_names}")
    
    def test_mongodb_component_health(self):
        """Test MongoDB component reports correct status"""
        response = requests.get(f"{BASE_URL}/api/maintenance/health")
        assert response.status_code == 200
        data = response.json()
        
        mongodb_component = next(
            (c for c in data["components"] if c["component"] == "mongodb"),
            None
        )
        assert mongodb_component is not None
        assert mongodb_component["status"] == "healthy"
        assert "database" in mongodb_component
        assert "connections" in mongodb_component
        assert "storage" in mongodb_component
        print(f"✓ MongoDB health: status={mongodb_component['status']}, db={mongodb_component['database']}")
    
    def test_system_resources_component(self):
        """Test system resources component reports CPU/Memory/Disk"""
        response = requests.get(f"{BASE_URL}/api/maintenance/health")
        assert response.status_code == 200
        data = response.json()
        
        resources = next(
            (c for c in data["components"] if c["component"] == "system_resources"),
            None
        )
        assert resources is not None
        assert resources["status"] in ["healthy", "warning", "critical"]
        
        # Verify CPU metrics
        assert "cpu" in resources
        assert "percent" in resources["cpu"]
        assert "count" in resources["cpu"]
        
        # Verify Memory metrics
        assert "memory" in resources
        assert "total" in resources["memory"]
        assert "available" in resources["memory"]
        assert "percent" in resources["memory"]
        
        # Verify Disk metrics
        assert "disk" in resources
        assert "total" in resources["disk"]
        assert "used" in resources["disk"]
        assert "free" in resources["disk"]
        assert "percent" in resources["disk"]
        
        print(f"✓ System resources: CPU={resources['cpu']['percent']}%, Memory={resources['memory']['percent']}%, Disk={resources['disk']['percent']}%")
    
    def test_openclaw_gateway_component(self):
        """Test OpenClaw gateway component status (expected: info when not running)"""
        response = requests.get(f"{BASE_URL}/api/maintenance/health")
        assert response.status_code == 200
        data = response.json()
        
        gateway = next(
            (c for c in data["components"] if c["component"] == "openclaw_gateway"),
            None
        )
        assert gateway is not None
        # Gateway not running is expected - should show "info" status
        assert gateway["status"] in ["healthy", "info", "critical"]
        assert "running" in gateway
        assert "message" in gateway
        print(f"✓ OpenClaw gateway: status={gateway['status']}, running={gateway['running']}, message={gateway['message']}")
    
    def test_api_endpoints_component(self):
        """Test API endpoints component health"""
        response = requests.get(f"{BASE_URL}/api/maintenance/health")
        assert response.status_code == 200
        data = response.json()
        
        api_component = next(
            (c for c in data["components"] if c["component"] == "api_endpoints"),
            None
        )
        assert api_component is not None
        assert api_component["status"] in ["healthy", "degraded", "critical"]
        assert "endpoints" in api_component
        
        for endpoint in api_component["endpoints"]:
            assert "name" in endpoint
            assert "path" in endpoint
            assert "status" in endpoint
            assert "status_code" in endpoint
        
        print(f"✓ API endpoints health: status={api_component['status']}, endpoints_checked={len(api_component['endpoints'])}")


class TestWorkOrderEndpoints:
    """Test work order management endpoints"""
    
    def test_list_work_orders(self):
        """Test listing work orders"""
        response = requests.get(f"{BASE_URL}/api/maintenance/work-orders?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "work_orders" in data
        assert isinstance(data["work_orders"], list)
        print(f"✓ Work orders list: {len(data['work_orders'])} orders found")
    
    def test_work_order_stats(self):
        """Test work order statistics endpoint"""
        response = requests.get(f"{BASE_URL}/api/maintenance/work-orders/stats/summary")
        assert response.status_code == 200
        data = response.json()
        # Stats endpoint should return some data structure
        print(f"✓ Work order stats: {data}")


class TestMultimodalEndpoints:
    """Test multimodal AI service endpoints"""
    
    def test_multimodal_status(self):
        """Test multimodal services status endpoint"""
        response = requests.get(f"{BASE_URL}/api/multimodal/status")
        assert response.status_code == 200
        data = response.json()
        
        # Verify TTS service status
        assert "tts" in data
        assert "available" in data["tts"]
        assert "service" in data["tts"]
        assert data["tts"]["service"] == "Coqui TTS"
        
        # Verify STT service status
        assert "stt" in data
        assert "available" in data["stt"]
        assert "service" in data["stt"]
        assert data["stt"]["service"] == "OpenAI Whisper"
        
        # Verify Vision service status
        assert "vision" in data
        assert "available" in data["vision"]
        assert "service" in data["vision"]
        assert data["vision"]["service"] == "CLIP"
        
        print(f"✓ Multimodal status: TTS={data['tts']['available']}, STT={data['stt']['available']}, Vision={data['vision']['available']}")
    
    def test_tts_voices_endpoint(self):
        """Test TTS voices endpoint (may return 503 if service unavailable)"""
        response = requests.get(f"{BASE_URL}/api/multimodal/tts/voices")
        # Service may not be available, so 503 is acceptable
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            print(f"✓ TTS voices available: {response.json()}")
        else:
            print("✓ TTS voices endpoint returns 503 (service unavailable - expected)")
    
    def test_stt_languages_endpoint(self):
        """Test STT languages endpoint (may return 503 if service unavailable)"""
        response = requests.get(f"{BASE_URL}/api/multimodal/stt/languages")
        # Service may not be available, so 503 is acceptable
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            print(f"✓ STT languages available: {response.json()}")
        else:
            print("✓ STT languages endpoint returns 503 (service unavailable - expected)")


class TestOpenClawEndpoints:
    """Test OpenClaw gateway management endpoints"""
    
    def test_openclaw_status(self):
        """Test OpenClaw status endpoint"""
        response = requests.get(f"{BASE_URL}/api/openclaw/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "running" in data
        assert isinstance(data["running"], bool)
        
        if data["running"]:
            assert "pid" in data
            assert "provider" in data
            assert "started_at" in data
            assert "controlUrl" in data
            print(f"✓ OpenClaw status: running=True, provider={data['provider']}")
        else:
            print("✓ OpenClaw status: running=False (expected - requires auth to start)")
    
    def test_openclaw_start_requires_auth(self):
        """Test that starting OpenClaw requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/openclaw/start",
            json={"provider": "emergent"}
        )
        assert response.status_code == 401
        print("✓ OpenClaw start requires authentication (401)")
    
    def test_openclaw_stop_requires_auth(self):
        """Test that stopping OpenClaw requires authentication"""
        response = requests.post(f"{BASE_URL}/api/openclaw/stop")
        assert response.status_code == 401
        print("✓ OpenClaw stop requires authentication (401)")
    
    def test_openclaw_token_requires_auth(self):
        """Test that getting OpenClaw token requires authentication"""
        response = requests.get(f"{BASE_URL}/api/openclaw/token")
        assert response.status_code == 401
        print("✓ OpenClaw token requires authentication (401)")


class TestKnowledgeBaseEndpoints:
    """Test knowledge base endpoints"""
    
    def test_search_knowledge_base(self):
        """Test knowledge base search endpoint"""
        response = requests.get(f"{BASE_URL}/api/maintenance/knowledge-base?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "articles" in data
        assert isinstance(data["articles"], list)
        print(f"✓ Knowledge base search: {len(data['articles'])} articles found")


class TestTroubleshootingEndpoints:
    """Test troubleshooting endpoints"""
    
    def test_troubleshooting_suggestions(self):
        """Test troubleshooting suggestions endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/maintenance/troubleshooting/suggestions",
            params={"component": "mongodb", "symptoms": []}
        )
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        print(f"✓ Troubleshooting suggestions: {len(data['suggestions'])} suggestions")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
