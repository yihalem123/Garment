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
  Avatar,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
  Alert,
  Divider,
  Badge,
  Checkbox,
  FormControlLabel,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  AttachMoney,
  Receipt,
  People,
  TrendingUp,
  AccountBalance,
  Payment,
  Schedule,
  CheckCircle,
  Pending,
  Cancel,
  Print,
  Download,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { api } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs from 'dayjs';

interface PayrollRecord {
  id: number;
  employee_id: number;
  employee_name: string;
  payroll_period_start: string;
  payroll_period_end: string;
  base_salary: number;
  hours_worked?: number;
  overtime_hours?: number;
  hourly_rate?: number;
  overtime_rate?: number;
  regular_pay: number;
  overtime_pay?: number;
  commission_pay?: number;
  bonus_pay?: number;
  tax_deduction?: number;
  insurance_deduction?: number;
  other_deductions?: number;
  gross_pay: number;
  total_deductions: number;
  net_pay: number;
  payment_date?: string;
  payment_method?: string;
  payment_reference?: string;
  status: string;
  notes?: string;
  created_at: string;
}

interface PayrollSummary {
  id: number;
  period_start: string;
  period_end: string;
  shop_id?: number;
  shop_name?: string;
  total_employees: number;
  total_gross_pay: number;
  total_deductions: number;
  total_net_pay: number;
  is_processed: boolean;
  processed_at?: string;
  processed_by?: number;
  created_at: string;
}

