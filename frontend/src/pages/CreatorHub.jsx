import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card } from '@/components/ui/card';
import {
  User,
  Search,
  Sparkles,
  DollarSign,
  TrendingUp
} from 'lucide-react';

import CreatorPortfolio from '@/components/creator/CreatorPortfolio';
import MarketplaceSearch from '@/components/creator/MarketplaceSearch';
import AIRecommendations from '@/components/creator/AIRecommendations';
import RevenueAnalytics from '@/components/creator/RevenueAnalytics';

const CreatorHub = () => {
  const [activeTab, setActiveTab] = useState('portfolio');

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Creator Hub</h1>
          <p className="text-lg text-gray-600">
            Manage your portfolio, discover tools, and track your success
          </p>
        </div>

        {/* Tabs Navigation */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:inline-grid">
            <TabsTrigger value="portfolio" className="flex items-center gap-2">
              <User className="w-4 h-4" />
              <span className="hidden sm:inline">Portfolio</span>
            </TabsTrigger>
            <TabsTrigger value="marketplace" className="flex items-center gap-2">
              <Search className="w-4 h-4" />
              <span className="hidden sm:inline">Marketplace</span>
            </TabsTrigger>
            <TabsTrigger value="recommendations" className="flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              <span className="hidden sm:inline">AI Picks</span>
            </TabsTrigger>
            <TabsTrigger value="revenue" className="flex items-center gap-2">
              <DollarSign className="w-4 h-4" />
              <span className="hidden sm:inline">Revenue</span>
            </TabsTrigger>
          </TabsList>

          {/* Portfolio Tab */}
          <TabsContent value="portfolio" className="space-y-6">
            <CreatorPortfolio />
          </TabsContent>

          {/* Marketplace Tab */}
          <TabsContent value="marketplace" className="space-y-6">
            <MarketplaceSearch />
          </TabsContent>

          {/* Recommendations Tab */}
          <TabsContent value="recommendations" className="space-y-6">
            <AIRecommendations />
          </TabsContent>

          {/* Revenue Tab */}
          <TabsContent value="revenue" className="space-y-6">
            <RevenueAnalytics />
          </TabsContent>
        </Tabs>

        {/* Quick Stats Card (Visible on all tabs) */}
        <Card className="mt-8 bg-gradient-to-r from-blue-500 to-purple-600 text-white">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-6 h-6" />
              <h3 className="text-xl font-bold">Creator Platform Stats</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <p className="text-blue-100 text-sm mb-1">Portfolio Items</p>
                <p className="text-3xl font-bold">--</p>
              </div>
              <div>
                <p className="text-blue-100 text-sm mb-1">Tools Discovered</p>
                <p className="text-3xl font-bold">5</p>
              </div>
              <div>
                <p className="text-blue-100 text-sm mb-1">Total Revenue</p>
                <p className="text-3xl font-bold">$--</p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default CreatorHub;
