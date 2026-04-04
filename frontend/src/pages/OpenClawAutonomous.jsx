import React, { useState, useEffect } from 'react';
import { Zap, Play, Pause, Settings, Activity, Brain, Shield, Cog, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const OpenClawAutonomous = () => {
  const [status, setStatus] = useState(null);
  const [config, setConfig] = useState({
    enabled: true,
    thinking_mode: true,
    continuous_operation: true,
    auto_learn: true,
    auto_optimize: true,
    auto_heal: true,
    max_concurrent_tasks: 10,
    response_timeout: 300
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API}/api/openclaw/autonomous/status`);
      const data = await response.json();
      setStatus(data);
      if (data.config) {
        setConfig(data.config);
      }
    } catch (error) {
      console.error('Failed to fetch autonomous status:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleAutonomous = async () => {
    try {
      const endpoint = status?.enabled 
        ? `${API}/api/openclaw/autonomous/disable`
        : `${API}/api/openclaw/autonomous/enable`;
      
      const response = await fetch(endpoint, { method: 'POST' });
      const data = await response.json();
      
      if (data.success) {
        await fetchStatus();
      }
    } catch (error) {
      console.error('Failed to toggle autonomous mode:', error);
    }
  };

  const updateConfig = async () => {
    try {
      const response = await fetch(`${API}/api/openclaw/autonomous/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      
      const data = await response.json();
      if (data.success) {
        await fetchStatus();
      }
    } catch (error) {
      console.error('Failed to update config:', error);
    }
  };

  const triggerSelfHeal = async () => {
    try {
      const response = await fetch(`${API}/api/openclaw/autonomous/self-heal`, {
        method: 'POST'
      });
      const data = await response.json();
      alert(`Self-healing completed:\n${data.actions.join('\n')}`);
      await fetchStatus();
    } catch (error) {
      console.error('Failed to trigger self-heal:', error);
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
                Autonomous Agent Control 🤖
              </h1>
              <p className="text-slate-300 text-lg">
                Fully autonomous OpenClaw with self-management and intelligent decision-making
              </p>
            </div>
            <button
              onClick={toggleAutonomous}
              className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
                status?.enabled
                  ? 'bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700'
                  : 'bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700'
              }`}
            >
              {status?.enabled ? (
                <>
                  <Pause className="w-5 h-5" />
                  Disable Autonomous
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Enable Autonomous
                </>
              )}
            </button>
          </div>
        </div>

        {/* Status Overview */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20">
            <div className="flex items-center gap-3 mb-2">
              <Zap className="w-8 h-8 text-purple-400" />
              <div className="text-sm text-slate-400">Status</div>
            </div>
            <div className={`text-2xl font-bold ${status?.enabled ? 'text-green-400' : 'text-slate-400'}`}>
              {status?.enabled ? 'Active' : 'Inactive'}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Mode: {status?.mode || 'N/A'}
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/20">
            <div className="flex items-center gap-3 mb-2">
              <Activity className="w-8 h-8 text-blue-400" />
              <div className="text-sm text-slate-400">Tasks Executed</div>
            </div>
            <div className="text-2xl font-bold text-blue-400">
              {status?.stats?.total_tasks_executed || 0}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Success: {status?.stats?.successful_tasks || 0}
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-green-500/20">
            <div className="flex items-center gap-3 mb-2">
              <Shield className="w-8 h-8 text-green-400" />
              <div className="text-sm text-slate-400">Auto Heals</div>
            </div>
            <div className="text-2xl font-bold text-green-400">
              {status?.stats?.auto_heals || 0}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Self-healing events
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-yellow-500/20">
            <div className="flex items-center gap-3 mb-2">
              <Cog className="w-8 h-8 text-yellow-400" />
              <div className="text-sm text-slate-400">Uptime</div>
            </div>
            <div className="text-2xl font-bold text-yellow-400">
              {Math.floor((status?.stats?.uptime_seconds || 0) / 60)}m
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Autonomous mode
            </div>
          </div>
        </div>

        {/* Configuration Panel */}
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Settings className="w-6 h-6 text-purple-400" />
              <h2 className="text-2xl font-bold">Autonomous Configuration</h2>
            </div>
            <button
              onClick={updateConfig}
              className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg transition-all"
            >
              Save Configuration
            </button>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex items-center gap-3">
                  <Brain className="w-5 h-5 text-purple-400" />
                  <div>
                    <div className="font-medium">Thinking Mode</div>
                    <div className="text-xs text-slate-400">Enable reasoning for all tasks</div>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.thinking_mode}
                    onChange={(e) => setConfig({...config, thinking_mode: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-blue-400" />
                  <div>
                    <div className="font-medium">Continuous Operation</div>
                    <div className="text-xs text-slate-400">Never stop, always ready</div>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.continuous_operation}
                    onChange={(e) => setConfig({...config, continuous_operation: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex items-center gap-3">
                  <Brain className="w-5 h-5 text-green-400" />
                  <div>
                    <div className="font-medium">Auto-Learn</div>
                    <div className="text-xs text-slate-400">Learn from interactions</div>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.auto_learn}
                    onChange={(e) => setConfig({...config, auto_learn: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                </label>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex items-center gap-3">
                  <Cog className="w-5 h-5 text-yellow-400" />
                  <div>
                    <div className="font-medium">Auto-Optimize</div>
                    <div className="text-xs text-slate-400">Self-optimize performance</div>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.auto_optimize}
                    onChange={(e) => setConfig({...config, auto_optimize: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-yellow-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div className="flex items-center gap-3">
                  <Shield className="w-5 h-5 text-red-400" />
                  <div>
                    <div className="font-medium">Auto-Heal</div>
                    <div className="text-xs text-slate-400">Self-repair and recover</div>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.auto_heal}
                    onChange={(e) => setConfig({...config, auto_heal: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
                </label>
              </div>

              <div className="p-4 bg-slate-700/30 rounded-lg">
                <label className="block mb-2 font-medium">Max Concurrent Tasks</label>
                <input
                  type="number"
                  value={config.max_concurrent_tasks}
                  onChange={(e) => setConfig({...config, max_concurrent_tasks: parseInt(e.target.value)})}
                  className="w-full bg-slate-900/50 border border-purple-500/20 rounded-lg px-4 py-2 text-white"
                  min="1"
                  max="50"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20">
          <h2 className="text-2xl font-bold mb-4">Quick Actions</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <button
              onClick={triggerSelfHeal}
              className="bg-green-600 hover:bg-green-700 rounded-lg p-4 flex items-center gap-3 transition-all"
            >
              <Shield className="w-6 h-6" />
              <div className="text-left">
                <div className="font-semibold">Trigger Self-Heal</div>
                <div className="text-xs opacity-80">Run health check & repairs</div>
              </div>
            </button>

            <button
              onClick={fetchStatus}
              className="bg-blue-600 hover:bg-blue-700 rounded-lg p-4 flex items-center gap-3 transition-all"
            >
              <Activity className="w-6 h-6" />
              <div className="text-left">
                <div className="font-semibold">Refresh Status</div>
                <div className="text-xs opacity-80">Update statistics</div>
              </div>
            </button>

            <a
              href="/openclaw-chat"
              className="bg-purple-600 hover:bg-purple-700 rounded-lg p-4 flex items-center gap-3 transition-all"
            >
              <Brain className="w-6 h-6" />
              <div className="text-left">
                <div className="font-semibold">Chat with Agent</div>
                <div className="text-xs opacity-80">Interact with autonomous AI</div>
              </div>
            </a>
          </div>
        </div>

        {/* Features Info */}
        <div className="mt-8 bg-gradient-to-r from-purple-900/50 to-pink-900/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/30">
          <h3 className="text-lg font-semibold mb-3">Autonomous Features</h3>
          <div className="grid md:grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Continuous monitoring & operation</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Auto-response to channels</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Self-healing & recovery</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Automated task execution</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Intelligent decision making</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Learning from interactions</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Performance optimization</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span>Event-driven automation</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OpenClawAutonomous;
