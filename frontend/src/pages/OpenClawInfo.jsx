import React, { useState, useEffect } from 'react';
import { Activity, Code, Zap, Globe, GitBranch, Star, Users, Package, ExternalLink, CheckCircle, XCircle, Terminal } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const OpenClawInfo = () => {
  const [capabilities, setCapabilities] = useState(null);
  const [features, setFeatures] = useState(null);
  const [githubInfo, setGithubInfo] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOpenClawData();
  }, []);

  const fetchOpenClawData = async () => {
    try {
      const [capsRes, featRes, ghRes, healthRes] = await Promise.all([
        fetch(`${API}/api/openclaw/capabilities`),
        fetch(`${API}/api/openclaw/features`),
        fetch(`${API}/api/openclaw/github-info`),
        fetch(`${API}/api/openclaw/health`)
      ]);

      setCapabilities(await capsRes.json());
      setFeatures(await featRes.json());
      setGithubInfo(await ghRes.json());
      setHealth(await healthRes.json());
    } catch (error) {
      console.error('Failed to fetch OpenClaw data:', error);
    } finally {
      setLoading(false);
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
                OpenClaw Integration 🦞
              </h1>
              <p className="text-slate-300 text-lg">
                Your personal AI assistant integrated with Nexus AI Marketplace
              </p>
            </div>
            {health && (
              <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
                health.healthy ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
              }`}>
                {health.healthy ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
                <span className="font-medium">
                  {health.healthy ? 'Gateway Healthy' : 'Gateway Offline'}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* GitHub Info Card */}
        {githubInfo && (
          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 mb-8 border border-purple-500/20">
            <div className="flex items-center gap-3 mb-4">
              <GitBranch className="w-6 h-6 text-purple-400" />
              <h2 className="text-2xl font-bold">GitHub Repository</h2>
              <a
                href={githubInfo.repository.url}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-auto text-purple-400 hover:text-purple-300 flex items-center gap-2"
              >
                <ExternalLink className="w-4 h-4" />
                View on GitHub
              </a>
            </div>

            <p className="text-slate-300 mb-4">{githubInfo.repository.description}</p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-700/30 rounded-lg p-4">
                <div className="flex items-center gap-2 text-yellow-400 mb-2">
                  <Star className="w-4 h-4" />
                  <span className="text-sm">Stars</span>
                </div>
                <div className="text-2xl font-bold">{githubInfo.repository.stars}</div>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-4">
                <div className="flex items-center gap-2 text-blue-400 mb-2">
                  <Users className="w-4 h-4" />
                  <span className="text-sm">Contributors</span>
                </div>
                <div className="text-2xl font-bold">{githubInfo.repository.contributors}</div>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-4">
                <div className="flex items-center gap-2 text-green-400 mb-2">
                  <GitBranch className="w-4 h-4" />
                  <span className="text-sm">Forks</span>
                </div>
                <div className="text-2xl font-bold">{githubInfo.repository.forks}</div>
              </div>
              <div className="bg-slate-700/30 rounded-lg p-4">
                <div className="flex items-center gap-2 text-purple-400 mb-2">
                  <Package className="w-4 h-4" />
                  <span className="text-sm">Version</span>
                </div>
                <div className="text-xl font-bold">{githubInfo.repository.latest_version}</div>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-3 text-purple-400">Tech Stack</h3>
              <div className="flex flex-wrap gap-2">
                {Object.entries(githubInfo.tech_stack).map(([key, value]) => (
                  <span
                    key={key}
                    className="px-3 py-1 bg-slate-700/50 rounded-full text-sm text-slate-300"
                  >
                    {Array.isArray(value) ? value.join(', ') : value}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Capabilities Grid */}
        {capabilities && (
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/20">
              <div className="flex items-center gap-3 mb-4">
                <Code className="w-6 h-6 text-blue-400" />
                <h2 className="text-2xl font-bold">Coding Capabilities</h2>
              </div>
              <ul className="space-y-2">
                {capabilities.coding.map((cap, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
                    <span className="text-slate-300">{cap}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-green-500/20">
              <div className="flex items-center gap-3 mb-4">
                <Zap className="w-6 h-6 text-green-400" />
                <h2 className="text-2xl font-bold">Multimodal AI</h2>
              </div>
              <ul className="space-y-2">
                {capabilities.multimodal.map((cap, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
                    <span className="text-slate-300">{cap}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20">
              <div className="flex items-center gap-3 mb-4">
                <Activity className="w-6 h-6 text-purple-400" />
                <h2 className="text-2xl font-bold">Integrations</h2>
              </div>
              <ul className="space-y-2">
                {capabilities.integrations.map((cap, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
                    <span className="text-slate-300">{cap}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-pink-500/20">
              <div className="flex items-center gap-3 mb-4">
                <Globe className="w-6 h-6 text-pink-400" />
                <h2 className="text-2xl font-bold">Platforms</h2>
              </div>
              <ul className="space-y-2">
                {capabilities.platforms.map((cap, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
                    <span className="text-slate-300">{cap}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Nexus Integration Features */}
        {features && (
          <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/20 mb-8">
            <h2 className="text-2xl font-bold mb-4 text-purple-400">Nexus AI Integration Features</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold mb-3 text-blue-400">Gateway Features</h3>
                <ul className="space-y-2">
                  {features.gateway_features.map((feat, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
                      <span className="text-slate-300 text-sm">{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3 text-green-400">Nexus Integrations</h3>
                <ul className="space-y-2">
                  {features.nexus_integrations.map((feat, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
                      <span className="text-slate-300 text-sm">{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/30">
          <h2 className="text-2xl font-bold mb-4">Quick Actions</h2>
          <div className="grid md:grid-cols-4 gap-4">
            <a
              href="/openclaw-control"
              className="bg-slate-800/50 hover:bg-slate-700/50 rounded-lg p-4 flex items-center gap-3 transition-all"
            >
              <Terminal className="w-5 h-5 text-blue-400" />
              <div>
                <div className="font-semibold">Control UI</div>
                <div className="text-sm text-slate-400">Gateway management</div>
              </div>
            </a>
            <a
              href="/maintenance"
              className="bg-slate-800/50 hover:bg-slate-700/50 rounded-lg p-4 flex items-center gap-3 transition-all"
            >
              <Activity className="w-5 h-5 text-purple-400" />
              <div>
                <div className="font-semibold">O&M Dashboard</div>
                <div className="text-sm text-slate-400">Monitor gateway health</div>
              </div>
            </a>
            <a
              href="https://github.com/openclaw/openclaw"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-slate-800/50 hover:bg-slate-700/50 rounded-lg p-4 flex items-center gap-3 transition-all"
            >
              <GitBranch className="w-5 h-5 text-green-400" />
              <div>
                <div className="font-semibold">GitHub Repo</div>
                <div className="text-sm text-slate-400">View source code</div>
              </div>
            </a>
            <button
              onClick={fetchOpenClawData}
              className="bg-slate-800/50 hover:bg-slate-700/50 rounded-lg p-4 flex items-center gap-3 transition-all"
            >
              <Activity className="w-5 h-5 text-pink-400" />
              <div>
                <div className="font-semibold">Refresh Status</div>
                <div className="text-sm text-slate-400">Update information</div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OpenClawInfo;
