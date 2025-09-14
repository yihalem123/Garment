import React from 'react';
import { Box, Typography, Grid, Card, CardContent } from '@mui/material';
import { useQuery } from 'react-query';
import { api } from '../../services/api';

const HR: React.FC = () => {
  const { data: workforceSummary } = useQuery(
    'workforceSummary',
    async () => {
      const response = await api.get('/hr/workforce-summary');
      return response.data;
    }
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Human Resources
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Employees
              </Typography>
              <Typography variant="h4">
                {workforceSummary?.total_employees || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={9}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Employees by Role
              </Typography>
              <Grid container spacing={2}>
                {workforceSummary?.by_role && Object.entries(workforceSummary.by_role).map(([role, count]) => (
                  <Grid item xs={4} key={role}>
                    <Typography variant="body2" color="textSecondary">
                      {role.charAt(0).toUpperCase() + role.slice(1)}
                    </Typography>
                    <Typography variant="h6">
                      {count as number}
                    </Typography>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Hires
              </Typography>
              {workforceSummary?.recent_hires?.map((hire: any, index: number) => (
                <Box key={index} sx={{ mb: 2, p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
                  <Typography variant="subtitle1">
                    {hire.full_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {hire.email} • {hire.role} • {hire.shop_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Hired: {new Date(hire.created_at).toLocaleDateString()}
                  </Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default HR;

