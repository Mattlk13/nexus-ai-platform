import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Filter, TrendingUp, Star, DollarSign } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const MarketplaceSearch = () => {
  const [tools, setTools] = useState([]);
  const [trending, setTrending] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    category: '',
    minPrice: '',
    maxPrice: '',
    ratingMin: '',
    sortBy: 'relevance'
  });

  useEffect(() => {
    loadTrendingTools();
    loadCategories();
  }, []);

  const loadTrendingTools = async () => {
    try {
      const response = await fetch(`${API_URL}/api/creator/marketplace/trending`);
      const data = await response.json();
      setTrending(data.tools || []);
    } catch (error) {
      console.error('Failed to load trending tools:', error);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await fetch(`${API_URL}/api/creator/marketplace/categories`);
      const data = await response.json();
      setCategories(data.categories || []);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append('query', searchQuery);
      if (filters.category) params.append('category', filters.category);
      if (filters.minPrice) params.append('min_price', filters.minPrice);
      if (filters.maxPrice) params.append('max_price', filters.maxPrice);
      if (filters.ratingMin) params.append('rating_min', filters.ratingMin);
      params.append('sort_by', filters.sortBy);

      const response = await fetch(`${API_URL}/api/creator/marketplace/search?${params}`);
      const data = await response.json();
      setTools(data.tools || []);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const ToolCard = ({ tool }) => (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <CardTitle className="text-lg">{tool.name}</CardTitle>
            <CardDescription className="mt-1">{tool.description}</CardDescription>
          </div>
          {tool.is_trending && (
            <Badge variant="default" className="ml-2">
              <TrendingUp className="w-3 h-3 mr-1" />
              Trending
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2 mb-3">
          <Badge variant="secondary">{tool.category}</Badge>
          {tool.tags?.slice(0, 3).map((tag, idx) => (
            <Badge key={idx} variant="outline">{tag}</Badge>
          ))}
        </div>
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-green-600">${tool.price}</span>
          </div>
          <div className="flex items-center gap-1 text-sm text-gray-600">
            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
            <span className="font-semibold">{tool.rating}</span>
            <span className="text-gray-400">({tool.total_reviews})</span>
          </div>
        </div>
        <Button className="w-full mt-4" variant="default">
          View Details
        </Button>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold">AI Tools Marketplace</h2>
        <p className="text-gray-600 mt-2">Discover and find the perfect AI tools for your needs</p>
      </div>

      {/* Search Bar */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1 flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="Search AI tools..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="pl-10"
                />
              </div>
              <Button onClick={handleSearch} disabled={loading}>
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </div>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3 mt-4">
            <select
              value={filters.category}
              onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              className="border rounded-md px-3 py-2 text-sm"
            >
              <option value="">All Categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>

            <Input
              type="number"
              placeholder="Min Price"
              value={filters.minPrice}
              onChange={(e) => setFilters({ ...filters, minPrice: e.target.value })}
              className="text-sm"
            />

            <Input
              type="number"
              placeholder="Max Price"
              value={filters.maxPrice}
              onChange={(e) => setFilters({ ...filters, maxPrice: e.target.value })}
              className="text-sm"
            />

            <Input
              type="number"
              placeholder="Min Rating"
              value={filters.ratingMin}
              onChange={(e) => setFilters({ ...filters, ratingMin: e.target.value })}
              step="0.1"
              max="5"
              className="text-sm"
            />

            <select
              value={filters.sortBy}
              onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
              className="border rounded-md px-3 py-2 text-sm"
            >
              <option value="relevance">Relevance</option>
              <option value="price_low">Price: Low to High</option>
              <option value="price_high">Price: High to Low</option>
              <option value="rating">Highest Rated</option>
              <option value="recent">Recently Added</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Trending Section */}
      {trending.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-orange-500" />
            <h3 className="text-xl font-semibold">Trending Tools</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {trending.map((tool) => (
              <ToolCard key={tool.id} tool={tool} />
            ))}
          </div>
        </div>
      )}

      {/* Search Results */}
      {tools.length > 0 && (
        <div>
          <h3 className="text-xl font-semibold mb-4">
            Search Results ({tools.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tools.map((tool) => (
              <ToolCard key={tool.id} tool={tool} />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {tools.length === 0 && !loading && searchQuery && (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-gray-500">No tools found matching your criteria</p>
            <Button variant="outline" onClick={() => { setSearchQuery(''); setTools([]); }} className="mt-4">
              Clear Search
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default MarketplaceSearch;
