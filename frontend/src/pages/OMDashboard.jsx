import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Activity,
  Server,
  Database,
  Cpu,
  HardDrive,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Wrench,
  FileText,
  TrendingUp,
  Target,
  DollarSign,
  Search,
  Lightbulb
} from 'lucide-react';
import MarketingIntelligence from '../components/intelligence/MarketingIntelligence';
import TrendTracking from '../components/intelligence/TrendTracking';
import InvestmentResearch from '../components/intelligence/InvestmentResearch';
import ResearchHub from '../components/intelligence/ResearchHub';
import DiscoveryDashboard from '../components/discovery/DiscoveryDashboard';
import HybridAgentsHub from '../components/hybrid/HybridAgentsHub';
import AtomsDashboard from '../components/atoms/AtomsDashboard';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const OMDashboard = () => {
  const [healthData, setHealthData] = useState(null);
  const [workOrders, setWorkOrders] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(null);

  useEffect(() => {
    fetchData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    setRefreshInterval(interval);
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, []);

  const fetchData = async () => {
    try {
      const [healthRes, workOrdersRes, statsRes] = await Promise.all([
        fetch(`${API_URL}/api/maintenance/health`),
        fetch(`${API_URL}/api/maintenance/work-orders?limit=5`),
        fetch(`${API_URL}/api/maintenance/work-orders/stats/summary`)
      ]);

      const [health, workOrdersData, statsData] = await Promise.all([
        healthRes.json(),
        workOrdersRes.json(),
        statsRes.json()
      ]);

      setHealthData(health);
      setWorkOrders(workOrdersData.work_orders || []);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
        return 'text-green-500';
      case 'info':
        return 'text-blue-500';
      case 'warning':
      case 'degraded':
        return 'text-yellow-500';
      case 'critical':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      healthy: 'bg-green-500',
      info: 'bg-blue-500',
      degraded: 'bg-yellow-500',
      warning: 'bg-yellow-500',
      critical: 'bg-red-500',
      unknown: 'bg-gray-500'
    };
    
    const color = colors[status?.toLowerCase()] || colors.unknown;
    
    return <Badge className={`${color} text-white`}>{status}</Badge>;
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'info':
        return <Activity className="w-5 h-5 text-blue-500" />;
      case 'warning':
      case 'degraded':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'critical':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  const getComponentIcon = (component) => {
    const icons = {
      openclaw_gateway: <Server className="w-5 h-5" />,
      mongodb: <Database className="w-5 h-5" />,
      system_resources: <Cpu className="w-5 h-5" />,
      api_endpoints: <Activity className="w-5 h-5" />
    };
    return icons[component] || <Activity className="w-5 h-5" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Activity className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading system status...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Operations & Maintenance</h1>
          <p className="text-gray-600">System health, work orders, and diagnostics</p>
        </div>
        <Button onClick={fetchData} variant="outline">
          <Activity className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Overall Status Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>System Overview</CardTitle>
              <CardDescription>Real-time platform health</CardDescription>
            </div>
            {healthData && getStatusBadge(healthData.overall_status)}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {healthData?.components?.map((component, idx) => (
              <Card key={idx} className="border-l-4" style={{
                borderLeftColor: 
                  component.status === 'healthy' ? '#22c55e' :
                  component.status === 'info' ? '#3b82f6' :
                  component.status === 'degraded' || component.status === 'warning' ? '#eab308' : 
                  '#ef4444'
              }}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    {getComponentIcon(component.component)}
                    {getStatusIcon(component.status)}
                  </div>
                  <h3 className="font-semibold capitalize">
                    {component.component.replace('_', ' ')}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {component.message || component.status}
                  </p>
                  
                  {/* Component-specific details */}
                  {component.component === 'system_resources' && component.cpu && (
                    <div className="mt-3 space-y-1 text-xs text-gray-600">
                      <div className="flex justify-between">
                        <span>CPU:</span>
                        <span className={component.cpu.percent > 80 ? 'text-yellow-600 font-semibold' : ''}>
                          {component.cpu.percent}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Memory:</span>
                        <span className={component.memory.percent > 85 ? 'text-yellow-600 font-semibold' : ''}>
                          {component.memory.percent}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Disk:</span>
                        <span className={component.disk.percent > 90 ? 'text-red-600 font-semibold' : ''}>
                          {component.disk.percent}%
                        </span>
                      </div>
                    </div>
                  )}
                  
                  {component.component === 'openclaw_gateway' && (
                    <div className="mt-2 text-xs text-gray-600">
                      {component.running ? (
                        <span className="text-green-600">● Running</span>
                      ) : (
                        <span className="text-red-600">● Stopped</span>
                      )}
                      {component.provider && (
                        <span className="ml-2">({component.provider})</span>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Tabs for different sections */}
      <Tabs defaultValue="workorders">
        <TabsList className="grid w-full grid-cols-10 gap-2">
          <TabsTrigger value="workorders">
            <Wrench className="w-4 h-4 mr-2" />
            Work Orders
          </TabsTrigger>
          <TabsTrigger value="diagnostics">
            <FileText className="w-4 h-4 mr-2" />
            Diagnostics
          </TabsTrigger>
          <TabsTrigger value="analytics">
            <TrendingUp className="w-4 h-4 mr-2" />
            Analytics
          </TabsTrigger>
          <TabsTrigger value="hybrid-agents">
            🤖 AI Agents
          </TabsTrigger>
          <TabsTrigger value="atoms">
            🚀 Atoms
          </TabsTrigger>
          <TabsTrigger value="discovery">
            <Search className="w-4 h-4 mr-2" />
            Discovery
          </TabsTrigger>
          <TabsTrigger value="marketing">
            <Target className="w-4 h-4 mr-2" />
            Marketing
          </TabsTrigger>
          <TabsTrigger value="trends">
            <TrendingUp className="w-4 h-4 mr-2" />
            Trends
          </TabsTrigger>
          <TabsTrigger value="investment">
            <DollarSign className="w-4 h-4 mr-2" />
            Investment
          </TabsTrigger>
          <TabsTrigger value="research">
            <Search className="w-4 h-4 mr-2" />
            Research
          </TabsTrigger>
        </TabsList>

        <TabsContent value="workorders" className="space-y-4">
          {/* Work Orders Stats */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold">{stats.total || 0}</div>
                  <p className="text-sm text-gray-600">Total Work Orders</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-blue-600">
                    {stats.by_status?.open || 0}
                  </div>
                  <p className="text-sm text-gray-600">Open</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-yellow-600">
                    {stats.by_status?.in_progress || 0}
                  </div>
                  <p className="text-sm text-gray-600">In Progress</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-green-600">
                    {stats.avg_resolution_time_minutes || 0} min
                  </div>
                  <p className="text-sm text-gray-600">Avg Resolution Time</p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Recent Work Orders */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Recent Work Orders</CardTitle>
                <Button onClick={() => window.location.href = '/work-orders'}>
                  View All
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {workOrders.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Wrench className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No work orders yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {workOrders.map((wo) => (
                    <div key={wo.id} className="border rounded-lg p-4 hover:bg-gray-50 transition">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold">{wo.title}</h4>
                          <p className="text-sm text-gray-600 mt-1">{wo.description}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <Badge className={
                              wo.priority === 'critical' ? 'bg-red-500 text-white' :
                              wo.priority === 'high' ? 'bg-orange-500 text-white' :
                              wo.priority === 'medium' ? 'bg-yellow-500 text-white' :
                              'bg-blue-500 text-white'
                            }>
                              {wo.priority}
                            </Badge>
                            <Badge variant="outline">{wo.status}</Badge>
                            <span className="text-xs text-gray-500">
                              <Clock className="w-3 h-3 inline mr-1" />
                              {new Date(wo.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="diagnostics">
          <Card>
            <CardHeader>
              <CardTitle>System Diagnostics</CardTitle>
              <CardDescription>Troubleshooting tools and knowledge base</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={() => window.location.href = '/troubleshooter'}
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Start Troubleshooting Session
                </Button>
                <Button 
                  className="w-full justify-start" 
                  variant="outline"
                  onClick={() => window.location.href = '/knowledge-base'}
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Browse Knowledge Base
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics">
          <Card>
            <CardHeader>
              <CardTitle>System Analytics</CardTitle>
              <CardDescription>Performance metrics and insights</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Analytics dashboard coming soon...
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Hybrid AI Agents Tab */}
        <TabsContent value="hybrid-agents">
          <HybridAgentsHub />
        </TabsContent>

        {/* Hybrid AI Agents Tab */}
        <TabsContent value="hybrid-agents">
          <HybridAgentsHub />
        </TabsContent>

        {/* Atoms AI Team Tab */}
        <TabsContent value="atoms">
          <AtomsDashboard />
        </TabsContent>

        {/* Intelligence Tabs */}
        <TabsContent value="discovery">
          <DiscoveryDashboard />
        </TabsContent>

        <TabsContent value="marketing">
          <MarketingIntelligence />
        </TabsContent>

        <TabsContent value="trends">
          <TrendTracking />
        </TabsContent>

        <TabsContent value="investment">
          <InvestmentResearch />
        </TabsContent>

        <TabsContent value="research">
          <ResearchHub />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default OMDashboard;
