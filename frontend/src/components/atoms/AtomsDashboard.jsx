import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import {
  Search,
  FileText,
  Boxes,
  TrendingUp,
  BarChart3,
  Users,
  Zap,
  Loader2,
  CheckCircle,
  Rocket
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AtomsDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [task, setTask] = useState('');
  const [activeTab, setActiveTab] = useState('iris');

  const agents = [
    { id: 'iris', name: 'Iris', role: 'Deep Researcher', icon: Search, color: 'purple' },
    { id: 'emma', name: 'Emma', role: 'Product Manager', icon: FileText, color: 'blue' },
    { id: 'bob', name: 'Bob', role: 'Architect', icon: Boxes, color: 'green' },
    { id: 'sarah', name: 'Sarah', role: 'SEO Specialist', icon: TrendingUp, color: 'orange' },
    { id: 'david', name: 'David', role: 'Data Analyst', icon: BarChart3, color: 'pink' }
  ];

  const runAgent = async (agentId) => {
    if (!task.trim()) return;
    
    setLoading(true);
    setResult(null);
    
    try {
      const response = await fetch(`${API_URL}/api/atoms/agents/${agentId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task, context: {} })
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const runFullWorkflow = async () => {
    if (!task.trim()) return;
    
    setLoading(true);
    setResult(null);
    
    try {
      const response = await fetch(`${API_URL}/api/atoms/workflow`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project: task, context: {} })
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const runRaceMode = async () => {
    if (!task.trim()) return;
    
    setLoading(true);
    setResult(null);
    
    try {
      const response = await fetch(`${API_URL}/api/atoms/race-mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: task, model_count: 3 })
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
          🚀 Atoms AI Team
        </h2>
        <p className="text-slate-400">
          Multi-agent AI system for research, product management, architecture, SEO, and analytics
        </p>
      </div>

      {/* Agents Overview */}
      <div className="grid md:grid-cols-3 lg:grid-cols-5 gap-4">
        {agents.map((agent) => {
          const Icon = agent.icon;
          return (
            <Card key={agent.id} className="bg-slate-800/50 border-slate-700 cursor-pointer hover:border-purple-500 transition-colors" onClick={() => setActiveTab(agent.id)}>
              <CardContent className="p-4 flex flex-col items-center text-center">
                <div className={`p-3 bg-${agent.color}-600/20 rounded-lg mb-2`}>
                  <Icon className={`w-6 h-6 text-${agent.color}-400`} />
                </div>
                <h4 className="font-semibold text-white mb-1">{agent.name}</h4>
                <p className="text-xs text-slate-400">{agent.role}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Main Interface */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-slate-800">
          <TabsTrigger value="iris">Iris</TabsTrigger>
          <TabsTrigger value="emma">Emma</TabsTrigger>
          <TabsTrigger value="bob">Bob</TabsTrigger>
          <TabsTrigger value="sarah">Sarah</TabsTrigger>
          <TabsTrigger value="david">David</TabsTrigger>
          <TabsTrigger value="workflow">Full Workflow</TabsTrigger>
          <TabsTrigger value="race">Race Mode</TabsTrigger>
        </TabsList>

        {/* Iris Tab */}
        <TabsContent value="iris">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="w-5 h-5 text-purple-400" />
                Iris - Deep Research Agent
              </CardTitle>
              <CardDescription>
                Market research, demand analysis, and opportunity identification
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="What market or topic should Iris research? (e.g., 'AI productivity tools for developers')"
                className="min-h-[120px] bg-slate-900"
              />
              <Button
                onClick={() => runAgent('iris')}
                disabled={loading || !task}
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Search className="w-4 h-4 mr-2" />}
                Research Market
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Emma Tab */}
        <TabsContent value="emma">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-400" />
                Emma - Product Manager
              </CardTitle>
              <CardDescription>
                Turn ideas into clear specifications and scope
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="Describe your product idea... (e.g., 'A scheduling app for remote teams')"
                className="min-h-[120px] bg-slate-900"
              />
              <Button
                onClick={() => runAgent('emma')}
                disabled={loading || !task}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <FileText className="w-4 h-4 mr-2" />}
                Create Product Spec
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Bob Tab */}
        <TabsContent value="bob">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Boxes className="w-5 h-5 text-green-400" />
                Bob - Systems Architect
              </CardTitle>
              <CardDescription>
                Design scalable system architecture and tech stack
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="Describe your system requirements... (e.g., 'Real-time chat platform with 10k concurrent users')"
                className="min-h-[120px] bg-slate-900"
              />
              <Button
                onClick={() => runAgent('bob')}
                disabled={loading || !task}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Boxes className="w-4 h-4 mr-2" />}
                Design Architecture
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Sarah Tab */}
        <TabsContent value="sarah">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-orange-400" />
                Sarah - SEO Specialist
              </CardTitle>
              <CardDescription>
                SEO strategy, keyword research, and content optimization
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="What website/page needs SEO optimization? (e.g., 'E-commerce site selling handmade jewelry')"
                className="min-h-[120px] bg-slate-900"
              />
              <Button
                onClick={() => runAgent('sarah')}
                disabled={loading || !task}
                className="w-full bg-orange-600 hover:bg-orange-700"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <TrendingUp className="w-4 h-4 mr-2" />}
                Generate SEO Strategy
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* David Tab */}
        <TabsContent value="david">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-pink-400" />
                David - Data Analyst
              </CardTitle>
              <CardDescription>
                Data analysis, insights, and trend identification
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="What data should David analyze? (e.g., 'User engagement metrics for mobile app')"
                className="min-h-[120px] bg-slate-900"
              />
              <Button
                onClick={() => runAgent('david')}
                disabled={loading || !task}
                className="w-full bg-pink-600 hover:bg-pink-700"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <BarChart3 className="w-4 h-4 mr-2" />}
                Analyze Data
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Full Workflow Tab */}
        <TabsContent value="workflow">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-indigo-400" />
                Mike - Full Multi-Agent Workflow
              </CardTitle>
              <CardDescription>
                Complete end-to-end project: Research → Spec → Architecture → SEO → Analytics
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert className="bg-indigo-900/20 border-indigo-500">
                <Rocket className="w-4 h-4 text-indigo-400" />
                <AlertDescription className="text-sm text-slate-300 ml-2">
                  This runs all 5 agents in sequence: Iris, Emma, Bob, Sarah, and David. Takes 2-3 minutes.
                </AlertDescription>
              </Alert>
              <Textarea
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="Describe your complete project... (e.g., 'Build a SaaS platform for freelance designers')"
                className="min-h-[120px] bg-slate-900"
              />
              <Button
                onClick={runFullWorkflow}
                disabled={loading || !task}
                className="w-full bg-indigo-600 hover:bg-indigo-700"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Rocket className="w-4 h-4 mr-2" />}
                Run Full Workflow
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Race Mode Tab */}
        <TabsContent value="race">
          <Card className="bg-slate-800/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                Race Mode - Multiple Solutions
              </CardTitle>
              <CardDescription>
                Generate 3 solutions in parallel and compare them
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert className="bg-yellow-900/20 border-yellow-500">
                <Zap className="w-4 h-4 text-yellow-400" />
                <AlertDescription className="text-sm text-slate-300 ml-2">
                  Generates multiple solutions simultaneously for you to compare and pick the best.
                </AlertDescription>
              </Alert>
              <Textarea
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="What problem needs multiple solution approaches? (e.g., 'How to reduce app loading time')"
                className="min-h-[120px] bg-slate-900"
              />
              <Button
                onClick={runRaceMode}
                disabled={loading || !task}
                className="w-full bg-yellow-600 hover:bg-yellow-700"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Zap className="w-4 h-4 mr-2" />}
                Run Race Mode
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Results Display */}
      {result && (
        <Card className="bg-slate-800/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {result.success ? (
                <CheckCircle className="w-5 h-5 text-green-500" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-500" />
              )}
              {result.success ? 'Results' : 'Error'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-slate-950 p-4 rounded-lg overflow-auto max-h-96 text-sm">
              {JSON.stringify(result, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AtomsDashboard;
