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
  IconButton,
  Tooltip,
  Alert,
  Divider,
  Badge,
  Avatar,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  LinearProgress,
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility,
  Build,
  TrendingUp,
  AttachMoney,
  Print,
  Download,
  Search,
  FilterList,
  PlayArrow,
  Pause,
  Stop,
  CheckCircle,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { api } from '../../services/api';
import toast from 'react-hot-toast';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';

interface ProductionRun {
  id: number;
  run_number: string;
  product_id: number;
  product_name?: string;
  planned_quantity: number;
  actual_quantity?: number;
  labor_cost: number;
  overhead_cost: number;
  status: string;
  start_date: string;
  end_date?: string;
  notes?: string;
  created_at: string;
}

interface Product {
  id: number;
  name: string;
  sku: string;
  unit_price: number;
}

const Production: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [viewOpen, setViewOpen] = useState(false);
  const [editingRun, setEditingRun] = useState<ProductionRun | null>(null);
  const [selectedRun, setSelectedRun] = useState<ProductionRun | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [formData, setFormData] = useState({
    product_id: 0,
    planned_quantity: 0,
    labor_cost: 0,
    overhead_cost: 0,
    start_date: dayjs().format('YYYY-MM-DD'),
    notes: '',
  });

  const queryClient = useQueryClient();

  const { data: productionRuns, isLoading } = useQuery(
    'production',
    async () => {
      const response = await api.get('/production/');
      return response.data;
    }
  );

  const { data: products } = useQuery(
    'products',
    async () => {
      const response = await api.get('/products/');
      return response.data;
    }
  );

  const createMutation = useMutation(
    async (data: any) => {
      const response = await api.post('/production/', data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('production');
        toast.success('Production run created successfully');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create production run');
      }
    }
  );

  const updateMutation = useMutation(
    async (data: any) => {
      const response = await api.put(`/production/${editingRun?.id}`, data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('production');
        toast.success('Production run updated successfully');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update production run');
      }
    }
  );

  const deleteMutation = useMutation(
    async (id: number) => {
      const response = await api.delete(`/production/${id}`);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('production');
        toast.success('Production run deleted successfully');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to delete production run');
      }
    }
  );

  const handleOpen = (run?: ProductionRun) => {
    if (run) {
      setEditingRun(run);
      setFormData({
        product_id: run.product_id,
        planned_quantity: run.planned_quantity,
        labor_cost: run.labor_cost,
        overhead_cost: run.overhead_cost,
        start_date: run.start_date,
        notes: run.notes || '',
      });
    } else {
      setEditingRun(null);
      setFormData({
        product_id: 0,
        planned_quantity: 0,
        labor_cost: 0,
        overhead_cost: 0,
        start_date: dayjs().format('YYYY-MM-DD'),
        notes: '',
      });
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setViewOpen(false);
    setEditingRun(null);
    setFormData({
      product_id: 0,
      planned_quantity: 0,
      labor_cost: 0,
      overhead_cost: 0,
      start_date: dayjs().format('YYYY-MM-DD'),
      notes: '',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingRun) {
      updateMutation.mutate(formData);
    } else {
      createMutation.mutate(formData);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ET', {
      style: 'currency',
      currency: 'ETB',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'info';
      case 'pending': return 'warning';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle color="success" />;
      case 'in_progress': return <PlayArrow color="info" />;
      case 'pending': return <Pause color="warning" />;
      case 'cancelled': return <Stop color="error" />;
      default: return <Build />;
    }
  };

  const filteredRuns = productionRuns?.filter((run: ProductionRun) => {
    const matchesSearch = run.run_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        run.product_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterStatus === 'all' || run.status === filterStatus;
    
    return matchesSearch && matchesFilter;
  }) || [];

  const totalCost = productionRuns?.reduce((sum: number, run: ProductionRun) => 
    sum + run.labor_cost + run.overhead_cost, 0) || 0;

  const completedRuns = productionRuns?.filter((run: ProductionRun) => run.status === 'completed').length || 0;

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'run_number', headerName: 'Run Number', width: 150 },
    { field: 'product_name', headerName: 'Product', width: 200 },
    { field: 'planned_quantity', headerName: 'Planned Qty', width: 120, type: 'number' },
    { field: 'actual_quantity', headerName: 'Actual Qty', width: 120, type: 'number' },
    { 
      field: 'labor_cost', 
      headerName: 'Labor Cost', 
      width: 120, 
      type: 'number',
      renderCell: (params) => formatCurrency(params.value)
    },
    { 
      field: 'overhead_cost', 
      headerName: 'Overhead Cost', 
      width: 120, 
      type: 'number',
      renderCell: (params) => formatCurrency(params.value)
    },
    { 
      field: 'status', 
      headerName: 'Status', 
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          color={getStatusColor(params.value) as any}
          variant="filled"
          size="small"
          icon={getStatusIcon(params.value)}
        />
      )
    },
    { field: 'start_date', headerName: 'Start Date', width: 120 },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 150,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="View Details">
            <IconButton
              size="small"
              onClick={() => {
                setSelectedRun(params.row);
                setViewOpen(true);
              }}
            >
              <Visibility />
            </IconButton>
          </Tooltip>
          <Tooltip title="Edit">
            <IconButton
              size="small"
              onClick={() => handleOpen(params.row)}
            >
              <EditIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete">
            <IconButton
              size="small"
              color="error"
              onClick={() => {
                if (window.confirm('Are you sure you want to delete this production run?')) {
                  deleteMutation.mutate(params.row.id);
                }
              }}
            >
              <DeleteIcon />
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
          <Typography variant="h4">Production Management</Typography>
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
              onClick={() => handleOpen()}
            >
              Add Production Run
            </Button>
          </Box>
        </Box>

        {/* Search and Filter */}
        <Box display="flex" gap={2} mb={3}>
          <TextField
            placeholder="Search production runs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
            }}
            sx={{ flexGrow: 1 }}
          />
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              label="Status"
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="cancelled">Cancelled</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* Summary Cards */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Build color="primary" sx={{ mr: 1 }} />
                  <Typography color="textSecondary" variant="body2">
                    Total Runs
                  </Typography>
                </Box>
                <Typography variant="h5" color="primary.main" fontWeight="bold">
                  {productionRuns?.length || 0}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Production runs
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <CheckCircle color="success" sx={{ mr: 1 }} />
                  <Typography color="textSecondary" variant="body2">
                    Completed
                  </Typography>
                </Box>
                <Typography variant="h5" color="success.main" fontWeight="bold">
                  {completedRuns}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Finished runs
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <AttachMoney color="info" sx={{ mr: 1 }} />
                  <Typography color="textSecondary" variant="body2">
                    Total Cost
                  </Typography>
                </Box>
                <Typography variant="h5" color="info.main" fontWeight="bold">
                  {formatCurrency(totalCost)}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Production costs
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <TrendingUp color="warning" sx={{ mr: 1 }} />
                  <Typography color="textSecondary" variant="body2">
                    Efficiency
                  </Typography>
                </Box>
                <Typography variant="h5" color="warning.main" fontWeight="bold">
                  {productionRuns?.length > 0 ? Math.round((completedRuns / productionRuns.length) * 100) : 0}%
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Completion rate
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Data Grid */}
        <Box sx={{ height: 400, width: '100%' }}>
          <DataGrid
            rows={filteredRuns}
            columns={columns}
            loading={isLoading}
            initialState={{
              pagination: {
                paginationModel: { pageSize: 10 },
              },
            }}
            pageSizeOptions={[5, 10, 25]}
            disableRowSelectionOnClick
          />
        </Box>

        {/* Add/Edit Production Run Dialog */}
        <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
          <DialogTitle>
            {editingRun ? 'Edit Production Run' : 'Add New Production Run'}
          </DialogTitle>
          <form onSubmit={handleSubmit}>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth required>
                    <InputLabel>Product</InputLabel>
                    <Select
                      value={formData.product_id}
                      onChange={(e) => setFormData({ ...formData, product_id: e.target.value as number })}
                      label="Product"
                    >
                      {products?.map((product: Product) => (
                        <MenuItem key={product.id} value={product.id}>
                          {product.name} - {product.sku}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Planned Quantity"
                    type="number"
                    value={formData.planned_quantity}
                    onChange={(e) => setFormData({ ...formData, planned_quantity: parseFloat(e.target.value) || 0 })}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Labor Cost"
                    type="number"
                    value={formData.labor_cost}
                    onChange={(e) => setFormData({ ...formData, labor_cost: parseFloat(e.target.value) || 0 })}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Overhead Cost"
                    type="number"
                    value={formData.overhead_cost}
                    onChange={(e) => setFormData({ ...formData, overhead_cost: parseFloat(e.target.value) || 0 })}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <DatePicker
                    label="Start Date"
                    value={dayjs(formData.start_date)}
                    onChange={(date) => setFormData({ ...formData, start_date: date?.format('YYYY-MM-DD') || '' })}
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
            </DialogContent>
            <DialogActions>
              <Button onClick={handleClose}>Cancel</Button>
              <Button type="submit" variant="contained">
                {editingRun ? 'Update' : 'Create'}
              </Button>
            </DialogActions>
          </form>
        </Dialog>

        {/* View Production Run Dialog */}
        <Dialog open={viewOpen} onClose={() => setViewOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Production Run Details</DialogTitle>
          <DialogContent>
            {selectedRun && (
              <Box>
                <Grid container spacing={2} mb={3}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">Run Number</Typography>
                    <Typography variant="body1">{selectedRun.run_number}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">Product</Typography>
                    <Typography variant="body1">{selectedRun.product_name}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">Planned Quantity</Typography>
                    <Typography variant="body1">{selectedRun.planned_quantity}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">Actual Quantity</Typography>
                    <Typography variant="body1">{selectedRun.actual_quantity || 'N/A'}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">Labor Cost</Typography>
                    <Typography variant="body1">{formatCurrency(selectedRun.labor_cost)}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">Overhead Cost</Typography>
                    <Typography variant="body1">{formatCurrency(selectedRun.overhead_cost)}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">Status</Typography>
                    <Chip
                      label={selectedRun.status}
                      color={getStatusColor(selectedRun.status) as any}
                      variant="filled"
                      icon={getStatusIcon(selectedRun.status)}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="textSecondary">Start Date</Typography>
                    <Typography variant="body1">{selectedRun.start_date}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary">Total Cost</Typography>
                    <Typography variant="h6" color="primary">
                      {formatCurrency(selectedRun.labor_cost + selectedRun.overhead_cost)}
                    </Typography>
                  </Grid>
                  {selectedRun.notes && (
                    <Grid item xs={12}>
                      <Typography variant="body2" color="textSecondary">Notes</Typography>
                      <Typography variant="body1">{selectedRun.notes}</Typography>
                    </Grid>
                  )}
                </Grid>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setViewOpen(false)}>Close</Button>
            <Button variant="contained" startIcon={<EditIcon />} onClick={() => {
              setViewOpen(false);
              handleOpen(selectedRun || undefined);
            }}>
              Edit
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};

export default Production;

