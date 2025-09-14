import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { useQuery } from 'react-query';
import { api } from '../../services/api';

interface StockItem {
  id: number;
  shop_id: number;
  item_type: string;
  product_id?: number;
  raw_material_id?: number;
  quantity: number;
  reserved_quantity: number;
  min_stock_level: number;
  created_at: string;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
interface StockMovement {
  id: number;
  shop_id: number;
  item_type: string;
  product_id?: number;
  raw_material_id?: number;
  quantity: number;
  reason: string;
  reference_id: number;
  reference_type: string;
  created_at: string;
}

const Inventory: React.FC = () => {
  const { data: stocks, isLoading: stocksLoading } = useQuery(
    'stocks',
    async () => {
      const response = await api.get('/inventory/stocks');
      return response.data;
    }
  );

  const { data: movements, isLoading: movementsLoading } = useQuery(
    'stockMovements',
    async () => {
      const response = await api.get('/inventory/stock-movements');
      return response.data;
    }
  );

  const stockColumns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'shop_id', headerName: 'Shop ID', width: 100 },
    { field: 'item_type', headerName: 'Type', width: 120 },
    { field: 'product_id', headerName: 'Product ID', width: 120 },
    { field: 'raw_material_id', headerName: 'Material ID', width: 120 },
    { field: 'quantity', headerName: 'Quantity', width: 120, type: 'number' },
    { field: 'reserved_quantity', headerName: 'Reserved', width: 120, type: 'number' },
    { field: 'min_stock_level', headerName: 'Min Level', width: 120, type: 'number' },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => {
        const available = params.row.quantity - params.row.reserved_quantity;
        const isLow = available <= params.row.min_stock_level;
        return (
          <Chip
            label={isLow ? 'Low Stock' : 'OK'}
            color={isLow ? 'error' : 'success'}
            size="small"
          />
        );
      },
    },
  ];

  const movementColumns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'shop_id', headerName: 'Shop ID', width: 100 },
    { field: 'item_type', headerName: 'Type', width: 120 },
    { field: 'quantity', headerName: 'Quantity', width: 120, type: 'number' },
    { field: 'reason', headerName: 'Reason', width: 150 },
    { field: 'reference_type', headerName: 'Reference Type', width: 150 },
    { field: 'reference_id', headerName: 'Reference ID', width: 120 },
    { field: 'created_at', headerName: 'Date', width: 180 },
  ];

  const lowStockItems = stocks?.filter((stock: StockItem) => 
    (stock.quantity - stock.reserved_quantity) <= stock.min_stock_level
  ) || [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Inventory Management
      </Typography>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Stock Items
              </Typography>
              <Typography variant="h4">
                {stocks?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Low Stock Items
              </Typography>
              <Typography variant="h4" color="error">
                {lowStockItems.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Movements
              </Typography>
              <Typography variant="h4">
                {movements?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Product Items
              </Typography>
              <Typography variant="h4">
                {stocks?.filter((s: StockItem) => s.item_type === 'product').length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Typography variant="h5" gutterBottom sx={{ mt: 3 }}>
        Stock Items
      </Typography>
      <Box sx={{ height: 400, width: '100%', mb: 3 }}>
        <DataGrid
          rows={stocks || []}
          columns={stockColumns}
          loading={stocksLoading}
          pageSizeOptions={[5, 10, 25]}
          disableRowSelectionOnClick
        />
      </Box>

      <Typography variant="h5" gutterBottom>
        Stock Movements
      </Typography>
      <Box sx={{ height: 400, width: '100%' }}>
        <DataGrid
          rows={movements || []}
          columns={movementColumns}
          loading={movementsLoading}
          pageSizeOptions={[5, 10, 25]}
          disableRowSelectionOnClick
        />
      </Box>
    </Box>
  );
};

export default Inventory;

