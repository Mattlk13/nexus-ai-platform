import React, { useState } from 'react';
import { Sparkles, Code, Globe, Brain, Image, Wand2 } from 'lucide-react';

const HybridIntegrationsHub = () => {
  const [activeTab, setActiveTab] = useState('llm');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  // LLM Hub state
  const [llmModel, setLlmModel] = useState('default');
  const [llmPrompt, setLlmPrompt] = useState('');

  // Code Gen state
  const [codeTask, setCodeTask] = useState('');
  const [codeLang, setCodeLang] = useState('python');

  // Image Gen state
  const [imagePrompt, setImagePrompt] = useState('');
  const [imageStyle, setImageStyle] = useState('photorealistic');

  const API_URL = process.env.REACT_APP_BACKEND_URL;

  const availableModels = [
    { id: 'default', name: 'GPT-5.1', description: 'Default high-performance model', icon: '🤖' },
    { id: 'grok', name: 'Grok 4.20', description: 'xAI\'s advanced conversational model', icon: '🚀' },
    { id: 'qwen', name: 'Qwen 3.5', description: 'Alibaba\'s multilingual LLM', icon: '🌏' },
    { id: 'gpt-codex', name: 'GPT-Codex', description: 'Advanced code generation', icon: '💻' },
    { id: 'claude', name: 'Claude Sonnet 4', description: 'High-quality reasoning', icon: '🧠' },
    { id: 'gemini', name: 'Gemini 3 Pro', description: 'Multimodal AI', icon: '✨' },
  ];

  const handleLLMChat = async () => {
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch(`${API_URL}/api/hybrid/llm/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: llmPrompt,
          model: llmModel
        })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleCodeGeneration = async () => {
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch(`${API_URL}/api/hybrid/llm/code-generation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task: codeTask,
          language: codeLang
        })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const handleImageGeneration = async () => {
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch(`${API_URL}/api/hybrid/creative/generate-image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: imagePrompt,
          style: imageStyle
        })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const renderLLMHub = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">Multi-Model LLM Hub</h3>
        <p className="text-sm text-gray-400 mb-6">
          Chat with trending AI models: Grok, Qwen, GPT-5, Claude, Gemini
        </p>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
          {availableModels.map((model) => (
            <button
              key={model.id}
              onClick={() => setLlmModel(model.id)}
              className={`p-4 rounded-lg border-2 transition-all ${
                llmModel === model.id
                  ? 'border-blue-500 bg-blue-500/10'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              <div className="text-2xl mb-2">{model.icon}</div>
              <div className="font-semibold text-sm">{model.name}</div>
              <div className="text-xs text-gray-400 mt-1">{model.description}</div>
            </button>
          ))}
        </div>

        <textarea
          value={llmPrompt}
          onChange={(e) => setLlmPrompt(e.target.value)}
          placeholder="Enter your prompt..."
          className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500 resize-none"
          rows="4"
        />

        <button
          onClick={handleLLMChat}
          disabled={loading || !llmPrompt}
          className="mt-4 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Processing...' : `Chat with ${availableModels.find(m => m.id === llmModel)?.name}`}
        </button>
      </div>
    </div>
  );

  const renderCodeGen = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">
          <Code className="inline-block mr-2" size={20} />
          Code Generation (GPT-Codex)
        </h3>
        <p className="text-sm text-gray-400 mb-6">
          Generate production-ready code in any language
        </p>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Programming Language</label>
          <select
            value={codeLang}
            onChange={(e) => setCodeLang(e.target.value)}
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="go">Go</option>
            <option value="rust">Rust</option>
            <option value="java">Java</option>
          </select>
        </div>

        <textarea
          value={codeTask}
          onChange={(e) => setCodeTask(e.target.value)}
          placeholder="Describe what code you need... (e.g., Create a REST API for user authentication)"
          className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500 resize-none"
          rows="4"
        />

        <button
          onClick={handleCodeGeneration}
          disabled={loading || !codeTask}
          className="mt-4 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Generating...' : 'Generate Code'}
        </button>
      </div>
    </div>
  );

  const renderImageGen = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">
          <Image className="inline-block mr-2" size={20} />
          Image Generation (Nano Banana 2)
        </h3>
        <p className="text-sm text-gray-400 mb-6">
          Create stunning images with Gemini's Nano Banana model
        </p>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Image Style</label>
          <select
            value={imageStyle}
            onChange={(e) => setImageStyle(e.target.value)}
            className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
          >
            <option value="photorealistic">Photorealistic</option>
            <option value="artistic">Artistic</option>
            <option value="anime">Anime</option>
            <option value="abstract">Abstract</option>
            <option value="professional">Professional</option>
          </select>
        </div>

        <textarea
          value={imagePrompt}
          onChange={(e) => setImagePrompt(e.target.value)}
          placeholder="Describe the image you want to create..."
          className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500 resize-none"
          rows="4"
        />

        <button
          onClick={handleImageGeneration}
          disabled={loading || !imagePrompt}
          className="mt-4 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg font-semibold hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Creating...' : 'Generate Image'}
        </button>
      </div>
    </div>
  );

  const renderResult = () => {
    if (!result) return null;

    return (
      <div className="mt-8 p-6 bg-gray-800/50 border border-gray-700 rounded-lg">
        <h4 className="text-lg font-semibold mb-4">Result</h4>
        
        {result.success === false ? (
          <div className="text-red-400">
            <p className="font-semibold">Error:</p>
            <p>{result.error}</p>
          </div>
        ) : (
          <div className="space-y-4">
            {result.response && (
              <div>
                <p className="text-sm text-gray-400 mb-2">Response:</p>
                <div className="bg-gray-900 p-4 rounded-lg whitespace-pre-wrap font-mono text-sm">
                  {result.response}
                </div>
              </div>
            )}
            
            {result.images && result.images.length > 0 && (
              <div>
                <p className="text-sm text-gray-400 mb-2">Generated Images ({result.images_count}):</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {result.images.map((img, idx) => (
                    <div key={idx} className="border border-gray-700 rounded-lg p-4">
                      <img 
                        src={`data:${img.mime_type};base64,${img.full_data}`}
                        alt={`Generated ${idx}`}
                        className="w-full rounded-lg"
                      />
                      <p className="text-xs text-gray-500 mt-2">
                        {img.mime_type} • {(img.size_bytes / 1024).toFixed(1)}KB
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {result.model && (
              <div className="text-xs text-gray-500">
                Model: {result.model} • {new Date(result.timestamp).toLocaleString()}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="text-yellow-400" size={32} />
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              Hybrid AI Integrations
            </h1>
          </div>
          <p className="text-gray-400">
            Trending AI models integrated into NEXUS: Grok, Qwen, GPT-Codex, Claude, Gemini, Nano Banana
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-8 border-b border-gray-700">
          <button
            onClick={() => setActiveTab('llm')}
            className={`px-6 py-3 font-semibold transition-all ${
              activeTab === 'llm'
                ? 'border-b-2 border-blue-500 text-blue-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            <Brain className="inline-block mr-2" size={18} />
            LLM Hub
          </button>
          <button
            onClick={() => setActiveTab('code')}
            className={`px-6 py-3 font-semibold transition-all ${
              activeTab === 'code'
                ? 'border-b-2 border-green-500 text-green-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            <Code className="inline-block mr-2" size={18} />
            Code Gen
          </button>
          <button
            onClick={() => setActiveTab('image')}
            className={`px-6 py-3 font-semibold transition-all ${
              activeTab === 'image'
                ? 'border-b-2 border-purple-500 text-purple-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            <Wand2 className="inline-block mr-2" size={18} />
            Image Gen
          </button>
        </div>

        {/* Content */}
        <div className="bg-gray-800/30 border border-gray-700 rounded-lg p-8">
          {activeTab === 'llm' && renderLLMHub()}
          {activeTab === 'code' && renderCodeGen()}
          {activeTab === 'image' && renderImageGen()}
          
          {renderResult()}
        </div>

        {/* Info Footer */}
        <div className="mt-8 p-6 bg-blue-500/10 border border-blue-500/30 rounded-lg">
          <h3 className="font-semibold mb-2">🚀 About These Integrations</h3>
          <p className="text-sm text-gray-300">
            These are the trending AI models from aixploria.com, integrated as hybrid capabilities in NEXUS. 
            All models use the Emergent LLM Key for seamless access. Switch between models to leverage different AI strengths!
          </p>
        </div>
      </div>
    </div>
  );
};

export default HybridIntegrationsHub;
