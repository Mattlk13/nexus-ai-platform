"""
Nexus System Health Monitor
Real-time monitoring of all platform components
"""
import asyncio
import logging
import psutil
import httpx
from datetime import datetime, timezone
from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitor system health and generate alerts"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
    
    async def check_openclaw_gateway(self) -> Dict:
        """Check OpenClaw gateway status"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.backend_url}/api/openclaw/status")
                data = response.json()
                
                # OpenClaw not running is not critical - it's expected until user starts it
                is_running = data.get("running", False)
                status = "healthy" if is_running else "info"
                
                return {
                    "component": "openclaw_gateway",
                    "status": status,
                    "running": is_running,
                    "pid": data.get("pid"),
                    "provider": data.get("provider"),
                    "uptime": data.get("started_at"),
                    "message": "Gateway ready to start" if not is_running else f"Running with {data.get('provider')}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            logger.error(f"OpenClaw health check failed: {e}")
            return {
                "component": "openclaw_gateway",
                "status": "critical",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def check_mongodb(self) -> Dict:
        """Check MongoDB connection and performance"""
        try:
            # Get the database client from the database object
            client = self.db.client
            
            # Ping MongoDB
            await client.admin.command('ping')
            
            # Get server status
            server_status = await client.admin.command('serverStatus')
            connections = server_status.get('connections', {})
            
            # Get current database stats
            db_name = os.environ['DB_NAME']
            stats = await self.db.command('dbStats')
            
            return {
                "component": "mongodb",
                "status": "healthy",
                "database": db_name,
                "connections": {
                    "current": connections.get('current', 0),
                    "available": connections.get('available', 0)
                },
                "storage": {
                    "data_size_mb": round(stats.get('dataSize', 0) / 1024 / 1024, 2),
                    "storage_size_mb": round(stats.get('storageSize', 0) / 1024 / 1024, 2),
                    "indexes": stats.get('indexes', 0),
                    "collections": stats.get('collections', 0)
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return {
                "component": "mongodb",
                "status": "critical",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def check_system_resources(self) -> Dict:
        """Check CPU, Memory, Disk usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine status based on thresholds
            status = "healthy"
            if cpu_percent > 80 or memory.percent > 85 or disk.percent > 90:
                status = "warning"
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                status = "critical"
            
            return {
                "component": "system_resources",
                "status": status,
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"System resources check failed: {e}")
            return {
                "component": "system_resources",
                "status": "unknown",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def check_api_endpoints(self) -> Dict:
        """Check critical API endpoints"""
        endpoints = [
            ("/api/", "root"),
            ("/api/auth/instance", "auth"),
        ]
        
        results = []
        overall_status = "healthy"
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            for path, name in endpoints:
                try:
                    start = datetime.now()
                    response = await client.get(f"{self.backend_url}{path}")
                    duration = (datetime.now() - start).total_seconds() * 1000
                    
                    endpoint_status = "healthy" if response.status_code < 500 else "degraded"
                    if response.status_code >= 500:
                        overall_status = "degraded"
                    
                    results.append({
                        "name": name,
                        "path": path,
                        "status": endpoint_status,
                        "status_code": response.status_code,
                        "response_time_ms": round(duration, 2)
                    })
                except Exception as e:
                    overall_status = "critical"
                    results.append({
                        "name": name,
                        "path": path,
                        "status": "critical",
                        "error": str(e)
                    })
        
        return {
            "component": "api_endpoints",
            "status": overall_status,
            "endpoints": results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def run_full_health_check(self) -> Dict:
        """Run comprehensive health check on all components"""
        checks = await asyncio.gather(
            self.check_openclaw_gateway(),
            self.check_mongodb(),
            self.check_system_resources(),
            self.check_api_endpoints(),
            return_exceptions=True
        )
        
        # Determine overall system status
        statuses = []
        for check in checks:
            if isinstance(check, dict):
                statuses.append(check.get('status', 'unknown'))
        
        if 'critical' in statuses:
            overall_status = 'critical'
        elif 'degraded' in statuses or 'warning' in statuses:
            overall_status = 'degraded'
        else:
            overall_status = 'healthy'
        
        health_report = {
            "overall_status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": [c for c in checks if isinstance(c, dict)]
        }
        
        # Store in database
        try:
            await self.db.health_checks.insert_one(health_report.copy())
        except Exception as e:
            logger.error(f"Failed to store health check: {e}")
        
        return health_report
    
    async def get_health_history(self, hours: int = 24, component: Optional[str] = None) -> List[Dict]:
        """Get health check history"""
        from_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        query = {"timestamp": {"$gte": from_time.isoformat()}}
        if component:
            query["components.component"] = component
        
        checks = await self.db.health_checks.find(
            query,
            {"_id": 0}
        ).sort("timestamp", -1).to_list(1000)
        
        return checks


from datetime import timedelta
