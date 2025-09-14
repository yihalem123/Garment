import React from 'react';
import { Box, Typography } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useQuery } from 'react-query';
import { api } from '../../services/api';

const Returns: React.FC = () => {
  const { data: returns, isLoading } = useQuery(
    'returns',
    async () => {
      const response = await api.get('/returns/');
      return response.data;
    }
  );

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'sale_id', headerName: 'Sale ID', width: 100 },
    { field: 'return_date', headerName: 'Return Date', width: 120 },
    { field: 'reason', headerName: 'Reason', width: 150 },
    { field: 'notes', headerName: 'Notes', width: 200 },
    { field: 'created_at', headerName: 'Created', width: 180 },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Returns
      </Typography>
      <Box sx={{ height: 400, width: '100%' }}>
        <DataGrid
          rows={returns || []}
          columns={columns}
          loading={isLoading}
          pageSizeOptions={[5, 10, 25]}
          disableRowSelectionOnClick
        />
      </Box>
    </Box>
  );
};

export default Returns;