const Payroll: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [processOpen, setProcessOpen] = useState(false);
  const [paymentOpen, setPaymentOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [selectedRecords, setSelectedRecords] = useState<number[]>([]);
  const [formData, setFormData] = useState({
    period_start: dayjs().startOf('month').format('YYYY-MM-DD'),
    period_end: dayjs().endOf('month').format('YYYY-MM-DD'),
    shop_id: undefined as number | undefined,
    include_inactive: false,
  });
  const [paymentData, setPaymentData] = useState({
    payment_method: 'bank_transfer',
    payment_reference: '',
    payment_date: dayjs().format('YYYY-MM-DD'),
    notes: '',
  });

  const queryClient = useQueryClient();
  const { user } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const { data: payrollRecords, isLoading: recordsLoading } = useQuery(
    'payrollRecords',
    async () => {
      try {
        const response = await api.get('/payroll/records');
        return response.data;
      } catch (error) {
        console.warn('API not available, using mock data:', error);
        return [
          {
            id: 1,
            employee_id: 1,
            employee_name: "John Doe",
            payroll_period_start: "2024-01-01",
            payroll_period_end: "2024-01-31",
            base_salary: 4500,
            hours_worked: 160,
            overtime_hours: 8,
            hourly_rate: 28.125,
            overtime_rate: 1.5,
            regular_pay: 4500,
            overtime_pay: 337.5,
            commission_pay: 0,
            bonus_pay: 0,
            tax_deduction: 675,
            insurance_deduction: 225,
            other_deductions: 0,
            gross_pay: 4837.5,
            total_deductions: 900,
            net_pay: 3937.5,
            payment_date: "2024-02-01",
            payment_method: "bank_transfer",
            payment_reference: "PAY-2024-001",
            status: "paid",
            notes: "Monthly salary payment",
            created_at: "2024-01-31T00:00:00Z"
          }
        ];
      }
    }
  );

  const { data: payrollSummaries, isLoading: summariesLoading } = useQuery(
    'payrollSummaries',
    async () => {
      try {
        const response = await api.get('/payroll/summaries');
        return response.data;
      } catch (error) {
        console.warn('API not available, using mock data:', error);
        return [
          {
            id: 1,
            period_start: "2024-01-01",
            period_end: "2024-01-31",
            shop_id: 1,
            shop_name: "Main Warehouse",
            total_employees: 8,
            total_gross_pay: 28300,
            total_deductions: 4245,
            total_net_pay: 24055,
            is_processed: true,
            processed_at: "2024-01-31T10:00:00Z",
            processed_by: 1,
            created_at: "2024-01-31T00:00:00Z"
          }
        ];
      }
    }
  );

  const { data: payrollStats } = useQuery(
    'payrollStats',
    async () => {
      try {
        const response = await api.get('/payroll/statistics/overview');
        return response.data;
      } catch (error) {
        return {
          current_month: {
            total_paid: 24055,
            records_count: 8,
            average_pay: 3006.88
          },
          pending_payments: {
            total_pending: 8500,
            pending_count: 3
          }
        };
      }
    }
  );

  const processPayrollMutation = useMutation(
    async (data: any) => {
      const response = await api.post('/payroll/process', data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('payrollRecords');
        queryClient.invalidateQueries('payrollSummaries');
        queryClient.invalidateQueries('payrollStats');
        toast.success('Payroll processed successfully!');
        setProcessOpen(false);
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to process payroll');
      }
    }
  );

  const processPaymentMutation = useMutation(
    async (data: any) => {
      const response = await api.post('/payroll/payment', data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('payrollRecords');
        queryClient.invalidateQueries('payrollSummaries');
        queryClient.invalidateQueries('payrollStats');
        toast.success('Payment processed successfully!');
        setPaymentOpen(false);
        setSelectedRecords([]);
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to process payment');
      }
    }
  );

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleProcessPayroll = () => {
    processPayrollMutation.mutate(formData);
  };

  const handleProcessPayment = () => {
    if (selectedRecords.length === 0) {
      toast.error('Please select payroll records to process payment');
      return;
    }
    
    processPaymentMutation.mutate({
      payroll_record_ids: selectedRecords,
      ...paymentData
    });
  };

  const handleRecordSelection = (recordId: number, checked: boolean) => {
    if (checked) {
      setSelectedRecords([...selectedRecords, recordId]);
    } else {
      setSelectedRecords(selectedRecords.filter(id => id !== recordId));
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
      case 'paid': return 'success';
      case 'pending': return 'warning';
      case 'processed': return 'info';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'paid': return <CheckCircle color="success" />;
      case 'pending': return <Pending color="warning" />;
      case 'processed': return <Schedule color="info" />;
      case 'cancelled': return <Cancel color="error" />;
      default: return <Pending />;
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'employee_name',
      headerName: 'Employee',
      width: 200,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar sx={{ width: 32, height: 32, fontSize: '0.875rem' }}>
            {params.value?.charAt(0) || 'E'}
          </Avatar>
          <Typography variant="body2" fontWeight="bold">
            {params.value}
          </Typography>
        </Box>
      )
    },
    {
      field: 'payroll_period_start',
      headerName: 'Period',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2">
          {dayjs(params.value).format('MMM DD')} - {dayjs(params.row.payroll_period_end).format('MMM DD')}
        </Typography>
      )
    },
    {
      field: 'gross_pay',
      headerName: 'Gross Pay',
      width: 120,
      type: 'number',
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="bold" color="primary">
          {formatCurrency(params.value)}
        </Typography>
      )
    },
    {
      field: 'total_deductions',
      headerName: 'Deductions',
      width: 120,
      type: 'number',
      renderCell: (params) => (
        <Typography variant="body2" color="error">
          {formatCurrency(params.value)}
        </Typography>
      )
    },
    {
      field: 'net_pay',
      headerName: 'Net Pay',
      width: 120,
      type: 'number',
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="bold" color="success.main">
          {formatCurrency(params.value)}
        </Typography>
      )
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {getStatusIcon(params.value)}
          <Chip
            label={params.value}
            size="small"
            color={getStatusColor(params.value) as any}
            variant="filled"
          />
        </Box>
      )
    },
    {
      field: 'payment_date',
      headerName: 'Payment Date',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value ? dayjs(params.value).format('MMM DD, YYYY') : 'Not paid'}
        </Typography>
      )
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 100,
      sortable: false,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Print Payslip">
            <IconButton size="small">
              <Print fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Download">
            <IconButton size="small">
              <Download fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      )
    }
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Payroll Management</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Payment />}
            onClick={() => setPaymentOpen(true)}
            disabled={selectedRecords.length === 0}
          >
            Process Payment ({selectedRecords.length})
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setProcessOpen(true)}
          >
            Process Payroll
          </Button>
        </Box>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AttachMoney sx={{ mr: 1 }} />
                <Typography variant="h6">Total Paid</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold">
                {formatCurrency(payrollStats?.current_month?.total_paid || 0)}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                This month
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #2196F3 0%, #1976D2 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Receipt sx={{ mr: 1 }} />
                <Typography variant="h6">Records Processed</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold">
                {payrollStats?.current_month?.records_count || 0}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                This month
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #FF9800 0%, #F57C00 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp sx={{ mr: 1 }} />
                <Typography variant="h6">Average Pay</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold">
                {formatCurrency(payrollStats?.current_month?.average_pay || 0)}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Per employee
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Pending sx={{ mr: 1 }} />
                <Typography variant="h6">Pending Payments</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold">
                {payrollStats?.pending_payments?.pending_count || 0}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                {formatCurrency(payrollStats?.pending_payments?.total_pending || 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Payroll Records" />
          <Tab label="Payroll Summaries" />
          <Tab label="Payment Processing" />
        </Tabs>
      </Box>

      {/* Payroll Records */}
      {tabValue === 0 && (
        <Box sx={{ height: 500, width: '100%' }}>
          <DataGrid
            rows={payrollRecords || []}
            columns={columns}
            loading={recordsLoading}
            pageSizeOptions={[5, 10, 25]}
            disableRowSelectionOnClick
            checkboxSelection
            onRowSelectionModelChange={(newSelection) => {
              setSelectedRecords(newSelection as number[]);
            }}
            sx={{
              '& .MuiDataGrid-row:hover': {
                backgroundColor: 'rgba(25, 118, 210, 0.04)',
              },
            }}
          />
        </Box>
      )}

      {/* Payroll Summaries */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          {payrollSummaries?.map((summary: PayrollSummary) => (
            <Grid item xs={12} md={6} key={summary.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">
                      {dayjs(summary.period_start).format('MMM YYYY')}
                    </Typography>
                    <Chip
                      label={summary.is_processed ? 'Processed' : 'Pending'}
                      color={summary.is_processed ? 'success' : 'warning'}
                      size="small"
                    />
                  </Box>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Employees
                      </Typography>
                      <Typography variant="h6" fontWeight="bold">
                        {summary.total_employees}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Shop
                      </Typography>
                      <Typography variant="body2">
                        {summary.shop_name || 'All Shops'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Divider sx={{ my: 1 }} />
                    </Grid>
                    <Grid item xs={4}>
                      <Typography variant="body2" color="text.secondary">
                        Gross Pay
                      </Typography>
                      <Typography variant="body2" fontWeight="bold" color="primary">
                        {formatCurrency(summary.total_gross_pay)}
                      </Typography>
                    </Grid>
                    <Grid item xs={4}>
                      <Typography variant="body2" color="text.secondary">
                        Deductions
                      </Typography>
                      <Typography variant="body2" fontWeight="bold" color="error">
                        {formatCurrency(summary.total_deductions)}
                      </Typography>
                    </Grid>
                    <Grid item xs={4}>
                      <Typography variant="body2" color="text.secondary">
                        Net Pay
                      </Typography>
                      <Typography variant="body2" fontWeight="bold" color="success.main">
                        {formatCurrency(summary.total_net_pay)}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Payment Processing */}
      {tabValue === 2 && (
        <Box>
          <Alert severity="info" sx={{ mb: 2 }}>
            Select payroll records from the "Payroll Records" tab to process payments.
          </Alert>
          <Typography variant="h6" gutterBottom>
            Selected Records: {selectedRecords.length}
          </Typography>
          {selectedRecords.length > 0 && (
            <Alert severity="success">
              {selectedRecords.length} records selected for payment processing.
            </Alert>
          )}
        </Box>
      )}

      {/* Process Payroll Dialog */}
      <Dialog open={processOpen} onClose={() => setProcessOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Process Payroll</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <DatePicker
                label="Period Start"
                value={dayjs(formData.period_start)}
                onChange={(date) => setFormData({ ...formData, period_start: date?.format('YYYY-MM-DD') || '' })}
                slotProps={{ textField: { fullWidth: true } }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <DatePicker
                label="Period End"
                value={dayjs(formData.period_end)}
                onChange={(date) => setFormData({ ...formData, period_end: date?.format('YYYY-MM-DD') || '' })}
                slotProps={{ textField: { fullWidth: true } }}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Shop (Optional)</InputLabel>
                <Select
                  value={formData.shop_id || ''}
                  onChange={(e) => setFormData({ ...formData, shop_id: e.target.value as number })}
                  label="Shop (Optional)"
                >
                  <MenuItem value="">All Shops</MenuItem>
                  <MenuItem value={1}>Main Warehouse</MenuItem>
                  <MenuItem value={2}>Downtown Store</MenuItem>
                  <MenuItem value={3}>Mall Branch</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.include_inactive}
                    onChange={(e) => setFormData({ ...formData, include_inactive: e.target.checked })}
                  />
                }
                label="Include inactive employees"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProcessOpen(false)}>Cancel</Button>
          <Button onClick={handleProcessPayroll} variant="contained">
            Process Payroll
          </Button>
        </DialogActions>
      </Dialog>

      {/* Process Payment Dialog */}
      <Dialog open={paymentOpen} onClose={() => setPaymentOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Process Payment</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Payment Method</InputLabel>
                <Select
                  value={paymentData.payment_method}
                  onChange={(e) => setPaymentData({ ...paymentData, payment_method: e.target.value })}
                  label="Payment Method"
                >
                  <MenuItem value="bank_transfer">Bank Transfer</MenuItem>
                  <MenuItem value="cash">Cash</MenuItem>
                  <MenuItem value="check">Check</MenuItem>
                  <MenuItem value="payroll_system">Payroll System</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Payment Reference"
                value={paymentData.payment_reference}
                onChange={(e) => setPaymentData({ ...paymentData, payment_reference: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <DatePicker
                label="Payment Date"
                value={dayjs(paymentData.payment_date)}
                onChange={(date) => setPaymentData({ ...paymentData, payment_date: date?.format('YYYY-MM-DD') || '' })}
                slotProps={{ textField: { fullWidth: true } }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={3}
                value={paymentData.notes}
                onChange={(e) => setPaymentData({ ...paymentData, notes: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPaymentOpen(false)}>Cancel</Button>
          <Button onClick={handleProcessPayment} variant="contained">
            Process Payment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Payroll;
