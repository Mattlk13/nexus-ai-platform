import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import {
  DollarSign,
  TrendingUp,
  ShoppingCart,
  Award,
  Calendar,
  ArrowUp,
  ArrowDown
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const RevenueAnalytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('all');

  useEffect(() => {
    loadAnalytics();
    loadMetrics();
  }, [timeRange]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (timeRange !== 'all') {
        // Add date filtering if needed
      }
      
      const response = await fetch(`${API_URL}/api/creator/revenue/analytics?${params}`);
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    try {
      const response = await fetch(`${API_URL}/api/creator/revenue/metrics`);
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatMonthlyData = (monthlyRevenue) => {
    if (!monthlyRevenue) return [];
    return Object.entries(monthlyRevenue).map(([month, revenue]) => ({
      month: month.substring(5), // Get MM from YYYY-MM
      revenue: revenue
    }));
  };

  const StatCard = ({ icon: Icon, title, value, subtitle, trend }) => (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Icon className="w-5 h-5 text-blue-600" />
              </div>
              <p className="text-sm font-medium text-gray-600">{title}</p>
            </div>
            <p className="text-3xl font-bold text-gray-900">{value}</p>
            {subtitle && (
              <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
            )}
          </div>
          {trend !== undefined && (
            <div className={`flex items-center gap-1 ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {trend >= 0 ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
              <span className="text-sm font-semibold">{Math.abs(trend)}%</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );

  if (loading && !analytics) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Revenue Analytics</h2>
          <p className="text-gray-600 mt-2">Track your earnings and sales performance</p>
        </div>
        <div className="flex gap-2">
          {['all', '30d', '7d'].map((range) => (
            <Button
              key={range}
              variant={timeRange === range ? 'default' : 'outline'}
              onClick={() => setTimeRange(range)}
              size="sm"
            >
              {range === 'all' ? 'All Time' : range === '30d' ? 'Last 30 Days' : 'Last 7 Days'}
            </Button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            icon={DollarSign}
            title="Total Earnings"
            value={formatCurrency(metrics.total_earnings)}
            subtitle={`${metrics.successful_transactions} transactions`}
          />
          <StatCard
            icon={TrendingUp}
            title="Available Balance"
            value={formatCurrency(metrics.available_balance)}
            subtitle="Ready to withdraw"
          />
          <StatCard
            icon={ShoppingCart}
            title="Avg Transaction"
            value={formatCurrency(metrics.avg_transaction_value)}
            subtitle={`${metrics.total_transactions} total`}
          />
          <StatCard
            icon={Award}
            title="Top Tool Earnings"
            value={metrics.highest_earning_tool ? formatCurrency(metrics.highest_earning_tool.earnings) : '$0.00'}
            subtitle="Best performer"
          />
        </div>
      )}

      {/* Revenue Chart */}
      {analytics && analytics.monthly_revenue && Object.keys(analytics.monthly_revenue).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Monthly Revenue Trend</CardTitle>
            <CardDescription>
              Track your revenue over time
              {analytics.growth_rate && (
                <span className={`ml-2 font-semibold ${analytics.growth_rate >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {analytics.growth_rate >= 0 ? '↑' : '↓'} {Math.abs(analytics.growth_rate)}% MoM
                </span>
              )}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={formatMonthlyData(analytics.monthly_revenue)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Top Selling Tools */}
      {analytics && analytics.top_selling_tools && analytics.top_selling_tools.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Top Selling Tools</CardTitle>
            <CardDescription>Your best performing products</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.top_selling_tools.slice(0, 5)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="tool_id" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Legend />
                <Bar dataKey="revenue" fill="#10b981" name="Revenue" />
                <Bar dataKey="count" fill="#3b82f6" name="Sales Count" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Recent Transactions */}
      {metrics && metrics.recent_transactions && metrics.recent_transactions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Transactions</CardTitle>
            <CardDescription>Latest sales activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {metrics.recent_transactions.slice(0, 5).map((txn) => (
                <div key={txn.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-full">
                      <ShoppingCart className="w-4 h-4 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium">Tool ID: {txn.tool_id}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(txn.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-green-600">{formatCurrency(txn.amount)}</p>
                    <p className="text-xs text-gray-500 capitalize">{txn.status}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {analytics && analytics.total_sales === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <DollarSign className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Revenue Yet</h3>
            <p className="text-gray-600 mb-4">Start selling your AI tools to see analytics here</p>
            <Button>Create Your First Tool</Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default RevenueAnalytics;
