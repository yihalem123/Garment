import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Tabs,
  Tab,
  Alert,
  Divider,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
  InputAdornment,
  Fab,
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import {
  Add as AddIcon,
  Inventory as InventoryIcon,
  TrendingUp,
  TrendingDown,
  Warning,
  Search,
  Refresh,
  Download,
  Print,
  Assessment,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { api } from '../../services/api';
import { toast } from 'react-hot-toast';

interface StockItem {
  id: number;
  shop_id: number;
  shop_name?: string;
  item_type: string;
  product_id?: number;
  product_name?: string;
  product_sku?: string;
  raw_material_id?: number;
  raw_material_name?: string;
  quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  min_stock_level: number;
  max_stock_level?: number;
  unit_cost?: number;
  total_value?: number;
  created_at: string;
  updated_at: string;
}

interface StockMovement {
  id: number;
  shop_id: number;
  shop_name?: string;
  item_type: string;
  product_id?: number;
  product_name?: string;
  raw_material_id?: number;
  raw_material_name?: string;
  quantity: number;
  reason: string;
  reference_id?: number;
  reference_type?: string;
  notes?: string;
  created_at: string;
}

interface StockAdjustment {
  shop_id: number;
  item_type: string;
  product_id?: number;
  raw_material_id?: number;
  quantity: number;
  reason: string;
  notes?: string;
}

const Inventory: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const queryClient = useQueryClient();
  const [tabValue, setTabValue] = useState(0);
  const [adjustmentOpen, setAdjustmentOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterShop, setFilterShop] = useState<number | null>(null);
  const [lowStockOnly, setLowStockOnly] = useState(false);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ET', {
      style: 'currency',
      currency: 'ETB',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  // Fetch data
  const { data: stocks, isLoading: stocksLoading } = useQuery(
    ['stocks', filterShop, filterType, lowStockOnly],
    async () => {
      const params = new URLSearchParams();
      if (filterShop) params.append('shop_id', filterShop.toString());
      if (filterType !== 'all') params.append('item_type', filterType);
      if (lowStockOnly) params.append('low_stock_only', 'true');
      
      const response = await api.get(`/inventory/stocks?${params}`);
      return response.data;
    }
  );

  const { data: movements, isLoading: movementsLoading } = useQuery(
    ['stockMovements', filterShop, filterType],
    async () => {
      const params = new URLSearchParams();
      if (filterShop) params.append('shop_id', filterShop.toString());
      if (filterType !== 'all') params.append('item_type', filterType);
      
      const response = await api.get(`/inventory/stock-movements?${params}`);
      return response.data;
    }
  );

  const { data: shops } = useQuery('shops', async () => {
    const response = await api.get('/shops/');
    return response.data;
  });

  const { data: products } = useQuery('products', async () => {
    const response = await api.get('/products/');
    return response.data;
  });

  const { data: rawMaterials } = useQuery('rawMaterials', async () => {
    const response = await api.get('/raw-materials/');
    return response.data;
  });

  // Adjust stock mutation
  const adjustStockMutation = useMutation(
    async (adjustment: StockAdjustment) => {
      const response = await api.post('/inventory/stocks/adjust', adjustment);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('stocks');
        queryClient.invalidateQueries('stockMovements');
        toast.success('Stock adjusted successfully!');
        setAdjustmentOpen(false);
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to adjust stock');
      }
    }
  );

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleAdjustStock = (adjustment: StockAdjustment) => {
    adjustStockMutation.mutate(adjustment);
  };

  const handleExport = () => {
    // TODO: Implement export functionality
    console.log('Exporting inventory data...');
  };

  const handlePrint = () => {
    // TODO: Implement print functionality
    console.log('Printing inventory report...');
  };

  // Calculate statistics
  const totalItems = stocks?.length || 0;
  const lowStockItems = stocks?.filter((item: StockItem) => item.quantity <= item.min_stock_level).length || 0;
  const totalValue = stocks?.reduce((sum: number, item: StockItem) => sum + (item.total_value || 0), 0) || 0;
  const outOfStockItems = stocks?.filter((item: StockItem) => item.quantity === 0).length || 0;

  // Filter stocks based on search term
  const filteredStocks = stocks?.filter((item: StockItem) => {
    const matchesSearch = !searchTerm || 
      item.product_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.raw_material_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.product_sku?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  }) || [];

  // Stock columns for DataGrid
  const stockColumns: GridColDef[] = [
    {
      field: 'item_name',
      headerName: 'Item',
      width: 200,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2" fontWeight="bold">
            {params.row.product_name || params.row.raw_material_name || 'Unknown Item'}
          </Typography>
          {params.row.product_sku && (
            <Typography variant="caption" color="textSecondary">
              SKU: {params.row.product_sku}
            </Typography>
          )}
        </Box>
      ),
    },
    {
      field: 'shop_name',
      headerName: 'Shop',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.row.shop_name || `Shop ${params.row.shop_id}`}
        </Typography>
      ),
    },
    {
      field: 'item_type',
      headerName: 'Type',
      width: 100,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          color={params.value === 'product' ? 'primary' : 'secondary'}
        />
      ),
    },
    {
      field: 'quantity',
      headerName: 'Quantity',
      width: 120,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2" fontWeight="bold">
            {params.value}
          </Typography>
          <Typography variant="caption" color="textSecondary">
            Available: {params.row.available_quantity || params.value}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'min_stock_level',
      headerName: 'Min Level',
      width: 100,
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => {
        const quantity = params.row.quantity;
        const minLevel = params.row.min_stock_level;
        
        if (quantity === 0) {
          return <Chip label="Out of Stock" color="error" size="small" />;
        } else if (quantity <= minLevel) {
          return <Chip label="Low Stock" color="warning" size="small" />;
        } else {
          return <Chip label="In Stock" color="success" size="small" />;
        }
      },
    },
    {
      field: 'total_value',
      headerName: 'Value',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="bold">
          {formatCurrency(params.value || 0)}
        </Typography>
      ),
    },
  ];

  // Movement columns for DataGrid
  const movementColumns: GridColDef[] = [
    {
      field: 'item_name',
      headerName: 'Item',
      width: 200,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2" fontWeight="bold">
            {params.row.product_name || params.row.raw_material_name || 'Unknown Item'}
          </Typography>
          <Typography variant="caption" color="textSecondary">
            {params.row.shop_name || `Shop ${params.row.shop_id}`}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'quantity',
      headerName: 'Quantity',
      width: 100,
      renderCell: (params) => (
        <Box display="flex" alignItems="center">
          {params.value > 0 ? (
            <TrendingUp color="success" sx={{ mr: 1 }} />
          ) : (
            <TrendingDown color="error" sx={{ mr: 1 }} />
          )}
          <Typography
            variant="body2"
            color={params.value > 0 ? 'success.main' : 'error.main'}
            fontWeight="bold"
          >
            {params.value > 0 ? '+' : ''}{params.value}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'reason',
      headerName: 'Reason',
      width: 150,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          color={
            params.value === 'purchase' ? 'success' :
            params.value === 'sale' ? 'error' :
            params.value === 'production' ? 'info' :
            params.value === 'adjustment' ? 'warning' : 'default'
          }
        />
      ),
    },
    {
      field: 'reference_type',
      headerName: 'Reference',
      width: 120,
    },
    {
      field: 'created_at',
      headerName: 'Date',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2">
          {new Date(params.value).toLocaleDateString()}
        </Typography>
      ),
    },
  ];

  if (stocksLoading || movementsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading inventory data...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          Inventory Management
        </Typography>
        <Box display="flex" gap={2}>
          <Tooltip title="Refresh Data">
            <IconButton>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="Export Data">
            <IconButton onClick={handleExport}>
              <Download />
            </IconButton>
          </Tooltip>
          <Tooltip title="Print Report">
            <IconButton onClick={handlePrint}>
              <Print />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <InventoryIcon color="primary" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Total Items
                </Typography>
              </Box>
              <Typography variant="h4" color="primary.main" fontWeight="bold">
                {totalItems}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Warning color="warning" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Low Stock Items
                </Typography>
              </Box>
              <Typography variant="h4" color="warning.main" fontWeight="bold">
                {lowStockItems}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingDown color="error" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Out of Stock
                </Typography>
              </Box>
              <Typography variant="h4" color="error.main" fontWeight="bold">
                {outOfStockItems}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Assessment color="success" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Total Value
                </Typography>
              </Box>
              <Typography variant="h4" color="success.main" fontWeight="bold">
                {formatCurrency(totalValue)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                placeholder="Search items..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  label="Type"
                >
                  <MenuItem value="all">All Types</MenuItem>
                  <MenuItem value="product">Products</MenuItem>
                  <MenuItem value="raw_material">Raw Materials</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Shop</InputLabel>
                <Select
                  value={filterShop || ''}
                  onChange={(e) => setFilterShop(e.target.value ? Number(e.target.value) : null)}
                  label="Shop"
                >
                  <MenuItem value="">All Shops</MenuItem>
                  {shops?.map((shop: any) => (
                    <MenuItem key={shop.id} value={shop.id}>
                      {shop.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Button
                variant={lowStockOnly ? 'contained' : 'outlined'}
                onClick={() => setLowStockOnly(!lowStockOnly)}
                startIcon={<Warning />}
                fullWidth
              >
                Low Stock Only
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setAdjustmentOpen(true)}
                fullWidth
              >
                Adjust Stock
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Card>
        <Tabs value={tabValue} onChange={handleTabChange} variant="fullWidth">
          <Tab label="Stock Items" icon={<InventoryIcon />} />
          <Tab label="Stock Movements" icon={<TrendingUp />} />
        </Tabs>

        <Box p={3}>
          {tabValue === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Stock Items ({filteredStocks.length})
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <DataGrid
                rows={filteredStocks}
                columns={stockColumns}
                initialState={{
                  pagination: {
                    paginationModel: { page: 0, pageSize: 10 },
                  },
                }}
                pageSizeOptions={[10, 25, 50]}
                autoHeight
                disableRowSelectionOnClick
              />
            </Box>
          )}

          {tabValue === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Stock Movements ({movements?.length || 0})
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <DataGrid
                rows={movements || []}
                columns={movementColumns}
                initialState={{
                  pagination: {
                    paginationModel: { page: 0, pageSize: 10 },
                  },
                }}
                pageSizeOptions={[10, 25, 50]}
                autoHeight
                disableRowSelectionOnClick
              />
            </Box>
          )}
        </Box>
      </Card>

      {/* Stock Adjustment Dialog */}
      <Dialog open={adjustmentOpen} onClose={() => setAdjustmentOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Adjust Stock</DialogTitle>
        <DialogContent>
          <StockAdjustmentForm
            shops={shops}
            products={products}
            rawMaterials={rawMaterials}
            onSubmit={handleAdjustStock}
            onCancel={() => setAdjustmentOpen(false)}
          />
        </DialogContent>
      </Dialog>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setAdjustmentOpen(true)}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
};

// Stock Adjustment Form Component
interface StockAdjustmentFormProps {
  shops: any[];
  products: any[];
  rawMaterials: any[];
  onSubmit: (adjustment: StockAdjustment) => void;
  onCancel: () => void;
}

const StockAdjustmentForm: React.FC<StockAdjustmentFormProps> = ({
  shops,
  products,
  rawMaterials,
  onSubmit,
  onCancel,
}) => {
  const [formData, setFormData] = useState<StockAdjustment>({
    shop_id: 0,
    item_type: 'product',
    product_id: undefined,
    raw_material_id: undefined,
    quantity: 0,
    reason: 'adjustment',
    notes: '',
  });

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <Grid container spacing={2} sx={{ mt: 1 }}>
        <Grid item xs={12}>
          <FormControl fullWidth required>
            <InputLabel>Shop</InputLabel>
            <Select
              value={formData.shop_id}
              onChange={(e) => handleChange('shop_id', e.target.value)}
              label="Shop"
            >
              {shops?.map((shop) => (
                <MenuItem key={shop.id} value={shop.id}>
                  {shop.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12}>
          <FormControl fullWidth required>
            <InputLabel>Item Type</InputLabel>
            <Select
              value={formData.item_type}
              onChange={(e) => handleChange('item_type', e.target.value)}
              label="Item Type"
            >
              <MenuItem value="product">Product</MenuItem>
              <MenuItem value="raw_material">Raw Material</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        {formData.item_type === 'product' ? (
          <Grid item xs={12}>
            <FormControl fullWidth required>
              <InputLabel>Product</InputLabel>
              <Select
                value={formData.product_id || ''}
                onChange={(e) => handleChange('product_id', e.target.value)}
                label="Product"
              >
                {products?.map((product) => (
                  <MenuItem key={product.id} value={product.id}>
                    {product.name} ({product.sku})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        ) : (
          <Grid item xs={12}>
            <FormControl fullWidth required>
              <InputLabel>Raw Material</InputLabel>
              <Select
                value={formData.raw_material_id || ''}
                onChange={(e) => handleChange('raw_material_id', e.target.value)}
                label="Raw Material"
              >
                {rawMaterials?.map((material) => (
                  <MenuItem key={material.id} value={material.id}>
                    {material.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        )}

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Quantity"
            type="number"
            value={formData.quantity}
            onChange={(e) => handleChange('quantity', parseFloat(e.target.value))}
            required
            helperText="Positive for increase, negative for decrease"
          />
        </Grid>

        <Grid item xs={12}>
          <FormControl fullWidth required>
            <InputLabel>Reason</InputLabel>
            <Select
              value={formData.reason}
              onChange={(e) => handleChange('reason', e.target.value)}
              label="Reason"
            >
              <MenuItem value="adjustment">Stock Adjustment</MenuItem>
              <MenuItem value="damage">Damage</MenuItem>
              <MenuItem value="theft">Theft</MenuItem>
              <MenuItem value="expired">Expired</MenuItem>
              <MenuItem value="found">Found</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Notes"
            multiline
            rows={3}
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
          />
        </Grid>
      </Grid>

      <DialogActions>
        <Button onClick={onCancel}>Cancel</Button>
        <Button type="submit" variant="contained">
          Adjust Stock
        </Button>
      </DialogActions>
    </form>
  );
};

export default Inventory;