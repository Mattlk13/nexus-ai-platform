import React, { useState } from 'react';
import { Zap, Target, Activity, Bot, Rocket, FlaskConical, Gauge, Settings as SettingsIcon } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const AutomationPanel = ({ onAutomationComplete, notifications }) => {
  const [loading, setLoading] = useState(null);
  const [autonomousEnabled, setAutonomousEnabled] = useState(false);

  const executeQuickAction = async (action, endpoint) => {
    setLoading(action);
    
    try {
      const response = await fetch(`${API}/api/openclaw/automation/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      const result = await response.json();
      
      if (result.success) {
        notifications?.success(
          `${action} Complete`,
          result.message || 'Action completed successfully'
        );
        onAutomationComplete?.(action, result);
      } else {
        notifications?.error(
          `${action} Failed`,
          result.message || 'Action failed'
        );
      }
    } catch (error) {
      console.error(`Failed to execute ${action}:`, error);
      notifications?.error(
        `${action} Error`,
        `Failed to execute: ${error.message}`
      );
    } finally {
      setLoading(null);
    }
  };

  const toggleAutonomous = async () => {
    const endpoint = autonomousEnabled ? 'disable-autonomous' : 'enable-autonomous';
    setLoading('autonomous');
    
    try {
      const response = await fetch(`${API}/api/openclaw/automation/${endpoint}`, {
        method: 'POST'
      });
      
      const result = await response.json();
      
      if (result.success) {
        setAutonomousEnabled(!autonomousEnabled);
        notifications?.success(
          autonomousEnabled ? 'Autonomous Disabled' : 'Autonomous Enabled',
          result.message
        );
        onAutomationComplete?.('autonomous-toggle', result);
      }
    } catch (error) {
      notifications?.error('Autonomous Toggle Failed', error.message);
    } finally {
      setLoading(null);
    }
  };

  const applyPreset = async (presetId, presetName) => {
    setLoading(presetId);
    
    try {
      const response = await fetch(`${API}/api/openclaw/automation/presets/${presetId}/apply`, {
        method: 'POST'
      });
      
      const result = await response.json();
      
      if (result.success) {
        notifications?.success(
          'Preset Applied',
          `${presetName} configuration activated`
        );
        onAutomationComplete?.('preset', result);
      }
    } catch (error) {
      notifications?.error('Preset Failed', error.message);
    } finally {
      setLoading(null);
    }
  };

  const quickActions = [
    {
      id: 'quick-start',
      title: 'Quick Start',
      description: 'Enable all features with optimal settings',
      icon: Rocket,
      color: 'from-blue-500 to-cyan-500',
      endpoint: 'quick-start'
    },
    {
      id: 'optimize-now',
      title: 'Optimize Now',
      description: 'Auto-configure best performance settings',
      icon: Target,
      color: 'from-purple-500 to-pink-500',
      endpoint: 'optimize-now'
    },
    {
      id: 'auto-heal-now',
      title: 'Auto-Heal',
      description: 'Diagnose and fix issues automatically',
      icon: Activity,
      color: 'from-green-500 to-emerald-500',
      endpoint: 'auto-heal-now'
    }
  ];

  const presets = [
    { id: 'development', name: 'Development', icon: FlaskConical, color: 'blue' },
    { id: 'production', name: 'Production', icon: Rocket, color: 'green' },
    { id: 'testing', name: 'Testing', icon: Gauge, color: 'yellow' }
  ];

  return (
    <div className="space-y-6">
      {/* Quick Actions */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-yellow-400" />
          Quick Actions
        </h3>
        <div className="grid md:grid-cols-3 gap-4">
          {quickActions.map((action) => (
            <button
              key={action.id}
              onClick={() => executeQuickAction(action.title, action.endpoint)}
              disabled={loading === action.title}
              className={`relative overflow-hidden bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700 rounded-xl p-6 text-left transition-all group disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${action.color} opacity-0 group-hover:opacity-10 transition-opacity`}></div>
              
              <div className="relative">
                <div className="flex items-center gap-3 mb-3">
                  <div className={`p-2 rounded-lg bg-gradient-to-br ${action.color}`}>
                    <action.icon className="w-5 h-5 text-white" />
                  </div>
                  <h4 className="font-semibold text-white">{action.title}</h4>
                </div>
                
                <p className="text-sm text-slate-400">{action.description}</p>
                
                {loading === action.title && (
                  <div className="mt-3 flex items-center gap-2 text-blue-400">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>
                    <span className="text-xs">Processing...</span>
                  </div>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Autonomous Mode Toggle */}
      <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 border border-purple-500/30 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-gradient-to-br from-purple-600 to-pink-600">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h4 className="font-semibold text-white mb-1">Autonomous Mode</h4>
              <p className="text-sm text-slate-400">
                {autonomousEnabled ? 'AI is self-managing and auto-responding' : 'Enable full autonomous operation'}
              </p>
            </div>
          </div>
          
          <button
            onClick={toggleAutonomous}
            disabled={loading === 'autonomous'}
            className={`relative inline-flex h-8 w-16 items-center rounded-full transition-colors disabled:opacity-50 ${
              autonomousEnabled ? 'bg-purple-600' : 'bg-slate-700'
            }`}
          >
            <span
              className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${
                autonomousEnabled ? 'translate-x-9' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
        
        {loading === 'autonomous' && (
          <div className="mt-3 flex items-center gap-2 text-purple-400">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-400"></div>
            <span className="text-xs">Configuring autonomous mode...</span>
          </div>
        )}
      </div>

      {/* Configuration Presets */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-slate-400" />
          Configuration Presets
        </h3>
        <div className="grid md:grid-cols-3 gap-3">
          {presets.map((preset) => (
            <button
              key={preset.id}
              onClick={() => applyPreset(preset.id, preset.name)}
              disabled={loading === preset.id}
              className={`bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700 rounded-lg p-4 text-left transition-all disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <div className="flex items-center gap-3">
                <preset.icon className={`w-5 h-5 text-${preset.color}-400`} />
                <span className="font-medium text-white">{preset.name}</span>
              </div>
              
              {loading === preset.id && (
                <div className="mt-2 flex items-center gap-2 text-blue-400">
                  <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-400"></div>
                  <span className="text-xs">Applying...</span>
                </div>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AutomationPanel;
