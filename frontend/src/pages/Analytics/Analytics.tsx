import React from 'react';
import { Box, Typography, Grid, Card, CardContent } from '@mui/material';
import { useQuery } from 'react-query';
import { api } from '../../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const Analytics: React.FC = () => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { data: dashboardData } = useQuery(
    'dashboard',
    async () => {
      const response = await api.get('/analytics/dashboard');
      return response.data;
    }
  );

  const { data: profitLossData } = useQuery(
    'profitLoss',
    async () => {
      const response = await api.get('/analytics/profit-loss');
      return response.data;
    }
  );

  const sampleChartData = [
    { month: 'Jan', sales: 4000, purchases: 3000 },
    { month: 'Feb', sales: 3000, purchases: 2000 },
    { month: 'Mar', sales: 5000, purchases: 4000 },
    { month: 'Apr', sales: 4500, purchases: 3500 },
    { month: 'May', sales: 6000, purchases: 4500 },
    { month: 'Jun', sales: 5500, purchases: 4000 },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analytics & Reporting
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Sales vs Purchases Trend
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={sampleChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="sales" stroke="#4caf50" strokeWidth={2} />
                  <Line type="monotone" dataKey="purchases" stroke="#ff9800" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Monthly Performance
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={sampleChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="sales" fill="#4caf50" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Revenue
              </Typography>
              <Typography variant="h4">
                ${profitLossData?.total_revenue?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Costs
              </Typography>
              <Typography variant="h4">
                ${profitLossData?.total_costs?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Profit Margin
              </Typography>
              <Typography variant="h4">
                {profitLossData?.profit_margin || 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Analytics;

