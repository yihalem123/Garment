import React from 'react';
import { Box, Typography } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useQuery } from 'react-query';
import { api } from '../../services/api';

const Production: React.FC = () => {
  const { data: productionRuns, isLoading } = useQuery(
    'production',
    async () => {
      const response = await api.get('/production/');
      return response.data;
    }
  );

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'run_number', headerName: 'Run Number', width: 150 },
    { field: 'planned_quantity', headerName: 'Planned Qty', width: 120, type: 'number' },
    { field: 'labor_cost', headerName: 'Labor Cost', width: 120, type: 'number' },
    { field: 'overhead_cost', headerName: 'Overhead Cost', width: 120, type: 'number' },
    { field: 'status', headerName: 'Status', width: 120 },
    { field: 'start_date', headerName: 'Start Date', width: 120 },
    { field: 'created_at', headerName: 'Created', width: 180 },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Production Runs
      </Typography>
      <Box sx={{ height: 400, width: '100%' }}>
        <DataGrid
          rows={productionRuns || []}
          columns={columns}
          loading={isLoading}
          pageSizeOptions={[5, 10, 25]}
          disableRowSelectionOnClick
        />
      </Box>
    </Box>
  );
};

export default Production;

