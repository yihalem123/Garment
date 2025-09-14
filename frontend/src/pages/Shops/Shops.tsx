import React from 'react';
import { Box, Typography } from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useQuery } from 'react-query';
import { api } from '../../services/api';

const Shops: React.FC = () => {
  const { data: shops, isLoading } = useQuery(
    'shops',
    async () => {
      const response = await api.get('/shops/');
      return response.data;
    }
  );

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'name', headerName: 'Shop Name', width: 200 },
    { field: 'address', headerName: 'Address', width: 300 },
    { field: 'phone', headerName: 'Phone', width: 150 },
    { field: 'manager_id', headerName: 'Manager ID', width: 120 },
    {
      field: 'is_active',
      headerName: 'Active',
      width: 100,
      renderCell: (params) => (params.value ? 'Yes' : 'No'),
    },
    { field: 'created_at', headerName: 'Created', width: 180 },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Shops
      </Typography>
      <Box sx={{ height: 400, width: '100%' }}>
        <DataGrid
          rows={shops || []}
          columns={columns}
          loading={isLoading}
          pageSizeOptions={[5, 10, 25]}
          disableRowSelectionOnClick
        />
      </Box>
    </Box>
  );
};

export default Shops;

