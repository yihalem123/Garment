import React from 'react';
import { Box, Typography } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useQuery } from 'react-query';
import { api } from '../../services/api';

const Purchases: React.FC = () => {
  const { data: purchases, isLoading } = useQuery(
    'purchases',
    async () => {
      const response = await api.get('/purchases/');
      return response.data;
    }
  );

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'supplier_name', headerName: 'Supplier', width: 200 },
    { field: 'supplier_invoice', headerName: 'Invoice', width: 150 },
    { field: 'total_amount', headerName: 'Total Amount', width: 150, type: 'number' },
    { field: 'status', headerName: 'Status', width: 120 },
    { field: 'purchase_date', headerName: 'Date', width: 120 },
    { field: 'created_at', headerName: 'Created', width: 180 },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Purchases
      </Typography>
      <Box sx={{ height: 400, width: '100%' }}>
        <DataGrid
          rows={purchases || []}
          columns={columns}
          loading={isLoading}
          pageSizeOptions={[5, 10, 25]}
          disableRowSelectionOnClick
        />
      </Box>
    </Box>
  );
};

export default Purchases;

