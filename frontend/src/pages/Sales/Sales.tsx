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
  IconButton,
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
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { api } from '../../services/api';
import toast from 'react-hot-toast';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
interface Sale {
  id: number;
  sale_number: string;
  shop_id: number;
  customer_name: string;
  customer_phone: string;
  total_amount: number;
  discount_amount: number;
  final_amount: number;
  status: string;
  sale_date: string;
  notes: string;
  created_at: string;
  sale_lines: SaleLine[];
  payments: Payment[];
}

interface SaleLine {
  product_id: number;
  quantity: number;
  unit_price: number;
  total_price: number;
}

interface Payment {
  amount: number;
  payment_method: string;
  payment_date: string;
  reference: string;
  notes: string;
}

const Sales: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [saleLines, setSaleLines] = useState<SaleLine[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [formData, setFormData] = useState({
    sale_number: '',
    shop_id: 1,
    customer_name: '',
    customer_phone: '',
    discount_amount: 0,
    sale_date: dayjs().format('YYYY-MM-DD'),
    notes: '',
  });

  const queryClient = useQueryClient();

  const { data: sales, isLoading } = useQuery(
    'sales',
    async () => {
      const response = await api.get('/sales/');
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

  const { data: shops } = useQuery(
    'shops',
    async () => {
      const response = await api.get('/shops/');
      return response.data;
    }
  );

  const createMutation = useMutation(
    async (data: any) => {
      const response = await api.post('/sales/', data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('sales');
        toast.success('Sale created successfully');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create sale');
      },
    }
  );

  const handleOpen = () => {
    setFormData({
      sale_number: `SALE-${Date.now()}`,
      shop_id: 1,
      customer_name: '',
      customer_phone: '',
      discount_amount: 0,
      sale_date: dayjs().format('YYYY-MM-DD'),
      notes: '',
    });
    setSaleLines([]);
    setPayments([]);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setSaleLines([]);
    setPayments([]);
  };

  const addSaleLine = () => {
    setSaleLines([...saleLines, {
      product_id: 1,
      quantity: 1,
      unit_price: 0,
      total_price: 0,
    }]);
  };

  const updateSaleLine = (index: number, field: keyof SaleLine, value: any) => {
    const updated = [...saleLines];
    updated[index] = { ...updated[index], [field]: value };
    if (field === 'quantity' || field === 'unit_price') {
      updated[index].total_price = updated[index].quantity * updated[index].unit_price;
    }
    setSaleLines(updated);
  };

  const removeSaleLine = (index: number) => {
    setSaleLines(saleLines.filter((_, i) => i !== index));
  };

  const addPayment = () => {
    setPayments([...payments, {
      amount: 0,
      payment_method: 'cash',
      payment_date: dayjs().format('YYYY-MM-DD'),
      reference: '',
      notes: '',
    }]);
  };

  const updatePayment = (index: number, field: keyof Payment, value: any) => {
    const updated = [...payments];
    updated[index] = { ...updated[index], [field]: value };
    setPayments(updated);
  };

  const removePayment = (index: number) => {
    setPayments(payments.filter((_, i) => i !== index));
  };

  const calculateTotal = () => {
    const subtotal = saleLines.reduce((sum, line) => sum + line.total_price, 0);
    return subtotal - formData.discount_amount;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const totalAmount = saleLines.reduce((sum, line) => sum + line.total_price, 0);
    const finalAmount = totalAmount - formData.discount_amount;

    const saleData = {
      ...formData,
      total_amount: totalAmount,
      final_amount: finalAmount,
      sale_lines: saleLines,
      payments: payments,
    };

    createMutation.mutate(saleData);
  };

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'sale_number', headerName: 'Sale Number', width: 150 },
    { field: 'customer_name', headerName: 'Customer', width: 200 },
    { field: 'total_amount', headerName: 'Total Amount', width: 120, type: 'number' },
    { field: 'final_amount', headerName: 'Final Amount', width: 120, type: 'number' },
    { field: 'status', headerName: 'Status', width: 100 },
    { field: 'sale_date', headerName: 'Sale Date', width: 120 },
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Sales</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpen}
        >
          New Sale
        </Button>
      </Box>

      <Box sx={{ height: 400, width: '100%' }}>
        <DataGrid
          rows={sales || []}
          columns={columns}
          loading={isLoading}
          pageSizeOptions={[5, 10, 25]}
          disableRowSelectionOnClick
        />
      </Box>

      <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
        <DialogTitle>Create New Sale</DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Sale Number"
                  value={formData.sale_number}
                  onChange={(e) => setFormData({ ...formData, sale_number: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Shop</InputLabel>
                  <Select
                    value={formData.shop_id}
                    onChange={(e) => setFormData({ ...formData, shop_id: e.target.value as number })}
                    label="Shop"
                  >
                    {shops?.map((shop: any) => (
                      <MenuItem key={shop.id} value={shop.id}>
                        {shop.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Customer Name"
                  value={formData.customer_name}
                  onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Customer Phone"
                  value={formData.customer_phone}
                  onChange={(e) => setFormData({ ...formData, customer_phone: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Discount Amount"
                  type="number"
                  value={formData.discount_amount}
                  onChange={(e) => setFormData({ ...formData, discount_amount: parseFloat(e.target.value) })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <LocalizationProvider dateAdapter={AdapterDayjs}>
                  <DatePicker
                    label="Sale Date"
                    value={dayjs(formData.sale_date)}
                    onChange={(newValue) => setFormData({ ...formData, sale_date: newValue?.format('YYYY-MM-DD') || '' })}
                    slotProps={{ textField: { fullWidth: true } }}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  multiline
                  rows={2}
                />
              </Grid>
            </Grid>

            {/* Sale Lines */}
            <Box sx={{ mt: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Sale Items</Typography>
                <Button startIcon={<AddIcon />} onClick={addSaleLine}>
                  Add Item
                </Button>
              </Box>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Product</TableCell>
                      <TableCell>Quantity</TableCell>
                      <TableCell>Unit Price</TableCell>
                      <TableCell>Total</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {saleLines.map((line, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <FormControl fullWidth size="small">
                            <Select
                              value={line.product_id}
                              onChange={(e) => updateSaleLine(index, 'product_id', e.target.value)}
                            >
                              {products?.map((product: any) => (
                                <MenuItem key={product.id} value={product.id}>
                                  {product.name}
                                </MenuItem>
                              ))}
                            </Select>
                          </FormControl>
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            type="number"
                            value={line.quantity}
                            onChange={(e) => updateSaleLine(index, 'quantity', parseInt(e.target.value))}
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            type="number"
                            value={line.unit_price}
                            onChange={(e) => updateSaleLine(index, 'unit_price', parseFloat(e.target.value))}
                          />
                        </TableCell>
                        <TableCell>{line.total_price}</TableCell>
                        <TableCell>
                          <IconButton onClick={() => removeSaleLine(index)}>
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>

            {/* Payments */}
            <Box sx={{ mt: 3 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Payments</Typography>
                <Button startIcon={<AddIcon />} onClick={addPayment}>
                  Add Payment
                </Button>
              </Box>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Amount</TableCell>
                      <TableCell>Method</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Reference</TableCell>
                      <TableCell>Notes</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {payments.map((payment, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <TextField
                            size="small"
                            type="number"
                            value={payment.amount}
                            onChange={(e) => updatePayment(index, 'amount', parseFloat(e.target.value))}
                          />
                        </TableCell>
                        <TableCell>
                          <FormControl fullWidth size="small">
                            <Select
                              value={payment.payment_method}
                              onChange={(e) => updatePayment(index, 'payment_method', e.target.value)}
                            >
                              <MenuItem value="cash">Cash</MenuItem>
                              <MenuItem value="bank_transfer">Bank Transfer</MenuItem>
                            </Select>
                          </FormControl>
                        </TableCell>
                        <TableCell>
                          <LocalizationProvider dateAdapter={AdapterDayjs}>
                            <DatePicker
                              value={dayjs(payment.payment_date)}
                              onChange={(newValue) => updatePayment(index, 'payment_date', newValue?.format('YYYY-MM-DD') || '')}
                              slotProps={{ textField: { size: 'small' } }}
                            />
                          </LocalizationProvider>
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            value={payment.reference}
                            onChange={(e) => updatePayment(index, 'reference', e.target.value)}
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            value={payment.notes}
                            onChange={(e) => updatePayment(index, 'notes', e.target.value)}
                          />
                        </TableCell>
                        <TableCell>
                          <IconButton onClick={() => removePayment(index)}>
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>

            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6">
                  Total: {calculateTotal().toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button type="submit" variant="contained">
              Create Sale
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default Sales;
