import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Target, TrendingUp, Zap } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AIRecommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/creator/recommendations?limit=6`);
      const data = await response.json();
      setRecommendations(data.recommendations || []);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const trackInteraction = async (toolId) => {
    try {
      await fetch(`${API_URL}/api/creator/track-interaction/${toolId}`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Failed to track interaction:', error);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-blue-600';
    return 'text-gray-600';
  };

  const getScoreBadge = (score) => {
    if (score >= 0.8) return { text: 'Perfect Match', color: 'default' };
    if (score >= 0.6) return { text: 'Good Match', color: 'secondary' };
    return { text: 'Suggested', color: 'outline' };
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Sparkles className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">AI-Powered Recommendations</h2>
            <p className="text-sm text-gray-600">Personalized tool suggestions based on your preferences</p>
          </div>
        </div>
        <Button onClick={loadRecommendations} variant="outline" disabled={loading}>
          {loading ? 'Loading...' : 'Refresh'}
        </Button>
      </div>

      {/* Recommendations Grid */}
      {recommendations.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recommendations.map((rec, idx) => {
            const scoreBadge = getScoreBadge(rec.score);
            return (
              <Card key={idx} className="hover:shadow-lg transition-all border-l-4 border-l-purple-500">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <Badge variant={scoreBadge.color} className="mb-2">
                        {scoreBadge.text}
                      </Badge>
                      <CardTitle className="text-lg">{rec.tool_name}</CardTitle>
                    </div>
                    <div className={`text-2xl font-bold ${getScoreColor(rec.score)}`}>
                      {Math.round(rec.score * 100)}%
                    </div>
                  </div>
                  <CardDescription className="mt-2 flex items-start gap-2">
                    <Target className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    <span>{rec.reason}</span>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {rec.matched_preferences && rec.matched_preferences.length > 0 && (
                    <div className="mb-4">
                      <p className="text-xs font-semibold text-gray-600 mb-2">Matched Interests:</p>
                      <div className="flex flex-wrap gap-1">
                        {rec.matched_preferences.slice(0, 4).map((pref, i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            {pref}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  <Button
                    className="w-full"
                    variant="default"
                    onClick={() => trackInteraction(rec.tool_id)}
                  >
                    <Zap className="w-4 h-4 mr-2" />
                    View Tool
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : loading ? (
        <Card>
          <CardContent className="py-12 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-600">Analyzing your preferences...</p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <Sparkles className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-2">No recommendations yet</p>
            <p className="text-sm text-gray-500 mb-4">
              Interact with tools to get personalized suggestions
            </p>
            <Button onClick={loadRecommendations}>
              Generate Recommendations
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Info Card */}
      <Card className="bg-purple-50 border-purple-200">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <TrendingUp className="w-5 h-5 text-purple-600 mt-0.5" />
            <div>
              <p className="font-semibold text-purple-900">How it works</p>
              <p className="text-sm text-purple-700 mt-1">
                Our AI analyzes your interests, browsing history, and preferences to suggest tools 
                that perfectly match your needs. The more you interact, the better the recommendations become.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIRecommendations;
