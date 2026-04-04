import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Target, TrendingUp, Users, DollarSign, Search, Lightbulb } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const MarketingIntelligence = () => {
  const [competitorName, setCompetitorName] = useState('');
  const [platform, setPlatform] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const analyzeCompetitor = async () => {
    if (!competitorName.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/intelligence/marketing/competitor-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ competitor_name: competitorName })
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Competitor analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeAdvertising = async () => {
    if (!platform.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/intelligence/marketing/advertising-intel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform })
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Advertising intelligence failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        {/* Competitor Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-500" />
              Competitive Analysis
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Enter competitor name (e.g., OnlyFans, Patreon)"
              value={competitorName}
              onChange={(e) => setCompetitorName(e.target.value)}
            />
            <Button
              onClick={analyzeCompetitor}
              disabled={loading || !competitorName.trim()}
              className="w-full"
            >
              {loading ? 'Analyzing...' : 'Analyze Competitor'}
            </Button>
          </CardContent>
        </Card>

        {/* Advertising Intel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-500" />
              Advertising Intelligence
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Enter platform name"
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
            />
            <Button
              onClick={analyzeAdvertising}
              disabled={loading || !platform.trim()}
              className="w-full"
            >
              {loading ? 'Researching...' : 'Research Ad Strategies'}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Results Display */}
      {results && (
        <Card>
          <CardHeader>
            <CardTitle>Intelligence Results</CardTitle>
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

export default MarketingIntelligence;
