import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Search, User, Globe, FileText } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const ResearchHub = () => {
  const [creatorName, setCreatorName] = useState('');
  const [url, setUrl] = useState('');
  const [topic, setTopic] = useState('');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const researchCreator = async () => {
    if (!creatorName.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/intelligence/research/creator`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ creator_name: creatorName })
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Creator research failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const extractData = async () => {
    if (!url.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/intelligence/research/extract-data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Data extraction failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const discoverContent = async () => {
    if (!topic.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/intelligence/research/discover-content`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, content_type: 'articles' })
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Content discovery failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const askIntelligence = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/intelligence/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Intelligence query failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        {/* Creator Research */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5 text-purple-500" />
              Creator Research
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Creator/influencer name"
              value={creatorName}
              onChange={(e) => setCreatorName(e.target.value)}
            />
            <Button
              onClick={researchCreator}
              disabled={loading || !creatorName.trim()}
              className="w-full"
            >
              {loading ? 'Researching...' : 'Research Creator'}
            </Button>
          </CardContent>
        </Card>

        {/* Data Extraction */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="w-5 h-5 text-blue-500" />
              Data Extraction
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="https://competitor-website.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
            <Button
              onClick={extractData}
              disabled={loading || !url.trim()}
              className="w-full"
            >
              {loading ? 'Extracting...' : 'Extract Data'}
            </Button>
          </CardContent>
        </Card>

        {/* Content Discovery */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-green-500" />
              Content Discovery
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Topic (e.g., creator tools)"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
            <Button
              onClick={discoverContent}
              disabled={loading || !topic.trim()}
              className="w-full"
            >
              {loading ? 'Discovering...' : 'Discover Content'}
            </Button>
          </CardContent>
        </Card>

        {/* Ask Intelligence */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="w-5 h-5 text-orange-500" />
              Ask Intelligence
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="Ask any business intelligence question..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              rows={3}
            />
            <Button
              onClick={askIntelligence}
              disabled={loading || !query.trim()}
              className="w-full"
            >
              {loading ? 'Thinking...' : 'Ask Intelligence'}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Results Display */}
      {results && (
        <Card>
          <CardHeader>
            <CardTitle>Research Results</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto max-h-96">
              {JSON.stringify(results, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ResearchHub;
