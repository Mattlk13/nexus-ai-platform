import React, { useState, useEffect } from 'react';
import { 
  Activity, Settings, Zap, Shield, Database, Globe, 
  Users, Code, Terminal, CheckCircle, XCircle, AlertTriangle,
  TrendingUp, Clock, Cpu, HardDrive, Network, Bell, Wifi, WifiOff
} from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useNotifications } from '../components/NotificationSystem';
import AutomationPanel from '../components/AutomationPanel';

const API = process.env.REACT_APP_BACKEND_URL;

const OpenClawDashboard = () => {
  const [dashboardInfo, setDashboardInfo] = useState(null);
  const [quickStats, setQuickStats] = useState(null);
  const [systemInfo, setSystemInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAutomation, setShowAutomation] = useState(false);
  const [autonomousStatus, setAutonomousStatus] = useState(null);
  
  const notifications = useNotifications();

  // WebSocket for real-time stats
  const statsWs = useWebSocket('/api/openclaw/ws/stats', {
    onMessage: (data) => {
      if (data.type === 'stats') {
        setQuickStats(prevStats => ({
          ...prevStats,
          ...data.data,
          gateway_healthy: data.data.healthy
        }));
      }
    },
    onConnect: () => {
      console.log('Real-time stats connected');
    },
    onError: (error) => {
      console.error('Stats WebSocket error:', error);
    },
    autoReconnect: true
  });

  // WebSocket for notifications
  const notifWs = useWebSocket('/api/openclaw/ws/notifications', {
    onMessage: (data) => {
      if (data.type === 'notification') {
        const { level, title, message } = data.data;
        notifications.notify({ level, title, message });
      }
    },
    autoReconnect: true
  });

  // WebSocket for autonomous updates
  const autonomousWs = useWebSocket('/api/openclaw/ws/autonomous', {
    onMessage: (data) => {
      if (data.type === 'autonomous') {
        setAutonomousStatus(data.data);
      }
    },
    autoReconnect: true
  });

  useEffect(() => {
    fetchDashboardData();
    fetchAutonomousStatus();
    
    // Fallback polling for non-WebSocket updates
    const interval = setInterval(() => {
      fetchDashboardData();
      fetchAutonomousStatus();
    }, 30000); // Every 30s as backup
    
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [infoRes, statsRes, systemRes] = await Promise.all([
        fetch(`${API}/api/openclaw/web/dashboard/info`),
        fetch(`${API}/api/openclaw/web/dashboard/quick-stats`),
        fetch(`${API}/api/openclaw/web/system/info`)
      ]);

      setDashboardInfo(await infoRes.json());
      
      // Only update stats if WebSocket isn't connected
      if (!statsWs.isConnected) {
        setQuickStats(await statsRes.json());
      }
      
      setSystemInfo(await systemRes.json());
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      notifications.error('Data Fetch Failed', 'Could not load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const fetchAutonomousStatus = async () => {
    try {
      const response = await fetch(`${API}/api/openclaw/automation/autonomous-status`);
      const data = await response.json();
      setAutonomousStatus(data);
    } catch (error) {
      console.error('Failed to fetch autonomous status:', error);
    }
  };

  const formatUptime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const handleAutomationComplete = (action, result) => {
    console.log('Automation completed:', action, result);
    // Refresh dashboard data after automation
    setTimeout(() => {
      fetchDashboardData();
      fetchAutonomousStatus();
    }, 1000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
      </div>
    );
  }

  const isHealthy = quickStats?.gateway_healthy && systemInfo?.healthy;
  const isRealTime = statsWs.isConnected || notifWs.isConnected;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                OpenClaw Dashboard 🦞
              </h1>
              <div className="flex items-center gap-4">
                <p className="text-slate-300 text-lg">
                  Complete gateway management and automation
                </p>
                
                {/* Real-time indicator */}
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs ${
                  isRealTime ? 'bg-green-500/20 text-green-400' : 'bg-slate-700 text-slate-400'
                }`}>
                  {isRealTime ? (
                    <>
                      <Wifi className="w-3 h-3 animate-pulse" />
                      <span>Live</span>
                    </>
                  ) : (
                    <>
                      <WifiOff className="w-3 h-3" />
                      <span>Polling</span>
                    </>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Autonomous Status Badge */}
              {autonomousStatus?.enabled && (
                <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-600/20 text-purple-400 border border-purple-500/30">
                  <Zap className="w-5 h-5 animate-pulse" />
                  <span className="font-medium">Autonomous Active</span>
                </div>
              )}
              
              {/* Health Status */}
              <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
                isHealthy ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
              }`}>
                {isHealthy ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
                <span className="font-medium">
                  {isHealthy ? 'All Systems Operational' : 'System Issues Detected'}
                </span>
              </div>
              
              {/* Automation Panel Toggle */}
              <button
                onClick={() => setShowAutomation(!showAutomation)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  showAutomation 
                    ? 'bg-purple-600 text-white' 
                    : 'bg-slate-800/50 text-slate-300 hover:bg-slate-700/50'
                }`}
              >
                <Zap className="w-5 h-5" />
                <span className="font-medium">Automation</span>
              </button>
            </div>
          </div>
        </div>

        {/* Automation Panel */}
        {showAutomation && (
          <div className="mb-8 bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20">
            <AutomationPanel 
              onAutomationComplete={handleAutomationComplete}
              notifications={notifications}
            />
          </div>
        )}

        {/* Quick Stats Grid - With Real-time Updates */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/20 relative overflow-hidden">
            {isRealTime && (
              <div className="absolute top-2 right-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              </div>
            )}
            <div className="flex items-center gap-3 mb-2">
              <Activity className="w-8 h-8 text-blue-400" />
              <div className="text-sm text-slate-400">Active Sessions</div>
            </div>
            <div className="text-3xl font-bold text-blue-400">
              {quickStats?.active_sessions || 0}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Current conversations
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20">
            <div className="flex items-center gap-3 mb-2">
              <Database className="w-8 h-8 text-purple-400" />
              <div className="text-sm text-slate-400">Models</div>
            </div>
            <div className="text-3xl font-bold text-purple-400">
              {quickStats?.total_models || 3}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Available AI models
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-green-500/20">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="w-8 h-8 text-green-400" />
              <div className="text-sm text-slate-400">Uptime</div>
            </div>
            <div className="text-3xl font-bold text-green-400">
              {quickStats?.uptime_hours || 0}h
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Gateway running
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-yellow-500/20">
            <div className="flex items-center gap-3 mb-2">
              <Network className="w-8 h-8 text-yellow-400" />
              <div className="text-sm text-slate-400">Version</div>
            </div>
            <div className="text-2xl font-bold text-yellow-400">
              {systemInfo?.version || '2026.3.2'}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              OpenClaw version
            </div>
          </div>
        </div>

        {/* Autonomous Stats (if enabled) */}
        {autonomousStatus?.enabled && (
          <div className="mb-8 bg-gradient-to-r from-purple-900/30 to-pink-900/30 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/30">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Zap className="w-6 h-6 text-purple-400" />
              Autonomous System Status
            </h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-slate-800/30 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">Mode</div>
                <div className="text-2xl font-bold text-purple-400 capitalize">
                  {autonomousStatus.mode}
                </div>
              </div>
              <div className="bg-slate-800/30 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">Tasks Executed</div>
                <div className="text-2xl font-bold text-blue-400">
                  {autonomousStatus.stats?.total_tasks_executed || 0}
                </div>
              </div>
              <div className="bg-slate-800/30 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">Auto-Heals</div>
                <div className="text-2xl font-bold text-green-400">
                  {autonomousStatus.stats?.auto_heals || 0}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* System Information */}
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20 mb-8">
          <div className="flex items-center gap-3 mb-6">
            <Cpu className="w-6 h-6 text-purple-400" />
            <h2 className="text-2xl font-bold">System Information</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex items-center gap-3">
                  <Terminal className="w-5 h-5 text-blue-400" />
                  <div>
                    <div className="font-medium">Node.js Version</div>
                    <div className="text-xs text-slate-400">{systemInfo?.node_version || 'v22.22.2'}</div>
                  </div>
                </div>
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex items-center gap-3">
                  <Globe className="w-5 h-5 text-green-400" />
                  <div>
                    <div className="font-medium">Platform</div>
                    <div className="text-xs text-slate-400">{systemInfo?.platform || 'Linux'}</div>
                  </div>
                </div>
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex items-center gap-3">
                  <Network className="w-5 h-5 text-purple-400" />
                  <div>
                    <div className="font-medium">Gateway Port</div>
                    <div className="text-xs text-slate-400">{systemInfo?.gateway_port || 18789}</div>
                  </div>
                </div>
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-yellow-400" />
                  <div>
                    <div className="font-medium">Control UI</div>
                    <div className="text-xs text-slate-400">
                      {dashboardInfo?.enabled ? 'Enabled' : 'Disabled'}
                    </div>
                  </div>
                </div>
                {dashboardInfo?.enabled ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <XCircle className="w-5 h-5 text-red-400" />
                )}
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex items-center gap-3">
                  <Shield className="w-5 h-5 text-red-400" />
                  <div>
                    <div className="font-medium">Webhooks</div>
                    <div className="text-xs text-slate-400">
                      {systemInfo?.webhooks_enabled ? 'Enabled' : 'Disabled'}
                    </div>
                  </div>
                </div>
                {systemInfo?.webhooks_enabled ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-yellow-400" />
                )}
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-blue-400" />
                  <div>
                    <div className="font-medium">Uptime</div>
                    <div className="text-xs text-slate-400">
                      {formatUptime(systemInfo?.uptime || 0)}
                    </div>
                  </div>
                </div>
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <a
            href="/openclaw-autonomous"
            className="bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20 transition-all group"
          >
            <div className="flex items-center gap-3 mb-3">
              <Zap className="w-8 h-8 text-purple-400" />
              <h3 className="text-xl font-bold">Autonomous Mode</h3>
            </div>
            <p className="text-slate-400 mb-4 text-sm">
              Self-managing AI with intelligent decision-making
            </p>
            <div className="flex items-center gap-2 text-purple-400 group-hover:gap-3 transition-all">
              <span className="text-sm">Configure →</span>
            </div>
          </a>

          <a
            href="/openclaw-chat"
            className="bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/20 transition-all group"
          >
            <div className="flex items-center gap-3 mb-3">
              <Activity className="w-8 h-8 text-blue-400" />
              <h3 className="text-xl font-bold">Live Chat</h3>
            </div>
            <p className="text-slate-400 mb-4 text-sm">
              Real-time AI chat with streaming responses
            </p>
            <div className="flex items-center gap-2 text-blue-400 group-hover:gap-3 transition-all">
              <span className="text-sm">Open Chat →</span>
            </div>
          </a>

          <a
            href="/openclaw-settings"
            className="bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-lg rounded-2xl p-6 border border-green-500/20 transition-all group"
          >
            <div className="flex items-center gap-3 mb-3">
              <Settings className="w-8 h-8 text-green-400" />
              <h3 className="text-xl font-bold">Settings</h3>
            </div>
            <p className="text-slate-400 mb-4 text-sm">
              Configure webhooks, security, and preferences
            </p>
            <div className="flex items-center gap-2 text-green-400 group-hover:gap-3 transition-all">
              <span className="text-sm">Manage →</span>
            </div>
          </a>
        </div>

        {/* Quick Links */}
        <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/30">
          <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
          <div className="grid md:grid-cols-4 gap-3">
            <a href="/openclaw-control" className="px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg text-sm transition-all text-center">
              Control Panel
            </a>
            <a href="/openclaw-logs" className="px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg text-sm transition-all text-center">
              Live Logs
            </a>
            <a href="/openclaw-info" className="px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg text-sm transition-all text-center">
              System Info
            </a>
            <a href="/maintenance" className="px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg text-sm transition-all text-center">
              Maintenance
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OpenClawDashboard;
