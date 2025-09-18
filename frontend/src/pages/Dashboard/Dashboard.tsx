import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  useTheme,
  useMediaQuery,
  Chip,
  Avatar,
} from '@mui/material';
import {
  ShoppingCart,
  Factory,
  LocalShipping,
  PointOfSale,
  TrendingUp,
  Inventory,
  TrendingDown,
  AttachMoney,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { api } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const Dashboard: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user } = useAuth();
  
  const { data: dashboardData, isLoading } = useQuery(
    'dashboard',
    async () => {
      try {
        // For shop managers, get shop-specific data
        const endpoint = user?.role === 'shop_manager' && user?.shop_id 
          ? `/analytics/dashboard?shop_id=${user.shop_id}`
          : '/analytics/dashboard';
        const response = await api.get(endpoint);
        return response.data;
      } catch (error) {
        // Return mock data if API fails
        console.warn('API not available, using mock data:', error);
        return {
          total_sales: user?.role === 'shop_manager' ? 45000 : 125000,
          total_purchases: user?.role === 'shop_manager' ? 32000 : 85000,
          total_products: user?.role === 'shop_manager' ? 45 : 150,
          total_customers: user?.role === 'shop_manager' ? 25 : 89
        };
      }
    }
  );

  const { data: profitLossData } = useQuery(
    'profitLoss',
    async () => {
      try {
        const response = await api.get('/analytics/profit-loss');
        return response.data;
      } catch (error) {
        // Return mock data if API fails
        console.warn('API not available, using mock data:', error);
        return [
          { month: 'Jan', sales: 12000, purchases: 8000 },
          { month: 'Feb', sales: 15000, purchases: 9500 },
          { month: 'Mar', sales: 18000, purchases: 11000 },
          { month: 'Apr', sales: 16000, purchases: 10000 },
          { month: 'May', sales: 20000, purchases: 12000 },
          { month: 'Jun', sales: 22000, purchases: 13000 },
        ];
      }
    }
  );

  const statsCards = [
    {
      title: 'Total Sales',
      value: dashboardData?.total_sales || 0,
      icon: <PointOfSale />,
      color: '#4CAF50',
      bgColor: '#E8F5E8',
      change: '+12.5%',
      changeType: 'positive' as const,
    },
    {
      title: 'Total Purchases',
      value: dashboardData?.total_purchases || 0,
      icon: <ShoppingCart />,
      color: '#FF9800',
      bgColor: '#FFF3E0',
      change: '+8.2%',
      changeType: 'positive' as const,
    },
    {
      title: 'Production Units',
      value: dashboardData?.total_production || 0,
      icon: <Factory />,
      color: '#2196F3',
      bgColor: '#E3F2FD',
      change: '+15.3%',
      changeType: 'positive' as const,
    },
    {
      title: 'Transfers',
      value: dashboardData?.total_transfers || 0,
      icon: <LocalShipping />,
      color: '#9C27B0',
      bgColor: '#F3E5F5',
      change: '-2.1%',
      changeType: 'negative' as const,
    },
    {
      title: 'Low Stock Items',
      value: dashboardData?.low_stock_items || 0,
      icon: <Inventory />,
      color: '#F44336',
      bgColor: '#FFEBEE',
      change: '-5.4%',
      changeType: 'positive' as const,
    },
    {
      title: 'Profit Margin',
      value: `${profitLossData?.profit_margin || 0}%`,
      icon: <AttachMoney />,
      color: '#4CAF50',
      bgColor: '#E8F5E8',
      change: '+3.2%',
      changeType: 'positive' as const,
    },
  ];

  const sampleChartData = [
    { month: 'Jan', sales: 4000, purchases: 3000 },
    { month: 'Feb', sales: 3000, purchases: 2000 },
    { month: 'Mar', sales: 5000, purchases: 4000 },
    { month: 'Apr', sales: 4500, purchases: 3500 },
    { month: 'May', sales: 6000, purchases: 4500 },
    { month: 'Jun', sales: 5500, purchases: 4000 },
  ];

  if (isLoading) {
    return <div>Loading dashboard...</div>;
  }

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, color: 'text.primary' }}>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome back! Here's what's happening with your business today.
        </Typography>
      </Box>
      
      <Grid container spacing={3}>
        {statsCards.map((card, index) => (
          <Grid item xs={12} sm={6} lg={4} key={index}>
            <Card 
              sx={{ 
                height: '100%',
                background: `linear-gradient(135deg, ${card.bgColor} 0%, white 100%)`,
                border: `1px solid ${card.bgColor}`,
                transition: 'all 0.3s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                }
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" alignItems="flex-start" justifyContent="space-between" mb={2}>
                  <Avatar 
                    sx={{ 
                      bgcolor: card.color, 
                      width: 48, 
                      height: 48,
                      boxShadow: `0 4px 12px ${card.color}40`,
                    }}
                  >
                    {card.icon}
                  </Avatar>
                  <Chip
                    label={card.change}
                    size="small"
                    color={card.changeType === 'positive' ? 'success' : 'error'}
                    icon={card.changeType === 'positive' ? <TrendingUp /> : <TrendingDown />}
                    sx={{ 
                      fontWeight: 600,
                      fontSize: '0.75rem',
                    }}
                  />
                </Box>
                <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, color: 'text.primary' }}>
                  {typeof card.value === 'number' ? card.value.toLocaleString() : card.value}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
                  {card.title}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}

        <Grid item xs={12} lg={8}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Sales vs Purchases Trend
                </Typography>
                <Chip label="Last 6 months" size="small" variant="outlined" />
              </Box>
              <ResponsiveContainer width="100%" height={isMobile ? 250 : 300}>
                <LineChart data={sampleChartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="month" 
                    tick={{ fontSize: 12 }}
                    axisLine={{ stroke: '#e0e0e0' }}
                  />
                  <YAxis 
                    tick={{ fontSize: 12 }}
                    axisLine={{ stroke: '#e0e0e0' }}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e0e0e0',
                      borderRadius: 8,
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="sales" 
                    stroke="#4CAF50" 
                    strokeWidth={3}
                    dot={{ fill: '#4CAF50', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: '#4CAF50', strokeWidth: 2 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="purchases" 
                    stroke="#FF9800" 
                    strokeWidth={3}
                    dot={{ fill: '#FF9800', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: '#FF9800', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Monthly Performance
                </Typography>
                <Chip label="2024" size="small" variant="outlined" />
              </Box>
              <ResponsiveContainer width="100%" height={isMobile ? 250 : 300}>
                <BarChart data={sampleChartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="month" 
                    tick={{ fontSize: 12 }}
                    axisLine={{ stroke: '#e0e0e0' }}
                  />
                  <YAxis 
                    tick={{ fontSize: 12 }}
                    axisLine={{ stroke: '#e0e0e0' }}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e0e0e0',
                      borderRadius: 8,
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                    }}
                  />
                  <Bar 
                    dataKey="sales" 
                    fill="#4CAF50"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Recent Activities
                </Typography>
                <Chip label="Live" size="small" color="success" />
              </Box>
              {dashboardData?.recent_activities ? (
                dashboardData.recent_activities.map((activity: any, index: number) => (
                  <Box 
                    key={index} 
                    sx={{ 
                      mb: 2, 
                      p: 2, 
                      backgroundColor: 'rgba(0,0,0,0.02)', 
                      borderRadius: 2,
                      border: '1px solid rgba(0,0,0,0.05)',
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        backgroundColor: 'rgba(0,0,0,0.04)',
                        transform: 'translateX(4px)',
                      }
                    }}
                  >
                    <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                      {activity.description}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(activity.timestamp).toLocaleString()}
                    </Typography>
                  </Box>
                ))
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No recent activities to display
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;

