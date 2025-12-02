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
  FormControlLabel,
  Switch,
  Card,
  CardContent,
  Chip,
  Avatar,
  useTheme,
  useMediaQuery,
  IconButton,
  Tooltip,
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Inventory as InventoryIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { api } from '../../services/api';
import toast from 'react-hot-toast';

interface Product {
  id: number;
  name: string;
  sku: string;
  description: string;
  category: string;
  unit_price: number;
  is_active: boolean;
  created_at: string;
}

const Products: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    description: '',
    category: '',
    unit_price: 0,
    is_active: true,
  });

  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  const queryClient = useQueryClient();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const { data: products, isLoading } = useQuery(
    'products',
    async () => {
      try {
        const response = await api.get('/products/');
        return response.data;
      } catch (error) {
        // Return mock data if API fails
        console.warn('API not available, using mock data:', error);
        return [
          {
            id: 1,
            name: 'Cotton T-Shirt',
            sku: 'TSH-001',
            description: 'High quality cotton t-shirt',
            category: 'T-Shirts',
            unit_price: 25.99,
            is_active: true,
            created_at: '2024-01-01T00:00:00Z'
          },
          {
            id: 2,
            name: 'Denim Jeans',
            sku: 'JNS-002',
            description: 'Classic blue denim jeans',
            category: 'Jeans',
            unit_price: 49.99,
            is_active: true,
            created_at: '2024-01-02T00:00:00Z'
          },
          {
            id: 3,
            name: 'Wool Sweater',
            sku: 'SWT-003',
            description: 'Warm wool sweater for winter',
            category: 'Sweaters',
            unit_price: 79.99,
            is_active: false,
            created_at: '2024-01-03T00:00:00Z'
          },
          {
            id: 4,
            name: 'Leather Jacket',
            sku: 'JKT-004',
            description: 'Premium leather jacket',
            category: 'Jackets',
            unit_price: 199.99,
            is_active: true,
            created_at: '2024-01-04T00:00:00Z'
          },
          {
            id: 5,
            name: 'Running Shoes',
            sku: 'SHO-005',
            description: 'Comfortable running shoes',
            category: 'Shoes',
            unit_price: 89.99,
            is_active: true,
            created_at: '2024-01-05T00:00:00Z'
          }
        ];
      }
    }
  );

  const createMutation = useMutation(
    async (data: any) => {
      const response = await api.post('/products/', data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('products');
        toast.success('Product created successfully');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create product');
      },
    }
  );

  const updateMutation = useMutation(
    async ({ id, data }: { id: number; data: any }) => {
      const response = await api.put(`/products/${id}`, data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('products');
        toast.success('Product updated successfully');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update product');
      },
    }
  );

  const handleOpen = (product?: Product) => {
    if (product) {
      setEditingProduct(product);
      setFormData({
        name: product.name,
        sku: product.sku,
        description: product.description,
        category: product.category,
        unit_price: product.unit_price,
        is_active: product.is_active,
      });
    } else {
      setEditingProduct(null);
      setFormData({
        name: '',
        sku: '',
        description: '',
        category: '',
        unit_price: 0,
        is_active: true,
      });
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setEditingProduct(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingProduct) {
      updateMutation.mutate({ id: editingProduct.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const columns: GridColDef[] = [
    { 
      field: 'id', 
      headerName: 'ID', 
      width: 80,
      headerAlign: 'center',
      align: 'center',
    },
    { 
      field: 'name', 
      headerName: 'Product Name', 
      width: 250,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: '0.8rem' }}>
            {params.value?.charAt(0)?.toUpperCase()}
          </Avatar>
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            {params.value}
          </Typography>
        </Box>
      ),
    },
    { 
      field: 'sku', 
      headerName: 'SKU', 
      width: 150,
      renderCell: (params) => (
        <Chip 
          label={params.value} 
          size="small" 
          variant="outlined" 
          color="primary"
          sx={{ fontWeight: 500 }}
        />
      ),
    },
    { 
      field: 'category', 
      headerName: 'Category', 
      width: 150,
      renderCell: (params) => (
        <Chip 
          label={params.value} 
          size="small" 
          color="secondary"
          variant="filled"
        />
      ),
    },
    { 
      field: 'unit_price', 
      headerName: 'Unit Price', 
      width: 130, 
      type: 'number',
      renderCell: (params) => (
        <Typography variant="body2" sx={{ fontWeight: 600, color: 'success.main' }}>
          ${typeof params.value === 'number' ? params.value.toFixed(2) : '0.00'}
        </Typography>
      ),
    },
    {
      field: 'created_at',
      headerName: 'Created',
      width: 120,
      type: 'date',
      renderCell: (params) => (
        <Typography variant="body2" color="text.secondary">
          {new Date(params.value).toLocaleDateString()}
        </Typography>
      ),
    },
    {
      field: 'is_active',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value ? 'Active' : 'Inactive'}
          size="small"
          color={params.value ? 'success' : 'error'}
          variant="filled"
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      sortable: false,
      filterable: false,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Tooltip title="View">
            <IconButton size="small" color="info">
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Edit">
            <IconButton 
              size="small" 
              color="primary"
              onClick={() => handleOpen(params.row)}
            >
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton size="small" color="error">
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  return (
    <Box>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'primary.main', width: 48, height: 48 }}>
              <InventoryIcon />
            </Avatar>
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'text.primary' }}>
                Products
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Manage your product catalog and inventory
              </Typography>
            </Box>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpen()}
            size="large"
            sx={{ 
              px: 3,
              py: 1.5,
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 600,
            }}
          >
            Add Product
          </Button>
        </Box>
        
        {/* Stats Cards */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
                {products?.length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Products
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'success.main' }}>
                {products?.filter((p: Product) => p.is_active).length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active Products
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'error.main' }}>
                {products?.filter((p: Product) => !p.is_active).length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Inactive Products
              </Typography>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'warning.main' }}>
                {new Set(products?.map((p: Product) => p.category)).size || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Categories
              </Typography>
            </Card>
          </Grid>
        </Grid>

        {/* Search and Filter Bar */}
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ p: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Search products..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: <Typography sx={{ mr: 1, color: 'text.secondary' }}>🔍</Typography>,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  fullWidth
                  size="small"
                  select
                  label="Category"
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  SelectProps={{
                    native: true,
                  }}
                >
                  <option value="">All Categories</option>
                  {Array.from(new Set(products?.map((p: Product) => p.category) || [])).map((category) => (
                    <option key={String(category)} value={String(category)}>
                      {String(category)}
                    </option>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={12} md={4}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => {
                      setSearchTerm('');
                      setCategoryFilter('');
                    }}
                  >
                    Clear Filters
                  </Button>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => setOpen(true)}
                    startIcon={<AddIcon />}
                  >
                    Add Product
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Box>

      {/* Data Table */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <Box sx={{ height: isMobile ? 500 : 600, width: '100%' }}>
            <DataGrid
              rows={products?.filter((product: Product) => {
                const matchesSearch = searchTerm === '' || 
                  product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  product.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  product.description.toLowerCase().includes(searchTerm.toLowerCase());
                
                const matchesCategory = categoryFilter === '' || product.category === categoryFilter;
                
                return matchesSearch && matchesCategory;
              }) || []}
              columns={columns}
              loading={isLoading}
              pageSizeOptions={[10, 25, 50]}
              disableRowSelectionOnClick
              sx={{
                border: 'none',
                '& .MuiDataGrid-main': {
                  borderRadius: 2,
                },
                '& .MuiDataGrid-columnHeaders': {
                  backgroundColor: 'rgba(25, 118, 210, 0.05)',
                  borderBottom: '2px solid rgba(25, 118, 210, 0.1)',
                  borderRadius: '8px 8px 0 0',
                  '& .MuiDataGrid-columnHeader': {
                    fontWeight: 600,
                    fontSize: '0.9rem',
                    color: 'primary.main',
                  },
                },
                '& .MuiDataGrid-cell': {
                  borderBottom: '1px solid rgba(0,0,0,0.05)',
                  '&:focus': {
                    outline: 'none',
                  },
                },
                '& .MuiDataGrid-row': {
                  '&:hover': {
                    backgroundColor: 'rgba(25, 118, 210, 0.04)',
                  },
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(25, 118, 210, 0.08)',
                    '&:hover': {
                      backgroundColor: 'rgba(25, 118, 210, 0.12)',
                    },
                  },
                },
                '& .MuiDataGrid-footerContainer': {
                  borderTop: '1px solid rgba(0,0,0,0.1)',
                  backgroundColor: 'rgba(25, 118, 210, 0.02)',
                },
              }}
              initialState={{
                pagination: {
                  paginationModel: { pageSize: 10 },
                },
              }}
            />
          </Box>
        </CardContent>
      </Card>

      <Dialog 
        open={open} 
        onClose={handleClose} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
          }
        }}
      >
        <DialogTitle sx={{ 
          pb: 1,
          borderBottom: '1px solid',
          borderColor: 'divider',
          background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.05) 0%, rgba(66, 165, 245, 0.05) 100%)',
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'primary.main', width: 40, height: 40 }}>
              <InventoryIcon />
            </Avatar>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {editingProduct ? 'Edit Product' : 'Add New Product'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {editingProduct ? 'Update product information' : 'Create a new product in your catalog'}
              </Typography>
            </Box>
          </Box>
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent sx={{ p: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Product Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  variant="outlined"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="SKU"
                  value={formData.sku}
                  onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                  required
                  variant="outlined"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  multiline
                  rows={3}
                  variant="outlined"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  required
                  variant="outlined"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Unit Price"
                  type="number"
                  value={formData.unit_price}
                  onChange={(e) => setFormData({ ...formData, unit_price: parseFloat(e.target.value) })}
                  required
                  variant="outlined"
                  InputProps={{
                    startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  required
                  variant="outlined"
                  placeholder="e.g., T-Shirts, Jeans, Shoes"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box sx={{ 
                  p: 2, 
                  border: '1px solid', 
                  borderColor: 'divider', 
                  borderRadius: 2,
                  backgroundColor: 'rgba(0,0,0,0.02)',
                }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.is_active}
                        onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                        color="primary"
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          Product Status
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {formData.is_active ? 'Active and visible' : 'Inactive and hidden'}
                        </Typography>
                      </Box>
                    }
                  />
                </Box>
              </Grid>
              
              {/* Product Summary */}
              <Grid item xs={12}>
                <Box sx={{ 
                  p: 3, 
                  border: '1px solid', 
                  borderColor: 'divider',
                  borderRadius: 2,
                  backgroundColor: 'rgba(0,0,0,0.02)',
                  textAlign: 'center',
                }}>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                    Product Summary
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Selling Price
                      </Typography>
                      <Typography 
                        variant="h5" 
                        sx={{ 
                          fontWeight: 700, 
                          color: 'primary.main'
                        }}
                      >
                        ${formData.unit_price.toFixed(2)}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        SKU
                      </Typography>
                      <Typography 
                        variant="h6" 
                        sx={{ 
                          fontWeight: 600, 
                          color: 'text.primary'
                        }}
                      >
                        {formData.sku || 'Auto-generated'}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Status
                      </Typography>
                      <Chip 
                        label={formData.is_active ? 'Active' : 'Inactive'} 
                        color={formData.is_active ? 'success' : 'error'} 
                        size="small" 
                      />
                    </Box>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ p: 3, pt: 0, gap: 1 }}>
            <Button 
              onClick={handleClose}
              variant="outlined"
              size="large"
              sx={{ minWidth: 100 }}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              variant="contained"
              size="large"
              sx={{ minWidth: 100 }}
            >
              {editingProduct ? 'Update Product' : 'Create Product'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default Products;

