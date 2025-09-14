import React from 'react';
import { Box, Typography } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useQuery } from 'react-query';
import { api } from '../../services/api';

const Transfers: React.FC = () => {
  const { data: transfers, isLoading } = useQuery(
    'transfers',
    async () => {
      const response = await api.get('/transfers/');
      return response.data;
    }
  );

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'transfer_number', headerName: 'Transfer Number', width: 150 },
    { field: 'from_shop_id', headerName: 'From Shop', width: 120 },
    { field: 'to_shop_id', headerName: 'To Shop', width: 120 },
    { field: 'status', headerName: 'Status', width: 120 },
    { field: 'transfer_date', headerName: 'Date', width: 120 },
    { field: 'created_at', headerName: 'Created', width: 180 },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Transfers
      </Typography>
      <Box sx={{ height: 400, width: '100%' }}>
        <DataGrid
          rows={transfers || []}
          columns={columns}
          loading={isLoading}
          pageSizeOptions={[5, 10, 25]}
          disableRowSelectionOnClick
        />
      </Box>
    </Box>
  );
};

export default Transfers;

