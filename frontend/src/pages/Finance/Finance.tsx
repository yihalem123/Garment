import React from 'react';
import { Box, Typography, Grid, Card, CardContent } from '@mui/material';
import { useQuery } from 'react-query';
import { api } from '../../services/api';

const Finance: React.FC = () => {
  const { data: plStatement } = useQuery(
    'profitLossStatement',
    async () => {
      const response = await api.get('/finance/profit-loss-statement');
      return response.data;
    }
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Financial Reporting
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Revenue
              </Typography>
              <Typography variant="h4" color="success.main">
                ${plStatement?.revenue?.total?.toLocaleString() || 0}
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
              <Typography variant="h4" color="error.main">
                ${plStatement?.costs?.total?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Net Profit
              </Typography>
              <Typography variant="h4" color="primary.main">
                ${plStatement?.profit?.net_profit?.toLocaleString() || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Revenue by Payment Method
              </Typography>
              {plStatement?.revenue?.by_payment_method?.map((payment: any, index: number) => (
                <Box key={index} display="flex" justifyContent="space-between" sx={{ mb: 1 }}>
                  <Typography variant="body2">
                    {payment.payment_method}
                  </Typography>
                  <Typography variant="body2">
                    ${payment.amount?.toLocaleString()}
                  </Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cost Breakdown
              </Typography>
              <Box display="flex" justifyContent="space-between" sx={{ mb: 1 }}>
                <Typography variant="body2">Purchases</Typography>
                <Typography variant="body2">
                  ${plStatement?.costs?.purchases?.toLocaleString()}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" sx={{ mb: 1 }}>
                <Typography variant="body2">Production</Typography>
                <Typography variant="body2">
                  ${plStatement?.costs?.production?.toLocaleString()}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" sx={{ mb: 1 }}>
                <Typography variant="body2">Overhead</Typography>
                <Typography variant="body2">
                  ${plStatement?.costs?.overhead?.toLocaleString()}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Finance;

