import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { 
  Search, 
  Zap, 
  Package, 
  Database, 
  Cpu, 
  Loader2,
  ExternalLink,
  DollarSign,
  Key,
  Code
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const DiscoveryDashboard = () => {
  const [query, setQuery] = useState('');
  const [resourceType, setResourceType] = useState('api');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [selectedPreset, setSelectedPreset] = useState(null);

  const resourceTypes = [
    { id: 'api', label: 'APIs', icon: Database },
    { id: 'ai_service', label: 'AI Services', icon: Cpu },
    { id: 'mcp_server', label: 'MCP Servers', icon: Package },
  ];

  const presets = [
    { id: 'payment-apis', label: 'Payment APIs', icon: '💳', endpoint: '/presets/payment-apis' },
    { id: 'ai-image-generation', label: 'AI Image Gen', icon: '🎨', endpoint: '/presets/ai-image-generation' },
    { id: 'llm-apis', label: 'LLM APIs', icon: '🧠', endpoint: '/presets/llm-apis' },
    { id: 'communication-apis', label: 'Communication', icon: '📧', endpoint: '/presets/communication-apis' },
  ];

  const discoverResources = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setResults(null);
    
    try {
      const response = await fetch(`${API}/api/discovery/full-discovery`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, resource_type: resourceType })
      });
      
      const data = await response.json();
      setResults(data.data);
    } catch (error) {
      console.error('Discovery failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = async (preset) => {
    setLoading(true);
    setResults(null);
    setSelectedPreset(preset.id);
    
    try {
      const response = await fetch(`${API}/api/discovery${preset.endpoint}`);
      const data = await response.json();
      setResults(data.data);
    } catch (error) {
      console.error('Preset discovery failed:', error);
    } finally {
      setLoading(false);
      setSelectedPreset(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Discovery Search */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="w-5 h-5 text-blue-500" />
            Automated Resource Discovery
          </CardTitle>
          <CardDescription>
            Automatically find, scrape, and catalog integrations, APIs, AI services, and tools
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Resource Type Selector */}
          <div className="flex gap-2">
            {resourceTypes.map((type) => (
              <Button
                key={type.id}
                variant={resourceType === type.id ? 'default' : 'outline'}
                onClick={() => setResourceType(type.id)}
                className="flex-1"
              >
                <type.icon className="w-4 h-4 mr-2" />
                {type.label}
              </Button>
            ))}
          </div>

          {/* Search Input */}
          <div className="flex gap-2">
            <Input
              placeholder="Search for resources (e.g., 'payment APIs', 'AI image generation')..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && discoverResources()}
            />
            <Button
              onClick={discoverResources}
              disabled={loading || !query.trim()}
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
            </Button>
          </div>

          {/* Quick Presets */}
          <div>
            <p className="text-sm text-gray-600 mb-2">Quick Discover:</p>
            <div className="flex flex-wrap gap-2">
              {presets.map((preset) => (
                <Button
                  key={preset.id}
                  variant="outline"
                  size="sm"
                  onClick={() => applyPreset(preset)}
                  disabled={loading}
                >
                  <span className="mr-2">{preset.icon}</span>
                  {preset.label}
                  {selectedPreset === preset.id && (
                    <Loader2 className="w-3 h-3 ml-2 animate-spin" />
                  )}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      {results && (
        <Card>
          <CardHeader>
            <CardTitle>
              Discovery Results
              <Badge className="ml-2">
                {results.total_discovered || 0} found
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {/* Enriched Results (with details) */}
            {results.enriched_results && results.enriched_results.length > 0 && (
              <div className="space-y-4 mb-6">
                <h3 className="font-semibold text-lg">Top Results (Detailed)</h3>
                {results.enriched_results.map((resource, idx) => (
                  <Card key={idx} className="border-l-4 border-l-blue-500">
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h4 className="font-semibold text-lg">{resource.name}</h4>
                          <a 
                            href={resource.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                          >
                            {resource.url}
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                        <Badge variant="outline">{resource.type}</Badge>
                      </div>

                      {resource.description && (
                        <p className="text-sm text-gray-600 mb-4">{resource.description}</p>
                      )}

                      {/* Details from scraping */}
                      {resource.details && !resource.details.error && (
                        <div className="grid md:grid-cols-2 gap-4 mt-4">
                          {/* Pricing */}
                          {resource.details.pricing && resource.details.pricing.length > 0 && (
                            <div>
                              <div className="flex items-center gap-2 mb-2">
                                <DollarSign className="w-4 h-4 text-green-500" />
                                <span className="font-medium text-sm">Pricing</span>
                              </div>
                              <div className="space-y-1">
                                {resource.details.pricing.slice(0, 3).map((price, i) => (
                                  <Badge key={i} variant="outline" className="mr-1">
                                    {price}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Authentication */}
                          {resource.details.authentication && resource.details.authentication.length > 0 && (
                            <div>
                              <div className="flex items-center gap-2 mb-2">
                                <Key className="w-4 h-4 text-yellow-500" />
                                <span className="font-medium text-sm">Auth Methods</span>
                              </div>
                              <div className="space-y-1">
                                {resource.details.authentication.map((auth, i) => (
                                  <Badge key={i} variant="outline" className="mr-1">
                                    {auth}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Features */}
                          {resource.details.features && resource.details.features.length > 0 && (
                            <div className="md:col-span-2">
                              <div className="flex items-center gap-2 mb-2">
                                <Zap className="w-4 h-4 text-purple-500" />
                                <span className="font-medium text-sm">Features</span>
                              </div>
                              <div className="space-y-1">
                                {resource.details.features.slice(0, 5).map((feature, i) => (
                                  <div key={i} className="text-sm text-gray-600">
                                    • {feature}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* API Endpoints */}
                          {resource.details.api_endpoints && resource.details.api_endpoints.length > 0 && (
                            <div className="md:col-span-2">
                              <div className="flex items-center gap-2 mb-2">
                                <Code className="w-4 h-4 text-blue-500" />
                                <span className="font-medium text-sm">API Endpoints</span>
                              </div>
                              <div className="space-y-1">
                                {resource.details.api_endpoints.slice(0, 5).map((endpoint, i) => (
                                  <code key={i} className="text-xs bg-gray-100 px-2 py-1 rounded block">
                                    {endpoint}
                                  </code>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}

            {/* All Results Summary */}
            {results.all_results && results.all_results.length > 5 && (
              <div>
                <h3 className="font-semibold text-lg mb-3">All Discovered Resources</h3>
                <div className="grid md:grid-cols-2 gap-3">
                  {results.all_results.slice(5).map((resource, idx) => (
                    <Card key={idx} className="border">
                      <CardContent className="pt-4">
                        <h4 className="font-medium mb-1">{resource.name}</h4>
                        <a 
                          href={resource.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                        >
                          View
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {loading && !results && (
        <Card>
          <CardContent className="pt-6 text-center">
            <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-500" />
            <p className="text-gray-600">Discovering and scraping resources...</p>
            <p className="text-sm text-gray-400 mt-2">
              This may take 10-30 seconds
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DiscoveryDashboard;
