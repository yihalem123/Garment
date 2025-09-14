import React from 'react';
import { Box, Typography, Grid, Card, CardContent } from '@mui/material';
import { useQuery } from 'react-query';
import { api } from '../../services/api';

const BusinessIntelligence: React.FC = () => {
  const { data: kpis } = useQuery(
    'kpis',
    async () => {
      const response = await api.get('/business-intelligence/kpis');
      return response.data;
    }
  );

  const { data: businessHealth } = useQuery(
    'businessHealth',
    async () => {
      const response = await api.get('/business-intelligence/business-health');
      return response.data;
    }
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Business Intelligence
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Key Performance Indicators
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Total Sales
                  </Typography>
                  <Typography variant="h5">
                    ${kpis?.sales_kpi?.total_sales?.toLocaleString() || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Sales Growth
                  </Typography>
                  <Typography variant="h5">
                    {kpis?.sales_kpi?.sales_growth || 0}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Avg Order Value
                  </Typography>
                  <Typography variant="h5">
                    ${kpis?.sales_kpi?.average_order_value || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Inventory Turnover
                  </Typography>
                  <Typography variant="h5">
                    {kpis?.inventory_kpi?.inventory_turnover || 0}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Business Health
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Overall Score
                  </Typography>
                  <Typography variant="h5">
                    {businessHealth?.overall_score || 0}/100
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Financial Health
                  </Typography>
                  <Typography variant="h5">
                    {businessHealth?.financial_health || 0}/100
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Operational Health
                  </Typography>
                  <Typography variant="h5">
                    {businessHealth?.operational_health || 0}/100
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="textSecondary">
                    Inventory Health
                  </Typography>
                  <Typography variant="h5">
                    {businessHealth?.inventory_health || 0}/100
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {businessHealth?.recommendations && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recommendations
                </Typography>
                {businessHealth.recommendations.map((recommendation: string, index: number) => (
                  <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                    • {recommendation}
                  </Typography>
                ))}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default BusinessIntelligence;

