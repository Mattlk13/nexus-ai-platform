import React, { useState, useEffect } from 'react';
import { Settings, Shield, Webhook, Key, Globe, Save, Download, Upload, CheckCircle, AlertTriangle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const OpenClawSettings = () => {
  const [activeTab, setActiveTab] = useState('webhooks');
  const [webhookConfig, setWebhookConfig] = useState({
    enabled: false,
    url: '',
    secret: '',
    events: ['chat.message', 'cron.run', 'error']
  });
  const [authInfo, setAuthInfo] = useState(null);
  const [allowedOrigins, setAllowedOrigins] = useState([]);
  const [newOrigin, setNewOrigin] = useState('');
  const [loading, setLoading] = useState(true);
  const [saveStatus, setSaveStatus] = useState(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const [webhooksRes, authRes, originsRes] = await Promise.all([
        fetch(`${API}/api/openclaw/web/webhooks/status`),
        fetch(`${API}/api/openclaw/web/security/auth-info`),
        fetch(`${API}/api/openclaw/web/security/allowed-origins`)
      ]);

      const webhooks = await webhooksRes.json();
      setWebhookConfig({
        enabled: webhooks.enabled || false,
        url: webhooks.url || '',
        secret: '',
        events: webhooks.events || ['chat.message', 'cron.run', 'error']
      });

      setAuthInfo(await authRes.json());
      
      const origins = await originsRes.json();
      setAllowedOrigins(origins.origins || []);
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveWebhooks = async () => {
    try {
      setSaveStatus('saving');
      const response = await fetch(`${API}/api/openclaw/web/webhooks/configure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(webhookConfig)
      });

      if (response.ok) {
        setSaveStatus('success');
        setTimeout(() => setSaveStatus(null), 3000);
      }
    } catch (error) {
      console.error('Failed to save webhooks:', error);
      setSaveStatus('error');
    }
  };

  const testWebhook = async () => {
    try {
      const response = await fetch(`${API}/api/openclaw/web/webhooks/test?url=${encodeURIComponent(webhookConfig.url)}&secret=${webhookConfig.secret}`, {
        method: 'POST'
      });

      const result = await response.json();
      alert(result.success ? `Test successful! Status: ${result.status_code}` : `Test failed: ${result.error}`);
    } catch (error) {
      alert(`Test failed: ${error.message}`);
    }
  };

  const addOrigin = async () => {
    if (!newOrigin.trim()) return;

    try {
      const response = await fetch(`${API}/api/openclaw/web/security/add-origin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ origin: newOrigin })
      });

      if (response.ok) {
        const result = await response.json();
        setAllowedOrigins(result.origins);
        setNewOrigin('');
      }
    } catch (error) {
      console.error('Failed to add origin:', error);
    }
  };

  const rotateToken = async () => {
    if (!confirm('Are you sure you want to rotate the gateway token? All clients will need to be updated.')) {
      return;
    }

    try {
      const response = await fetch(`${API}/api/openclaw/web/security/rotate-token`, {
        method: 'POST'
      });

      const result = await response.json();
      alert(`New token: ${result.new_token}\n\nPlease update all clients immediately!`);
      await fetchSettings();
    } catch (error) {
      alert(`Failed to rotate token: ${error.message}`);
    }
  };

  const exportConfig = async () => {
    try {
      const response = await fetch(`${API}/api/openclaw/web/config/export`, {
        method: 'POST'
      });

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `openclaw-config-${Date.now()}.json`;
      a.click();
    } catch (error) {
      alert(`Export failed: ${error.message}`);
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
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            OpenClaw Settings ⚙️
          </h1>
          <p className="text-slate-300 text-lg">
            Configure webhooks, security, and system preferences
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {[
            { id: 'webhooks', label: 'Webhooks', icon: Webhook },
            { id: 'security', label: 'Security', icon: Shield },
            { id: 'config', label: 'Configuration', icon: Settings }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                activeTab === tab.id
                  ? 'bg-purple-600 text-white'
                  : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Webhooks Tab */}
        {activeTab === 'webhooks' && (
          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">Webhook Configuration</h2>
              <button
                onClick={saveWebhooks}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg transition-all"
              >
                <Save className="w-4 h-4" />
                Save Changes
              </button>
            </div>

            <div className="space-y-6">
              <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                <div>
                  <div className="font-medium">Enable Webhooks</div>
                  <div className="text-xs text-slate-400">Send events to external URL</div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={webhookConfig.enabled}
                    onChange={(e) => setWebhookConfig({...webhookConfig, enabled: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>

              <div>
                <label className="block mb-2 font-medium">Webhook URL</label>
                <input
                  type="url"
                  value={webhookConfig.url}
                  onChange={(e) => setWebhookConfig({...webhookConfig, url: e.target.value})}
                  placeholder="https://your-server.com/webhook"
                  className="w-full bg-slate-900/50 border border-purple-500/20 rounded-lg px-4 py-3 text-white placeholder-slate-500"
                />
              </div>

              <div>
                <label className="block mb-2 font-medium">Secret (Optional)</label>
                <input
                  type="password"
                  value={webhookConfig.secret}
                  onChange={(e) => setWebhookConfig({...webhookConfig, secret: e.target.value})}
                  placeholder="Webhook secret for verification"
                  className="w-full bg-slate-900/50 border border-purple-500/20 rounded-lg px-4 py-3 text-white placeholder-slate-500"
                />
              </div>

              <div>
                <label className="block mb-2 font-medium">Events to Send</label>
                <div className="space-y-2">
                  {['chat.message', 'cron.run', 'error', 'session.start', 'session.end'].map(event => (
                    <label key={event} className="flex items-center gap-2 p-3 bg-slate-700/30 rounded-lg cursor-pointer hover:bg-slate-700/50">
                      <input
                        type="checkbox"
                        checked={webhookConfig.events.includes(event)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setWebhookConfig({...webhookConfig, events: [...webhookConfig.events, event]});
                          } else {
                            setWebhookConfig({...webhookConfig, events: webhookConfig.events.filter(e => e !== event)});
                          }
                        }}
                        className="form-checkbox h-4 w-4 text-purple-600"
                      />
                      <span className="text-sm">{event}</span>
                    </label>
                  ))}
                </div>
              </div>

              <button
                onClick={testWebhook}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg transition-all"
              >
                Test Webhook
              </button>
            </div>

            {saveStatus && (
              <div className={`mt-4 p-4 rounded-lg flex items-center gap-2 ${
                saveStatus === 'success' ? 'bg-green-500/20 text-green-400' :
                saveStatus === 'error' ? 'bg-red-500/20 text-red-400' :
                'bg-blue-500/20 text-blue-400'
              }`}>
                {saveStatus === 'success' && <CheckCircle className="w-5 h-5" />}
                {saveStatus === 'error' && <AlertTriangle className="w-5 h-5" />}
                <span>
                  {saveStatus === 'success' ? 'Settings saved successfully!' :
                   saveStatus === 'error' ? 'Failed to save settings' :
                   'Saving...'}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            {/* Auth Info */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20">
              <h2 className="text-2xl font-bold mb-4">Authentication</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                  <div>
                    <div className="font-medium">Auth Mode</div>
                    <div className="text-xs text-slate-400">Current authentication method</div>
                  </div>
                  <span className="px-3 py-1 bg-purple-600 rounded-full text-sm">
                    {authInfo?.mode || 'token'}
                  </span>
                </div>

                <div className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg">
                  <div>
                    <div className="font-medium">Gateway Token</div>
                    <div className="text-xs text-slate-400">
                      {authInfo?.tokenConfigured ? 'Configured' : 'Not configured'}
                    </div>
                  </div>
                  <button
                    onClick={rotateToken}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm transition-all"
                  >
                    <Key className="w-4 h-4 inline mr-2" />
                    Rotate Token
                  </button>
                </div>
              </div>
            </div>

            {/* Allowed Origins */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20">
              <h2 className="text-2xl font-bold mb-4">Allowed Origins</h2>
              
              <div className="mb-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newOrigin}
                    onChange={(e) => setNewOrigin(e.target.value)}
                    placeholder="https://example.com"
                    className="flex-1 bg-slate-900/50 border border-purple-500/20 rounded-lg px-4 py-2 text-white placeholder-slate-500"
                  />
                  <button
                    onClick={addOrigin}
                    className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-all"
                  >
                    Add Origin
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                {allowedOrigins.map((origin, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                    <span className="text-sm">{origin}</span>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  </div>
                ))}
                {allowedOrigins.length === 0 && (
                  <div className="text-center py-8 text-slate-500">
                    No allowed origins configured
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Configuration Tab */}
        {activeTab === 'config' && (
          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20">
            <h2 className="text-2xl font-bold mb-6">Configuration Management</h2>

            <div className="space-y-4">
              <button
                onClick={exportConfig}
                className="w-full flex items-center justify-center gap-3 p-4 bg-blue-600 hover:bg-blue-700 rounded-lg transition-all"
              >
                <Download className="w-5 h-5" />
                <span className="font-medium">Export Configuration</span>
              </button>

              <div className="p-4 bg-slate-700/30 rounded-lg">
                <div className="text-sm text-slate-400">
                  Export your complete OpenClaw configuration as JSON. This includes gateway settings, 
                  model providers, authentication, and all customizations.
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4 mt-6">
                <a
                  href="https://docs.openclaw.ai/gateway/configuration"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-4 bg-slate-700/30 hover:bg-slate-700/50 rounded-lg transition-all"
                >
                  <div className="font-medium mb-1">📚 Configuration Docs</div>
                  <div className="text-xs text-slate-400">View complete configuration reference</div>
                </a>

                <a
                  href="https://github.com/openclaw/openclaw"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-4 bg-slate-700/30 hover:bg-slate-700/50 rounded-lg transition-all"
                >
                  <div className="font-medium mb-1">🦞 GitHub Repository</div>
                  <div className="text-xs text-slate-400">Source code and examples</div>
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OpenClawSettings;
