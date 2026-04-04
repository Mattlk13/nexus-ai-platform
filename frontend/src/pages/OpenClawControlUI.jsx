import React, { useState, useEffect } from 'react';
import { Activity, Terminal, Settings, Users, Zap, Code, MessageSquare, Calendar, Package, Eye, ExternalLink, RefreshCw } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const OpenClawControlUI = () => {
  const [gatewayStatus, setGatewayStatus] = useState(null);
  const [devices, setDevices] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [skills, setSkills] = useState([]);
  const [channels, setChannels] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statusRes, devicesRes, sessionsRes, skillsRes, channelsRes] = await Promise.all([
        fetch(`${API}/api/openclaw/status`),
        fetch(`${API}/api/openclaw/ui/devices/list`).catch(() => ({ json: () => ({ pending: [] }) })),
        fetch(`${API}/api/openclaw/ui/sessions/list`).catch(() => ({ json: () => ({ sessions: [] }) })),
        fetch(`${API}/api/openclaw/ui/skills/list`).catch(() => ({ json: () => ({ skills: [] }) })),
        fetch(`${API}/api/openclaw/ui/channels/status`).catch(() => ({ json: () => ({}) }))
      ]);

      setGatewayStatus(await statusRes.json());
      setDevices((await devicesRes.json()).pending || []);
      setSessions((await sessionsRes.json()).sessions || []);
      setSkills((await skillsRes.json()).skills || []);
      setChannels(await channelsRes.json());
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const openNativeControlUI = () => {
    window.open(`${API}/api/openclaw/ui/`, '_blank');
  };

  const approveDevice = async (requestId) => {
    try {
      await fetch(`${API}/api/openclaw/ui/devices/approve?request_id=${requestId}`, {
        method: 'POST'
      });
      fetchDashboardData();
    } catch (error) {
      console.error('Failed to approve device:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                OpenClaw Control UI 🦞
              </h1>
              <p className="text-slate-300 text-lg">
                Comprehensive gateway management and AI control center
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={fetchDashboardData}
                className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg transition-all"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
              <button
                onClick={openNativeControlUI}
                className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg font-medium transition-all"
              >
                <ExternalLink className="w-4 h-4" />
                Open Native Control UI
              </button>
            </div>
          </div>
        </div>

        {/* Gateway Status Card */}
        {gatewayStatus && (
          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 mb-6 border border-purple-500/20">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Terminal className="w-6 h-6 text-purple-400" />
                <h2 className="text-2xl font-bold">Gateway Status</h2>
              </div>
              <div className={`px-4 py-2 rounded-lg ${
                gatewayStatus.running ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
              }`}>
                {gatewayStatus.running ? '● Running' : '● Stopped'}
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-700/30 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">PID</div>
                <div className="text-xl font-bold">{gatewayStatus.pid || 'N/A'}</div>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">Provider</div>
                <div className="text-xl font-bold capitalize">{gatewayStatus.provider || 'N/A'}</div>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">Port</div>
                <div className="text-xl font-bold">18789</div>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">Owner</div>
                <div className="text-sm font-bold truncate">{gatewayStatus.owner_user_id || 'System'}</div>
              </div>
            </div>
          </div>
        )}

        {/* Quick Access Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-6">
          {/* Autonomous Agent */}
          <div className="bg-gradient-to-br from-purple-800/50 to-pink-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/30">
            <div className="flex items-center gap-3 mb-4">
              <Zap className="w-8 h-8 text-purple-300" />
              <h2 className="text-xl font-bold">Autonomous Mode</h2>
            </div>
            <p className="text-slate-300 mb-4 text-sm">
              Enable fully autonomous operation with self-management and intelligent decision-making
            </p>
            <a
              href="/openclaw-autonomous"
              className="block w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-center py-3 rounded-lg font-medium transition-all"
            >
              Configure Autonomous Mode →
            </a>
          </div>

          {/* Device Pairing */}
          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/20">
            <div className="flex items-center gap-3 mb-4">
              <Users className="w-6 h-6 text-blue-400" />
              <h2 className="text-xl font-bold">Device Pairing</h2>
            </div>
            {devices.length > 0 ? (
              <div className="space-y-2">
                <p className="text-sm text-slate-400 mb-3">{devices.length} pending request(s)</p>
                {devices.slice(0, 3).map((device, idx) => (
                  <div key={idx} className="bg-slate-700/30 rounded-lg p-3 flex items-center justify-between">
                    <div className="text-sm truncate flex-1">{device.requestId || `Device ${idx + 1}`}</div>
                    <button
                      onClick={() => approveDevice(device.requestId)}
                      className="ml-2 px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm"
                    >
                      Approve
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <Users className="w-12 h-12 text-slate-600 mx-auto mb-2" />
                <p className="text-slate-400">No pending devices</p>
              </div>
            )}
          </div>

          {/* Active Sessions */}
          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-green-500/20">
            <div className="flex items-center gap-3 mb-4">
              <MessageSquare className="w-6 h-6 text-green-400" />
              <h2 className="text-xl font-bold">Active Sessions</h2>
            </div>
            <div className="text-center py-6">
              <div className="text-4xl font-bold text-green-400 mb-2">{sessions.length}</div>
              <p className="text-slate-400">Active AI sessions</p>
            </div>
          </div>

          {/* Installed Skills */}
          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20">
            <div className="flex items-center gap-3 mb-4">
              <Package className="w-6 h-6 text-purple-400" />
              <h2 className="text-xl font-bold">Skills</h2>
            </div>
            <div className="text-center py-6">
              <div className="text-4xl font-bold text-purple-400 mb-2">{skills.length}</div>
              <p className="text-slate-400">Installed skills</p>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          {/* Chat Interface */}
          <a
            href="/openclaw-chat"
            className="bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/20 text-left transition-all group"
          >
            <div className="flex items-center gap-3 mb-3">
              <MessageSquare className="w-8 h-8 text-blue-400" />
              <h3 className="text-xl font-bold">Chat Interface</h3>
            </div>
            <p className="text-slate-400 mb-4">Direct AI model interaction via WebSocket with streaming responses</p>
            <div className="flex items-center gap-2 text-blue-400 group-hover:gap-3 transition-all">
              <span className="text-sm">Open Chat</span>
              <ExternalLink className="w-4 h-4" />
            </div>
          </a>

          {/* Channel Management */}
          <button
            onClick={openNativeControlUI}
            className="bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-lg rounded-2xl p-6 border border-green-500/20 text-left transition-all group"
          >
            <div className="flex items-center gap-3 mb-3">
              <Activity className="w-8 h-8 text-green-400" />
              <h3 className="text-xl font-bold">Channels</h3>
            </div>
            <p className="text-slate-400 mb-4">Manage WhatsApp, Telegram, Discord, Slack integrations</p>
            <div className="flex items-center gap-2 text-green-400 group-hover:gap-3 transition-all">
              <span className="text-sm">Configure Channels</span>
              <ExternalLink className="w-4 h-4" />
            </div>
          </button>

          {/* Cron Jobs */}
          <button
            onClick={openNativeControlUI}
            className="bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20 text-left transition-all group"
          >
            <div className="flex items-center gap-3 mb-3">
              <Calendar className="w-8 h-8 text-purple-400" />
              <h3 className="text-xl font-bold">Cron Jobs</h3>
            </div>
            <p className="text-slate-400 mb-4">Schedule automated AI tasks and workflows</p>
            <div className="flex items-center gap-2 text-purple-400 group-hover:gap-3 transition-all">
              <span className="text-sm">Manage Jobs</span>
              <ExternalLink className="w-4 h-4" />
            </div>
          </button>

          {/* Config Editor */}
          <button
            onClick={openNativeControlUI}
            className="bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-lg rounded-2xl p-6 border border-yellow-500/20 text-left transition-all group"
          >
            <div className="flex items-center gap-3 mb-3">
              <Settings className="w-8 h-8 text-yellow-400" />
              <h3 className="text-xl font-bold">Configuration</h3>
            </div>
            <p className="text-slate-400 mb-4">Edit openclaw.json with schema validation</p>
            <div className="flex items-center gap-2 text-yellow-400 group-hover:gap-3 transition-all">
              <span className="text-sm">Edit Config</span>
              <ExternalLink className="w-4 h-4" />
            </div>
          </button>

          {/* Live Logs */}
          <a
            href="/openclaw-logs"
            className="bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-lg rounded-2xl p-6 border border-pink-500/20 text-left transition-all group"
          >
            <div className="flex items-center gap-3 mb-3">
              <Eye className="w-8 h-8 text-pink-400" />
              <h3 className="text-xl font-bold">Live Logs</h3>
            </div>
            <p className="text-slate-400 mb-4">Real-time log streaming with filtering</p>
            <div className="flex items-center gap-2 text-pink-400 group-hover:gap-3 transition-all">
              <span className="text-sm">View Logs</span>
              <ExternalLink className="w-4 h-4" />
            </div>
          </a>

          {/* Debug Panel */}
          <button
            onClick={openNativeControlUI}
            className="bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-lg rounded-2xl p-6 border border-red-500/20 text-left transition-all group"
          >
            <div className="flex items-center gap-3 mb-3">
              <Code className="w-8 h-8 text-red-400" />
              <h3 className="text-xl font-bold">Debug Tools</h3>
            </div>
            <p className="text-slate-400 mb-4">Status snapshots, health checks, RPC explorer</p>
            <div className="flex items-center gap-2 text-red-400 group-hover:gap-3 transition-all">
              <span className="text-sm">Debug Tools</span>
              <ExternalLink className="w-4 h-4" />
            </div>
          </button>
        </div>

        {/* Info Banner */}
        <div className="bg-gradient-to-r from-blue-900/50 to-purple-900/50 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/30">
          <div className="flex items-start gap-4">
            <Terminal className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg font-semibold mb-2">Native OpenClaw Control UI</h3>
              <p className="text-slate-300 mb-3">
                The native Control UI provides full access to all OpenClaw features including chat, channel management, 
                cron jobs, skills, configuration, and debugging tools. Click "Open Native Control UI" to access the 
                complete interface.
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-slate-700/50 rounded-full text-sm">WebSocket Chat</span>
                <span className="px-3 py-1 bg-slate-700/50 rounded-full text-sm">Real-time Events</span>
                <span className="px-3 py-1 bg-slate-700/50 rounded-full text-sm">Config Editor</span>
                <span className="px-3 py-1 bg-slate-700/50 rounded-full text-sm">Live Logs</span>
                <span className="px-3 py-1 bg-slate-700/50 rounded-full text-sm">Device Pairing</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OpenClawControlUI;
