import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { DollarSign, Building, PieChart } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const InvestmentResearch = () => {
  const [sector, setSector] = useState('');
  const [niche, setNiche] = useState('');
  const [loading, setLoading] = useState(false);
  const [research, setResearch] = useState(null);

  const researchInvestments = async () => {
    if (!sector.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/intelligence/investment/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sector })
      });
      
      const data = await response.json();
      setResearch(data);
    } catch (error) {
      console.error('Investment research failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeOpportunity = async () => {
    if (!niche.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/intelligence/investment/market-opportunity`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ niche })
      });
      
      const data = await response.json();
      setResearch(data);
    } catch (error) {
      console.error('Market opportunity analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-500" />
              Investment Research
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Sector (e.g., creator economy, AI tools)"
              value={sector}
              onChange={(e) => setSector(e.target.value)}
            />
            <Button
              onClick={researchInvestments}
              disabled={loading || !sector.trim()}
              className="w-full"
            >
              {loading ? 'Researching...' : 'Research Investments'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="w-5 h-5 text-blue-500" />
              Market Opportunities
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Niche (e.g., AI content creation)"
              value={niche}
              onChange={(e) => setNiche(e.target.value)}
            />
            <Button
              onClick={analyzeOpportunity}
              disabled={loading || !niche.trim()}
              className="w-full"
            >
              {loading ? 'Analyzing...' : 'Analyze Opportunity'}
            </Button>
          </CardContent>
        </Card>
      </div>

      {research && (
        <Card>
          <CardHeader>
            <CardTitle>Research Results</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto max-h-96">
              {JSON.stringify(research, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default InvestmentResearch;
