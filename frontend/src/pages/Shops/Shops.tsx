import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Card,
  CardContent,
  Chip,
  Avatar,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
  Alert,
  Badge,
  useTheme,
  useMediaQuery,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Store as StoreIcon,
  People as PeopleIcon,
  Inventory as InventoryIcon,
  TrendingUp as TrendingUpIcon,
  LocationOn as LocationIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Print as PrintIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { api } from '../../services/api';
import { toast } from 'react-hot-toast';

interface Shop {
  id: number;
  name: string;
  address: string;
  phone: string;
  email?: string;
  manager_id?: number;
  manager_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface ShopStats {
  total_sales: number;
  total_products: number;
  total_employees: number;
  monthly_revenue: number;
  inventory_value: number;
}

const Shops: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const queryClient = useQueryClient();
  const [tabValue, setTabValue] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingShop, setEditingShop] = useState<Shop | null>(null);
  const [selectedShop, setSelectedShop] = useState<number | null>(null);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ET', {
      style: 'currency',
      currency: 'ETB',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  // Fetch data
  const { data: shops, isLoading: shopsLoading } = useQuery(
    'shops',
    async () => {
      const response = await api.get('/shops/');
      return response.data;
    }
  );

  const { data: shopStats, isLoading: statsLoading } = useQuery(
    ['shopStats', selectedShop],
    async () => {
      if (!selectedShop) return null;
      const response = await api.get(`/shops/${selectedShop}/statistics`);
      return response.data;
    },
    { enabled: !!selectedShop }
  );

  const { data: shopEmployees } = useQuery(
    ['shopEmployees', selectedShop],
    async () => {
      if (!selectedShop) return [];
      const response = await api.get(`/employees/?shop_id=${selectedShop}`);
      return response.data;
    },
    { enabled: !!selectedShop }
  );

  const { data: shopInventory } = useQuery(
    ['shopInventory', selectedShop],
    async () => {
      if (!selectedShop) return [];
      const response = await api.get(`/inventory/stocks?shop_id=${selectedShop}`);
      return response.data;
    },
    { enabled: !!selectedShop }
  );

  const { data: shopSales } = useQuery(
    ['shopSales', selectedShop],
    async () => {
      if (!selectedShop) return [];
      const response = await api.get(`/sales/?shop_id=${selectedShop}`);
      return response.data;
    },
    { enabled: !!selectedShop }
  );

  // Mutations
  const createShopMutation = useMutation(
    async (shopData: Partial<Shop>) => {
      const response = await api.post('/shops/', shopData);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('shops');
        toast.success('Shop created successfully!');
        setDialogOpen(false);
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create shop');
      }
    }
  );

  const updateShopMutation = useMutation(
    async ({ id, ...shopData }: Partial<Shop> & { id: number }) => {
      const response = await api.put(`/shops/${id}`, shopData);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('shops');
        toast.success('Shop updated successfully!');
        setDialogOpen(false);
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update shop');
      }
    }
  );

  const deleteShopMutation = useMutation(
    async (id: number) => {
      const response = await api.delete(`/shops/${id}`);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('shops');
        toast.success('Shop deleted successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to delete shop');
      }
    }
  );

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleCreateShop = () => {
    setEditingShop(null);
    setDialogOpen(true);
  };

  const handleEditShop = (shop: Shop) => {
    setEditingShop(shop);
    setDialogOpen(true);
  };

  const handleDeleteShop = (id: number) => {
    if (window.confirm('Are you sure you want to delete this shop?')) {
      deleteShopMutation.mutate(id);
    }
  };

  const handleSubmit = (shopData: Partial<Shop>) => {
    if (editingShop) {
      updateShopMutation.mutate({ id: editingShop.id, ...shopData });
    } else {
      createShopMutation.mutate(shopData);
    }
  };

  const handleExport = () => {
    // TODO: Implement export functionality
    console.log('Exporting shops data...');
  };

  const handlePrint = () => {
    // TODO: Implement print functionality
    console.log('Printing shops report...');
  };

  // Shop columns for DataGrid
  const shopColumns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Shop Name',
      width: 200,
      renderCell: (params) => (
        <Box display="flex" alignItems="center">
          <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
            <StoreIcon />
          </Avatar>
          <Box>
            <Typography variant="body2" fontWeight="bold">
              {params.value}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              ID: {params.row.id}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      field: 'address',
      headerName: 'Address',
      width: 250,
      renderCell: (params) => (
        <Box display="flex" alignItems="center">
          <LocationIcon sx={{ mr: 1, fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="body2">
            {params.value}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'phone',
      headerName: 'Phone',
      width: 150,
      renderCell: (params) => (
        <Box display="flex" alignItems="center">
          <PhoneIcon sx={{ mr: 1, fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="body2">
            {params.value}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'manager_name',
      headerName: 'Manager',
      width: 150,
      renderCell: (params) => (
        <Box display="flex" alignItems="center">
          <PeopleIcon sx={{ mr: 1, fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="body2">
            {params.value || 'Unassigned'}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'is_active',
      headerName: 'Status',
      width: 100,
      renderCell: (params) => (
        <Chip
          label={params.value ? 'Active' : 'Inactive'}
          color={params.value ? 'success' : 'error'}
          size="small"
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 150,
      renderCell: (params) => (
        <Box>
          <Tooltip title="View Details">
            <IconButton
              size="small"
              onClick={() => setSelectedShop(params.row.id)}
            >
              <AssessmentIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Edit Shop">
            <IconButton
              size="small"
              onClick={() => handleEditShop(params.row)}
            >
              <EditIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete Shop">
            <IconButton
              size="small"
              onClick={() => handleDeleteShop(params.row.id)}
              color="error"
            >
              <DeleteIcon />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  if (shopsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading shops data...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          Shop Management
        </Typography>
        <Box display="flex" gap={2}>
          <Tooltip title="Refresh Data">
            <IconButton>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Export Data">
            <IconButton onClick={handleExport}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Print Report">
            <IconButton onClick={handlePrint}>
              <PrintIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateShop}
          >
            Add Shop
          </Button>
        </Box>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <StoreIcon color="primary" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Total Shops
                </Typography>
              </Box>
              <Typography variant="h4" color="primary.main" fontWeight="bold">
                {shops?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <PeopleIcon color="success" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Active Shops
                </Typography>
              </Box>
              <Typography variant="h4" color="success.main" fontWeight="bold">
                {shops?.filter((shop: Shop) => shop.is_active).length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingUpIcon color="info" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Total Revenue
                </Typography>
              </Box>
              <Typography variant="h4" color="info.main" fontWeight="bold">
                {formatCurrency(shopStats?.total_sales || 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <InventoryIcon color="warning" sx={{ mr: 1 }} />
                <Typography color="textSecondary" variant="body2">
                  Total Inventory
                </Typography>
              </Box>
              <Typography variant="h4" color="warning.main" fontWeight="bold">
                {formatCurrency(shopStats?.inventory_value || 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Card>
        <Tabs value={tabValue} onChange={handleTabChange} variant="fullWidth">
          <Tab label="All Shops" icon={<StoreIcon />} />
          <Tab label="Shop Details" icon={<AssessmentIcon />} />
        </Tabs>

        <Box p={3}>
          {tabValue === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                All Shops ({shops?.length || 0})
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <DataGrid
                rows={shops || []}
                columns={shopColumns}
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
                Shop Details
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {selectedShop ? (
                <Box>
                  {/* Selected Shop Info */}
                  {(() => {
                    const shop = shops?.find((s: Shop) => s.id === selectedShop);
                    return shop ? (
                      <Card sx={{ mb: 3 }}>
                        <CardContent>
                          <Grid container spacing={2}>
                            <Grid item xs={12} md={6}>
                              <Typography variant="h6" gutterBottom>
                                {shop.name}
                              </Typography>
                              <Box display="flex" alignItems="center" mb={1}>
                                <LocationIcon sx={{ mr: 1, fontSize: 16 }} />
                                <Typography variant="body2">{shop.address}</Typography>
                              </Box>
                              <Box display="flex" alignItems="center" mb={1}>
                                <PhoneIcon sx={{ mr: 1, fontSize: 16 }} />
                                <Typography variant="body2">{shop.phone}</Typography>
                              </Box>
                              {shop.email && (
                                <Box display="flex" alignItems="center" mb={1}>
                                  <EmailIcon sx={{ mr: 1, fontSize: 16 }} />
                                  <Typography variant="body2">{shop.email}</Typography>
                                </Box>
                              )}
                            </Grid>
                            <Grid item xs={12} md={6}>
                              <Typography variant="subtitle2" gutterBottom>
                                Manager: {shop.manager_name || 'Unassigned'}
                              </Typography>
                              <Typography variant="subtitle2" gutterBottom>
                                Status: 
                                <Chip
                                  label={shop.is_active ? 'Active' : 'Inactive'}
                                  color={shop.is_active ? 'success' : 'error'}
                                  size="small"
                                  sx={{ ml: 1 }}
                                />
                              </Typography>
                            </Grid>
                          </Grid>
                        </CardContent>
                      </Card>
                    ) : null;
                  })()}

                  {/* Shop Statistics */}
                  {shopStats && (
                    <Grid container spacing={3} mb={3}>
                      <Grid item xs={12} sm={6} md={3}>
                        <Card>
                          <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                              Total Sales
                            </Typography>
                            <Typography variant="h5" color="success.main">
                              {formatCurrency(shopStats.total_sales)}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Card>
                          <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                              Products
                            </Typography>
                            <Typography variant="h5" color="primary.main">
                              {shopStats.total_products}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Card>
                          <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                              Employees
                            </Typography>
                            <Typography variant="h5" color="info.main">
                              {shopStats.total_employees}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                      <Grid item xs={12} sm={6} md={3}>
                        <Card>
                          <CardContent>
                            <Typography color="textSecondary" gutterBottom>
                              Monthly Revenue
                            </Typography>
                            <Typography variant="h5" color="warning.main">
                              {formatCurrency(shopStats.monthly_revenue)}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    </Grid>
                  )}

                  {/* Shop Employees */}
                  {shopEmployees && shopEmployees.length > 0 && (
                    <Card sx={{ mb: 3 }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Employees ({shopEmployees.length})
                        </Typography>
                        <TableContainer component={Paper} variant="outlined">
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Name</TableCell>
                                <TableCell>Position</TableCell>
                                <TableCell>Department</TableCell>
                                <TableCell>Status</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {shopEmployees.slice(0, 5).map((employee: any) => (
                                <TableRow key={employee.id}>
                                  <TableCell>{employee.full_name}</TableCell>
                                  <TableCell>{employee.position}</TableCell>
                                  <TableCell>{employee.department}</TableCell>
                                  <TableCell>
                                    <Chip
                                      label={employee.employment_status}
                                      color={employee.employment_status === 'active' ? 'success' : 'error'}
                                      size="small"
                                    />
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  )}

                  {/* Recent Sales */}
                  {shopSales && shopSales.length > 0 && (
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Recent Sales ({shopSales.length})
                        </Typography>
                        <TableContainer component={Paper} variant="outlined">
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Sale #</TableCell>
                                <TableCell>Customer</TableCell>
                                <TableCell>Amount</TableCell>
                                <TableCell>Date</TableCell>
                                <TableCell>Status</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {shopSales.slice(0, 5).map((sale: any) => (
                                <TableRow key={sale.id}>
                                  <TableCell>{sale.sale_number}</TableCell>
                                  <TableCell>{sale.customer_name}</TableCell>
                                  <TableCell>{formatCurrency(sale.final_amount)}</TableCell>
                                  <TableCell>
                                    {new Date(sale.sale_date).toLocaleDateString()}
                                  </TableCell>
                                  <TableCell>
                                    <Chip
                                      label={sale.status}
                                      color={sale.status === 'completed' ? 'success' : 'warning'}
                                      size="small"
                                    />
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  )}
                </Box>
              ) : (
                <Alert severity="info">
                  Select a shop from the "All Shops" tab to view details.
                </Alert>
              )}
            </Box>
          )}
        </Box>
      </Card>

      {/* Shop Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingShop ? 'Edit Shop' : 'Add New Shop'}
        </DialogTitle>
        <DialogContent>
          <ShopForm
            shop={editingShop}
            onSubmit={handleSubmit}
            onCancel={() => setDialogOpen(false)}
          />
        </DialogContent>
      </Dialog>
    </Box>
  );
};

// Shop Form Component
interface ShopFormProps {
  shop: Shop | null;
  onSubmit: (shopData: Partial<Shop>) => void;
  onCancel: () => void;
}

const ShopForm: React.FC<ShopFormProps> = ({ shop, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: shop?.name || '',
    address: shop?.address || '',
    phone: shop?.phone || '',
    email: shop?.email || '',
    is_active: shop?.is_active ?? true,
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
          <TextField
            fullWidth
            label="Shop Name"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            required
          />
        </Grid>

        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Address"
            value={formData.address}
            onChange={(e) => handleChange('address', e.target.value)}
            required
            multiline
            rows={2}
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Phone"
            value={formData.phone}
            onChange={(e) => handleChange('phone', e.target.value)}
            required
          />
        </Grid>

        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => handleChange('email', e.target.value)}
          />
        </Grid>

        <Grid item xs={12}>
          <FormControlLabel
            control={
              <Switch
                checked={formData.is_active}
                onChange={(e) => handleChange('is_active', e.target.checked)}
              />
            }
            label="Active"
          />
        </Grid>
      </Grid>

      <DialogActions>
        <Button onClick={onCancel}>Cancel</Button>
        <Button type="submit" variant="contained">
          {shop ? 'Update' : 'Create'} Shop
        </Button>
      </DialogActions>
    </form>
  );
};

export default Shops;