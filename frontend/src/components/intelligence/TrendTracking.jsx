import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { TrendingUp, Activity, BarChart } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const TrendTracking = () => {
  const [topic, setTopic] = useState('');
  const [industry, setIndustry] = useState('creator economy');
  const [loading, setLoading] = useState(false);
  const [trends, setTrends] = useState(null);

  const analyzeTrends = async () => {
    if (!topic.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/intelligence/trends/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, industry })
      });
      
      const data = await response.json();
      setTrends(data);
    } catch (error) {
      console.error('Trend analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-500" />
            Trend Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <Input
              placeholder="Trend topic (e.g., AI tools, NFTs)"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
            <Input
              placeholder="Industry context"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
            />
          </div>
          <Button
            onClick={analyzeTrends}
            disabled={loading || !topic.trim()}
            className="w-full"
          >
            {loading ? 'Analyzing Trends...' : 'Analyze Trends'}
          </Button>
        </CardContent>
      </Card>

      {trends && (
        <Card>
          <CardHeader>
            <CardTitle>Trend Analysis Results</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto max-h-96">
              {JSON.stringify(trends, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default TrendTracking;
