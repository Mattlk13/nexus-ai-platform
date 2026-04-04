import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Input } from '../ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import {
  Code,
  Database,
  DollarSign,
  MessageSquare,
  TrendingUp,
  Bug,
  FileText,
  TestTube,
  CheckCircle,
  Loader2,
  AlertCircle,
  Zap
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const HybridAgentsHub = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('code-review');

  // Form states for each agent
  const [codeReviewForm, setCodeReviewForm] = useState({ code: '', language: 'python', pr_description: '' });
  const [dbOptForm, setDbOptForm] = useState({ query: '', database_type: 'postgresql', schema: '' });
  const [costOptForm, setCostOptForm] = useState({ platform: 'aws', current_cost: 0, resources: [] });
  const [supportForm, setSupportForm] = useState({ query: '', user_context: {}, conversation_history: [] });
  const [growthForm, setGrowthForm] = useState({ product: 'NEXUS Platform', target_audience: 'creators', current_metrics: {}, goals: 'increase user acquisition' });
  const [bugDetectForm, setBugDetectForm] = useState({ code: '', language: 'python', context: '' });
  const [docsForm, setDocsForm] = useState({ code: '', api_spec: '', doc_type: 'readme', style: 'clear and professional' });
  const [testForm, setTestForm] = useState({ code: '', language: 'python', test_framework: 'pytest', test_type: 'unit' });

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch(`${API_URL}/api/autonomous/hybrid/agents`);
      const data = await response.json();
      if (data.success) {
        setAgents(data.agents);
      }
    } catch (error) {
      console.error('Failed to fetch hybrid agents:', error);
    }
  };

  const runAgent = async (endpoint, payload) => {
    setLoading(true);
    setResult(null);
    
    try {
      const response = await fetch(`${API_URL}/api/autonomous/hybrid/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const AgentCard = ({ icon: Icon, title, description, status }) => (
    <div className="flex items-start gap-3 p-3 bg-slate-700/30 rounded-lg">
      <div className="p-2 bg-purple-600/20 rounded-lg">
        <Icon className="w-5 h-5 text-purple-400" />
      </div>
      <div className="flex-1">
        <h4 className="font-medium text-white">{title}</h4>
        <p className="text-sm text-slate-400">{description}</p>
        {status && (
          <Badge variant="outline" className="mt-2">
            {status.run_count || 0} runs
          </Badge>
        )}
      </div>
    </div>
  );

  const ResultDisplay = () => {
    if (!result) return null;
    
    return (
      <Alert className={result.success ? "bg-green-900/20 border-green-500" : "bg-red-900/20 border-red-500"}>
        <div className="flex items-start gap-2">
          {result.success ? (
            <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
          )}
          <div className="flex-1">
            <h4 className="font-semibold mb-2">
              {result.success ? 'Success' : 'Error'}
            </h4>
            <AlertDescription className="text-sm">
              <pre className="whitespace-pre-wrap overflow-auto max-h-96 bg-slate-950/50 p-4 rounded-lg">
                {JSON.stringify(result, null, 2)}
              </pre>
            </AlertDescription>
          </div>
        </div>
      </Alert>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          🤖 Hybrid AI Agents
        </h2>
        <p className="text-slate-400">
          Specialized AI agents for automation, optimization, and intelligent assistance
        </p>
      </div>

      {/* Agents Overview */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        <AgentCard 
          icon={Code}
          title="Code Review"
          description="Auto-review PRs"
          status={agents.find(a => a.agent_id === 'code-review')}
        />
        <AgentCard 
          icon={Database}
          title="DB Optimization"
          description="Tune queries"
          status={agents.find(a => a.agent_id === 'database-optimization')}
        />
        <AgentCard 
          icon={DollarSign}
          title="Cost Optimizer"
          description="Reduce costs"
          status={agents.find(a => a.agent_id === 'cost-optimization')}
        />
        <AgentCard 
          icon={MessageSquare}
          title="User Support"
          description="AI customer support"
          status={agents.find(a => a.agent_id === 'user-support')}
        />
        <AgentCard 
          icon={TrendingUp}
          title="Growth Hacking"
          description="Viral strategies"
          status={agents.find(a => a.agent_id === 'growth-hacking')}
        />
        <AgentCard 
          icon={Bug}
          title="Bug Detection"
          description="Find bugs automatically"
          status={agents.find(a => a.agent_id === 'bug-detection')}
        />
        <AgentCard 
          icon={FileText}
          title="Documentation"
          description="Auto-generate docs"
          status={agents.find(a => a.agent_id === 'documentation')}
        />
        <AgentCard 
          icon={TestTube}
          title="Testing"
          description="Auto-write tests"
          status={agents.find(a => a.agent_id === 'testing')}
        />
      </div>

      {/* Agent Interfaces */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-slate-800">
          <TabsTrigger value="code-review">Code Review</TabsTrigger>
          <TabsTrigger value="database">Database</TabsTrigger>
          <TabsTrigger value="cost">Cost</TabsTrigger>
          <TabsTrigger value="support">Support</TabsTrigger>
          <TabsTrigger value="growth">Growth</TabsTrigger>
          <TabsTrigger value="bugs">Bugs</TabsTrigger>
          <TabsTrigger value="docs">Docs</TabsTrigger>
          <TabsTrigger value="tests">Tests</TabsTrigger>
        </TabsList>

        {/* Code Review Tab */}
        <TabsContent value="code-review">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="w-5 h-5" />
                AI Code Review Agent
              </CardTitle>
              <CardDescription>
                Automatically review code for security, performance, and quality issues
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Code to Review</label>
                <Textarea
                  value={codeReviewForm.code}
                  onChange={(e) => setCodeReviewForm({ ...codeReviewForm, code: e.target.value })}
                  placeholder="Paste your code here..."
                  className="min-h-[200px] bg-slate-900 font-mono"
                />
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Language</label>
                  <Input
                    value={codeReviewForm.language}
                    onChange={(e) => setCodeReviewForm({ ...codeReviewForm, language: e.target.value })}
                    placeholder="python"
                    className="bg-slate-900"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">PR Description (Optional)</label>
                  <Input
                    value={codeReviewForm.pr_description}
                    onChange={(e) => setCodeReviewForm({ ...codeReviewForm, pr_description: e.target.value })}
                    placeholder="What does this code do?"
                    className="bg-slate-900"
                  />
                </div>
              </div>
              <Button
                onClick={() => runAgent('code-review', codeReviewForm)}
                disabled={loading || !codeReviewForm.code}
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Reviewing...
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4 mr-2" />
                    Review Code
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Database Optimization Tab */}
        <TabsContent value="database">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5" />
                Database Optimization Agent
              </CardTitle>
              <CardDescription>
                Optimize SQL queries and get index recommendations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">SQL Query</label>
                <Textarea
                  value={dbOptForm.query}
                  onChange={(e) => setDbOptForm({ ...dbOptForm, query: e.target.value })}
                  placeholder="SELECT * FROM users WHERE..."
                  className="min-h-[150px] bg-slate-900 font-mono"
                />
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Database Type</label>
                  <select
                    value={dbOptForm.database_type}
                    onChange={(e) => setDbOptForm({ ...dbOptForm, database_type: e.target.value })}
                    className="w-full p-2 bg-slate-900 border border-slate-700 rounded-md"
                  >
                    <option value="postgresql">PostgreSQL</option>
                    <option value="mysql">MySQL</option>
                    <option value="mongodb">MongoDB</option>
                    <option value="sqlite">SQLite</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Schema (Optional)</label>
                  <Textarea
                    value={dbOptForm.schema}
                    onChange={(e) => setDbOptForm({ ...dbOptForm, schema: e.target.value })}
                    placeholder="Table schemas..."
                    className="bg-slate-900"
                  />
                </div>
              </div>
              <Button
                onClick={() => runAgent('database-optimization', dbOptForm)}
                disabled={loading || !dbOptForm.query}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Zap className="w-4 h-4 mr-2" />}
                Optimize Query
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* User Support Tab */}
        <TabsContent value="support">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                AI Customer Support Agent
              </CardTitle>
              <CardDescription>
                Get AI-powered responses to customer queries
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Customer Query</label>
                <Textarea
                  value={supportForm.query}
                  onChange={(e) => setSupportForm({ ...supportForm, query: e.target.value })}
                  placeholder="How do I reset my password?"
                  className="min-h-[150px] bg-slate-900"
                />
              </div>
              <Button
                onClick={() => runAgent('user-support', supportForm)}
                disabled={loading || !supportForm.query}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Zap className="w-4 h-4 mr-2" />}
                Get AI Response
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Bug Detection Tab */}
        <TabsContent value="bugs">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bug className="w-5 h-5" />
                Bug Detection Agent
              </CardTitle>
              <CardDescription>
                Find bugs, vulnerabilities, and logic errors automatically
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Code to Analyze</label>
                <Textarea
                  value={bugDetectForm.code}
                  onChange={(e) => setBugDetectForm({ ...bugDetectForm, code: e.target.value })}
                  placeholder="Paste code to check for bugs..."
                  className="min-h-[200px] bg-slate-900 font-mono"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Language</label>
                <Input
                  value={bugDetectForm.language}
                  onChange={(e) => setBugDetectForm({ ...bugDetectForm, language: e.target.value })}
                  placeholder="python"
                  className="bg-slate-900"
                />
              </div>
              <Button
                onClick={() => runAgent('bug-detection', bugDetectForm)}
                disabled={loading || !bugDetectForm.code}
                className="w-full bg-red-600 hover:bg-red-700"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Zap className="w-4 h-4 mr-2" />}
                Detect Bugs
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Testing Agent Tab */}
        <TabsContent value="tests">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TestTube className="w-5 h-5" />
                Testing Agent
              </CardTitle>
              <CardDescription>
                Auto-generate comprehensive test cases
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Code to Test</label>
                <Textarea
                  value={testForm.code}
                  onChange={(e) => setTestForm({ ...testForm, code: e.target.value })}
                  placeholder="Paste code to generate tests for..."
                  className="min-h-[200px] bg-slate-900 font-mono"
                />
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Test Framework</label>
                  <select
                    value={testForm.test_framework}
                    onChange={(e) => setTestForm({ ...testForm, test_framework: e.target.value })}
                    className="w-full p-2 bg-slate-900 border border-slate-700 rounded-md"
                  >
                    <option value="pytest">pytest</option>
                    <option value="unittest">unittest</option>
                    <option value="jest">jest</option>
                    <option value="mocha">mocha</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Test Type</label>
                  <select
                    value={testForm.test_type}
                    onChange={(e) => setTestForm({ ...testForm, test_type: e.target.value })}
                    className="w-full p-2 bg-slate-900 border border-slate-700 rounded-md"
                  >
                    <option value="unit">Unit Tests</option>
                    <option value="integration">Integration Tests</option>
                    <option value="e2e">E2E Tests</option>
                  </select>
                </div>
              </div>
              <Button
                onClick={() => runAgent('testing', testForm)}
                disabled={loading || !testForm.code}
                className="w-full bg-indigo-600 hover:bg-indigo-700"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Zap className="w-4 h-4 mr-2" />}
                Generate Tests
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Additional tabs abbreviated for brevity - similar structure */}
        <TabsContent value="cost">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle>Cost Optimization Agent</CardTitle>
              <CardDescription>Reduce cloud infrastructure costs</CardDescription>
            </CardHeader>
            <CardContent className="text-slate-400 text-sm">
              Coming soon - Enter current costs and get optimization recommendations
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="growth">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle>Growth Hacking Agent</CardTitle>
              <CardDescription>Generate viral marketing strategies</CardDescription>
            </CardHeader>
            <CardContent className="text-slate-400 text-sm">
              Coming soon - Get data-driven growth tactics and viral campaigns
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="docs">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle>Documentation Agent</CardTitle>
              <CardDescription>Auto-generate comprehensive documentation</CardDescription>
            </CardHeader>
            <CardContent className="text-slate-400 text-sm">
              Coming soon - Generate README, API docs, and usage guides
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Result Display */}
      {result && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-3">Agent Response</h3>
          <ResultDisplay />
        </div>
      )}
    </div>
  );
};

export default HybridAgentsHub;
