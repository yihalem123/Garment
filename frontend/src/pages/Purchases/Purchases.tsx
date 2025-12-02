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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  Divider,
  Badge,
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility,
  AttachMoney,
  Inventory,
  TrendingUp,
  Receipt,
  Print,
  Download,
  Search,
  FilterList,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { api } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';

interface Purchase {
  id: number;
  order_id: string;
  supplier_name: string;
  supplier_invoice?: string;
  total_amount: number;
  status: string;
  purchase_date: string;
  notes?: string;
  created_at: string;
  purchase_lines?: PurchaseLine[];
}

interface PurchaseLine {
  id?: number;
  raw_material_id?: number;
  raw_material_name?: string;
  item_name?: string;
  item_description?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  item_type?: 'raw_material' | 'custom';
}

interface RawMaterial {
  id: number;
  name: string;
  sku: string;
  unit_price: number;
  cost_price: number;
}

const Purchases: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [viewOpen, setViewOpen] = useState(false);
  const [selectedPurchase, setSelectedPurchase] = useState<Purchase | null>(null);
  const [purchaseLines, setPurchaseLines] = useState<PurchaseLine[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [formData, setFormData] = useState({
    supplier_name: '',
    supplier_invoice: '',
    purchase_date: dayjs().format('YYYY-MM-DD'),
    notes: '',
  });

  const queryClient = useQueryClient();
  const { user } = useAuth();

  const { data: purchases, isLoading } = useQuery(
    'purchases',
    async () => {
      try {
      const response = await api.get('/purchases/');
      return response.data;
      } catch (error) {
        console.warn('API not available, using mock data:', error);
        return [
          {
            id: 1,
            supplier_name: 'Textile Supplier A',
            supplier_invoice: 'INV-001',
            total_amount: 15000,
            status: 'received',
            purchase_date: '2024-01-15',
            notes: 'Cotton fabric purchase',
            purchase_lines: [
              { id: 1, raw_material_id: 1, quantity: 100, unit_price: 150, total_price: 15000 }
            ]
          },
          {
            id: 2,
            supplier_name: 'Thread Supplier B',
            supplier_invoice: 'INV-002',
            total_amount: 5000,
            status: 'pending',
            purchase_date: '2024-01-16',
            notes: 'Polyester thread purchase',
            purchase_lines: [
              { id: 2, raw_material_id: 2, quantity: 50, unit_price: 100, total_price: 5000 }
            ]
          },
          {
            id: 3,
            supplier_name: 'Equipment Supplier C',
            supplier_invoice: 'INV-003',
            total_amount: 25000,
            status: 'received',
            purchase_date: '2024-01-17',
            notes: 'Sewing machine purchase',
            purchase_lines: [
              { id: 3, item_name: 'Industrial Sewing Machine', item_description: 'Heavy duty sewing machine', quantity: 1, unit_price: 25000, total_price: 25000 }
            ]
          }
        ];
      }
    }
  );

  // Filter purchases based on search and status
  const filteredPurchases = purchases?.filter((purchase: Purchase) => {
    const matchesSearch = searchTerm === '' || 
      purchase.supplier_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      purchase.supplier_invoice?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      purchase.status.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === '' || purchase.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  }) || [];

  const { data: rawMaterials } = useQuery(
    'rawMaterials',
    async () => {
      try {
        const response = await api.get('/raw-materials/');
        return response.data;
      } catch (error) {
        console.warn('Raw materials API not available, using mock data:', error);
        return [
          {
            id: 1,
            name: 'Cotton Fabric',
            sku: 'CF-001',
            unit_price: 150,
            unit_of_measure: 'meter',
            description: 'High quality cotton fabric'
          },
          {
            id: 2,
            name: 'Polyester Thread',
            sku: 'PT-002',
            unit_price: 100,
            unit_of_measure: 'spool',
            description: 'Strong polyester thread'
          },
          {
            id: 3,
            name: 'Zipper',
            sku: 'ZIP-003',
            unit_price: 50,
            unit_of_measure: 'piece',
            description: 'Metal zipper 20cm'
          }
        ];
      }
    }
  );

  const { data: shops } = useQuery(
    'shops',
    async () => {
      const response = await api.get('/shops/');
      return response.data;
    }
  );

  const createMutation = useMutation(
    async (data: any) => {
      const response = await api.post('/purchases/', data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('purchases');
        toast.success('Purchase created successfully');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create purchase');
      }
    }
  );

  const handleClose = () => {
    setOpen(false);
    setViewOpen(false);
    setFormData({
      supplier_name: '',
      supplier_invoice: '',
      purchase_date: dayjs().format('YYYY-MM-DD'),
      notes: '',
    });
    setPurchaseLines([]);
  };

  const addPurchaseLine = () => {
    const newLine = {
      raw_material_id: rawMaterials?.[0]?.id || '',
      item_name: '',
      item_description: '',
      quantity: 1,
      unit_price: 0,
      total_price: 0,
      item_type: 'raw_material' as const,
    };
    console.log('Adding new purchase line:', newLine);
    setPurchaseLines([...purchaseLines, newLine]);
  };

  const updatePurchaseLine = (index: number, field: keyof PurchaseLine, value: any) => {
    const updated = [...purchaseLines];
    updated[index] = { ...updated[index], [field]: value };
    
    if (field === 'quantity' || field === 'unit_price') {
      updated[index].total_price = updated[index].quantity * updated[index].unit_price;
    }
    
    setPurchaseLines(updated);
  };

  const removePurchaseLine = (index: number) => {
    setPurchaseLines(purchaseLines.filter((_, i) => i !== index));
  };

  const calculateTotal = () => {
    return purchaseLines.reduce((sum, line) => sum + line.total_price, 0);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const totalAmount = calculateTotal();

    const purchaseData = {
      ...formData,
      total_amount: totalAmount,
      purchase_lines: purchaseLines,
    };

    createMutation.mutate(purchaseData);
  };

  const formatCurrency = (amount: number | string | undefined) => {
    const numAmount = typeof amount === 'string' ? parseFloat(amount) : (amount || 0);
    if (isNaN(numAmount)) return 'ETB 0.00';
    
    return new Intl.NumberFormat('en-ET', {
      style: 'currency',
      currency: 'ETB',
      minimumFractionDigits: 2,
    }).format(numAmount);
  };

  const getItemName = (line: any) => {
    // If it's a custom item, use item_name
    if (line.item_name) {
      return line.item_name;
    }
    
    // If it's a raw material, look it up in the raw materials list
    if (line.raw_material_id && rawMaterials) {
      const material = rawMaterials.find((m: RawMaterial) => m.id === line.raw_material_id);
      return material?.name || 'Unknown Raw Material';
    }
    
    // Fallback
    return 'Unknown Item';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'received': return 'success';
      case 'pending': return 'warning';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const columns: GridColDef[] = [
    { 
      field: 'id', 
      headerName: 'ID', 
      width: 80,
      headerAlign: 'center',
      align: 'center',
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="bold" color="primary">
          #{params.value}
        </Typography>
      )
    },
    { 
      field: 'order_id', 
      headerName: 'Order ID', 
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="medium" color="info.main">
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'supplier_name', 
      headerName: 'Supplier', 
      width: 200,
      renderCell: (params) => (
        <Box>
          <Typography variant="body2" fontWeight="medium">
            {params.value}
          </Typography>
        </Box>
      )
    },
    { 
      field: 'supplier_invoice', 
      headerName: 'Invoice', 
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2" color="text.secondary">
          {params.value || 'N/A'}
        </Typography>
      )
    },
    { 
      field: 'total_amount', 
      headerName: 'Total Amount', 
      width: 160, 
      type: 'number',
      headerAlign: 'right',
      align: 'right',
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="bold" color="success.main">
          {formatCurrency(params.value)}
        </Typography>
      )
    },
    { 
      field: 'status', 
      headerName: 'Status', 
      width: 130,
      headerAlign: 'center',
      align: 'center',
      renderCell: (params) => (
        <Chip
          label={params.value?.charAt(0).toUpperCase() + params.value?.slice(1)}
          color={getStatusColor(params.value) as any}
          variant="filled"
          size="small"
          sx={{ fontWeight: 'bold' }}
        />
      )
    },
    { 
      field: 'purchase_date', 
      headerName: 'Date', 
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2">
          {new Date(params.value).toLocaleDateString()}
        </Typography>
      )
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 140,
      headerAlign: 'center',
      align: 'center',
      sortable: false,
      filterable: false,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
          <Tooltip title="View Details">
            <IconButton
              size="small"
              onClick={() => {
                setSelectedPurchase(params.row);
                setViewOpen(true);
              }}
              sx={{ 
                color: 'primary.main',
                '&:hover': { backgroundColor: 'primary.light', color: 'white' }
              }}
            >
              <Visibility fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Print Receipt">
            <IconButton 
              size="small"
              sx={{ 
                color: 'secondary.main',
                '&:hover': { backgroundColor: 'secondary.light', color: 'white' }
              }}
            >
              <Print fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
    <Box>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
      <Typography variant="h4" gutterBottom>
            Purchase Management
          </Typography>
          <Box display="flex" gap={2}>
            <Button
              variant="outlined"
              startIcon={<Download />}
            >
              Export
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpen(true)}
            >
              Add Purchase
            </Button>
          </Box>
        </Box>

        {/* Summary Cards */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <AttachMoney color="primary" sx={{ mr: 1 }} />
                  <Typography color="textSecondary" variant="body2">
                    Total Purchases
                  </Typography>
                </Box>
                <Typography variant="h5" color="primary.main" fontWeight="bold">
                  {formatCurrency(purchases?.reduce((sum: number, p: Purchase) => {
                    const amount = typeof p.total_amount === 'string' ? parseFloat(p.total_amount) : (p.total_amount || 0);
                    return sum + (isNaN(amount) ? 0 : amount);
                  }, 0) || 0)}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {purchases?.length || 0} orders
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Inventory color="success" sx={{ mr: 1 }} />
                  <Typography color="textSecondary" variant="body2">
                    This Month
                  </Typography>
                </Box>
                <Typography variant="h5" color="success.main" fontWeight="bold">
                  {formatCurrency(purchases?.filter((p: Purchase) => {
                    try {
                      return new Date(p.purchase_date).getMonth() === new Date().getMonth() &&
                             new Date(p.purchase_date).getFullYear() === new Date().getFullYear();
                    } catch {
                      return false;
                    }
                  }).reduce((sum: number, p: Purchase) => {
                    const amount = typeof p.total_amount === 'string' ? parseFloat(p.total_amount) : (p.total_amount || 0);
                    return sum + (isNaN(amount) ? 0 : amount);
                  }, 0) || 0)}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Current month
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <TrendingUp color="info" sx={{ mr: 1 }} />
                  <Typography color="textSecondary" variant="body2">
                    Pending Orders
                  </Typography>
                </Box>
                <Typography variant="h5" color="info.main" fontWeight="bold">
                  {purchases?.filter((p: Purchase) => p.status === 'pending').length || 0}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Awaiting delivery
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Receipt color="warning" sx={{ mr: 1 }} />
                  <Typography color="textSecondary" variant="body2">
                    Average Order
                  </Typography>
                </Box>
                <Typography variant="h5" color="warning.main" fontWeight="bold">
                  {formatCurrency(
                    purchases?.length > 0 
                      ? purchases.reduce((sum: number, p: Purchase) => {
                          const amount = typeof p.total_amount === 'string' ? parseFloat(p.total_amount) : (p.total_amount || 0);
                          return sum + (isNaN(amount) ? 0 : amount);
                        }, 0) / purchases.length 
                      : 0
                  )}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Per purchase
      </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Search and Filter Bar */}
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
              <TextField
                label="Search purchases..."
                variant="outlined"
                size="small"
                sx={{ minWidth: 250 }}
                placeholder="Search by supplier, invoice, or status..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <TextField
                select
                label="Status"
                variant="outlined"
                size="small"
                sx={{ minWidth: 120 }}
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="">All Status</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="received">Received</MenuItem>
                <MenuItem value="cancelled">Cancelled</MenuItem>
              </TextField>
              <Button 
                variant="outlined" 
                startIcon={<FilterList />}
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('');
                }}
              >
                Clear Filters
              </Button>
            </Box>
          </CardContent>
        </Card>

        {/* Data Grid */}
        <Card sx={{ height: 600, width: '100%' }}>
          <CardContent sx={{ height: '100%', p: 0 }}>
        <DataGrid
              rows={filteredPurchases}
          columns={columns}
          loading={isLoading}
            initialState={{
              pagination: {
                paginationModel: { pageSize: 25 },
              },
            }}
            pageSizeOptions={[10, 25, 50, 100]}
          disableRowSelectionOnClick
              density="comfortable"
              autoHeight={false}
              disableColumnMenu={false}
              sortingMode="server"
              filterMode="client"
              sx={{
                border: 'none',
                '& .MuiDataGrid-cell': {
                  borderBottom: '1px solid #f0f0f0',
                },
                '& .MuiDataGrid-columnHeaders': {
                  backgroundColor: '#f8f9fa',
                  borderBottom: '2px solid #e0e0e0',
                },
                '& .MuiDataGrid-row:hover': {
                  backgroundColor: '#f5f5f5',
                },
                '& .MuiDataGrid-footerContainer': {
                  borderTop: '1px solid #e0e0e0',
                  backgroundColor: '#f8f9fa',
                },
              }}
            />
          </CardContent>
        </Card>

        {/* Add Purchase Dialog */}
        <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
          <DialogTitle>Add New Purchase</DialogTitle>
          <form onSubmit={handleSubmit}>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Supplier Name"
                    value={formData.supplier_name}
                    onChange={(e) => setFormData({ ...formData, supplier_name: e.target.value })}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Supplier Invoice"
                    value={formData.supplier_invoice}
                    onChange={(e) => setFormData({ ...formData, supplier_invoice: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <DatePicker
                    label="Purchase Date"
                    value={dayjs(formData.purchase_date)}
                    onChange={(date) => setFormData({ ...formData, purchase_date: date?.format('YYYY-MM-DD') || '' })}
                    slotProps={{ textField: { fullWidth: true } }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Notes"
                    multiline
                    rows={3}
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  />
                </Grid>
              </Grid>

              <Divider sx={{ my: 3 }} />

              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Purchase Items</Typography>
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={addPurchaseLine}
                >
                  Add Item
                </Button>
              </Box>

              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Item Type</TableCell>
                      <TableCell>Item</TableCell>
                      <TableCell>Quantity</TableCell>
                      <TableCell>Unit Price</TableCell>
                      <TableCell>Total</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {purchaseLines.map((line, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <FormControl fullWidth size="small">
                            <Select
                              value={line.item_type || 'raw_material'}
                              onChange={(e) => {
                                const newType = e.target.value as 'raw_material' | 'custom';
                                console.log('Switching to:', newType, 'for line:', index);
                                
                                // Update the item type first
                                const updated = [...purchaseLines];
                                updated[index] = { ...updated[index], item_type: newType };
                                
                                if (newType === 'custom') {
                                  updated[index].raw_material_id = undefined;
                                  updated[index].item_name = '';
                                  updated[index].item_description = '';
                                } else {
                                  updated[index].raw_material_id = rawMaterials?.[0]?.id || '';
                                  updated[index].item_name = '';
                                  updated[index].item_description = '';
                                }
                                
                                setPurchaseLines(updated);
                              }}
                            >
                              <MenuItem value="raw_material">Raw Material</MenuItem>
                              <MenuItem value="custom">Custom Item</MenuItem>
                            </Select>
                          </FormControl>
                        </TableCell>
                        <TableCell>
                          {(line.item_type === 'raw_material' || line.item_type === undefined) ? (
                            <FormControl fullWidth size="small">
                              <Select
                                value={line.raw_material_id || ''}
                                onChange={(e) => updatePurchaseLine(index, 'raw_material_id', e.target.value)}
                              >
                                <MenuItem value="">
                                  <em>Select Raw Material</em>
                                </MenuItem>
                                {rawMaterials?.map((material: RawMaterial) => (
                                  <MenuItem key={material.id} value={material.id}>
                                    {material.name} - {formatCurrency(material.unit_price)}
                                  </MenuItem>
                                ))}
                              </Select>
                            </FormControl>
                          ) : (
                            <Box>
                              <Typography variant="caption" color="primary" sx={{ mb: 1, display: 'block' }}>
                                Custom Item Fields
                              </Typography>
                              <TextField
                                fullWidth
                                size="small"
                                placeholder="Item Name"
                                value={line.item_name || ''}
                                onChange={(e) => updatePurchaseLine(index, 'item_name', e.target.value)}
                                sx={{ mb: 1 }}
                              />
                              <TextField
                                fullWidth
                                size="small"
                                placeholder="Description"
                                value={line.item_description || ''}
                                onChange={(e) => updatePurchaseLine(index, 'item_description', e.target.value)}
                              />
                            </Box>
                          )}
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            type="number"
                            value={line.quantity}
                            onChange={(e) => updatePurchaseLine(index, 'quantity', parseFloat(e.target.value) || 0)}
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            type="number"
                            value={line.unit_price}
                            onChange={(e) => updatePurchaseLine(index, 'unit_price', parseFloat(e.target.value) || 0)}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {formatCurrency(line.total_price)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <IconButton
                            size="small"
                            onClick={() => removePurchaseLine(index)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              <Box display="flex" justifyContent="flex-end" mt={2}>
                <Typography variant="h6">
                  Total: {formatCurrency(calculateTotal())}
                </Typography>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleClose}>Cancel</Button>
              <Button type="submit" variant="contained" disabled={purchaseLines.length === 0}>
                Create Purchase
              </Button>
            </DialogActions>
          </form>
        </Dialog>

        {/* View Purchase Dialog */}
        <Dialog open={viewOpen} onClose={() => setViewOpen(false)} maxWidth="lg" fullWidth>
          <DialogTitle>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6">Purchase Details - #{selectedPurchase?.id}</Typography>
              <Chip
                label={selectedPurchase?.status ? selectedPurchase.status.charAt(0).toUpperCase() + selectedPurchase.status.slice(1) : ''}
                color={getStatusColor(selectedPurchase?.status || '') as any}
                variant="filled"
        />
      </Box>
          </DialogTitle>
          <DialogContent>
            {selectedPurchase && (
              <Box>
                {/* Purchase Info Header */}
                <Grid container spacing={2} mb={3} sx={{ backgroundColor: '#f8f9fa', p: 2, borderRadius: 1 }}>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>Supplier</Typography>
                    <Typography variant="body1" fontWeight="medium">{selectedPurchase.supplier_name}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>Invoice</Typography>
                    <Typography variant="body1">{selectedPurchase.supplier_invoice || 'N/A'}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>Date</Typography>
                    <Typography variant="body1">{new Date(selectedPurchase.purchase_date).toLocaleDateString()}</Typography>
                  </Grid>
                </Grid>

                {/* Purchased Items Table */}
                <Typography variant="h6" gutterBottom sx={{ mt: 2, mb: 2 }}>
                  Purchased Items
                </Typography>
                <TableContainer component={Paper} sx={{ mb: 3 }}>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                        <TableCell><strong>Item Name</strong></TableCell>
                        <TableCell align="right"><strong>Quantity</strong></TableCell>
                        <TableCell align="right"><strong>Unit Price</strong></TableCell>
                        <TableCell align="right"><strong>Total Price</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {selectedPurchase.purchase_lines?.map((line: any, index: number) => (
                        <TableRow key={index} hover>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              {getItemName(line)}
                            </Typography>
                            {line.item_description && (
                              <Typography variant="caption" color="textSecondary">
                                {line.item_description}
                              </Typography>
                            )}
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2">{line.quantity}</Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2">{formatCurrency(line.unit_price)}</Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight="bold" color="primary">
                              {formatCurrency(line.total_price)}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      )) || (
                        <TableRow>
                          <TableCell colSpan={4} align="center">
                            <Typography variant="body2" color="textSecondary">
                              No items found
                            </Typography>
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>

                {/* Total Amount */}
                <Box display="flex" justifyContent="flex-end" mt={2} p={2} sx={{ backgroundColor: '#f8f9fa', borderRadius: 1 }}>
                  <Typography variant="h6" color="primary" fontWeight="bold">
                    Total: {formatCurrency(selectedPurchase.total_amount)}
                  </Typography>
                </Box>

                {/* Notes */}
                {selectedPurchase.notes && (
                  <Box mt={2}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>Notes</Typography>
                    <Typography variant="body2">{selectedPurchase.notes}</Typography>
                  </Box>
                )}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setViewOpen(false)}>Close</Button>
            <Button variant="contained" startIcon={<Print />}>
              Print Receipt
            </Button>
          </DialogActions>
        </Dialog>
    </Box>
    </LocalizationProvider>
  );
};

export default Purchases;

