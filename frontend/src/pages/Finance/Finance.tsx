import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
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
  Alert,
  Divider,
  useTheme,
  useMediaQuery,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  AttachMoney,
  Assessment,
  Download,
  Refresh,
  FilterList,
  DateRange,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { api } from '../../services/api';
import PrintableReport from '../../components/PrintableReport/PrintableReport';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';

const Finance: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [tabValue, setTabValue] = useState(0);
  const [dateRange, setDateRange] = useState({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    endDate: new Date(),
  });
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  const [selectedShop, setSelectedShop] = useState<number | null>(null);
  const [printDialogOpen, setPrintDialogOpen] = useState(false);
  const [printData, setPrintData] = useState<any>(null);
  const [printTitle, setPrintTitle] = useState('');

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ET', {
      style: 'currency',
      currency: 'ETB',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  // Fetch financial data
  const { data: plStatement, isLoading: plLoading } = useQuery(
    ['profitLossStatement', dateRange, selectedShop],
    async () => {
      const params = new URLSearchParams({
        start_date: dateRange.startDate.toISOString().split('T')[0],
        end_date: dateRange.endDate.toISOString().split('T')[0],
      });
      if (selectedShop) params.append('shop_id', selectedShop.toString());
      
      const response = await api.get(`/finance/profit-loss-statement?${params}`);
      return response.data;
    }
  );

  const { data: cashFlow, isLoading: cfLoading } = useQuery(
    ['cashFlowStatement', dateRange, selectedShop],
    async () => {
      const params = new URLSearchParams({
        start_date: dateRange.startDate.toISOString().split('T')[0],
        end_date: dateRange.endDate.toISOString().split('T')[0],
      });
      if (selectedShop) params.append('shop_id', selectedShop.toString());
      
      const response = await api.get(`/finance/cash-flow-statement?${params}`);
      return response.data;
    }
  );

  const { data: balanceSheet, isLoading: bsLoading } = useQuery(
    ['balanceSheet', selectedShop],
    async () => {
      const params = new URLSearchParams();
      if (selectedShop) params.append('shop_id', selectedShop.toString());
      
      const response = await api.get(`/finance/balance-sheet?${params}`);
      return response.data;
    }
  );

  const { data: ratios, isLoading: ratiosLoading } = useQuery(
    ['financialRatios', dateRange, selectedShop],
    async () => {
      const params = new URLSearchParams({
        start_date: dateRange.startDate.toISOString().split('T')[0],
        end_date: dateRange.endDate.toISOString().split('T')[0],
      });
      if (selectedShop) params.append('shop_id', selectedShop.toString());
      
      const response = await api.get(`/finance/financial-ratios?${params}`);
      return response.data;
    }
  );

  const { data: shops } = useQuery('shops', async () => {
    const response = await api.get('/shops/');
    return response.data;
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleDateRangeChange = (field: 'startDate' | 'endDate', value: Date | null) => {
    if (value) {
      setDateRange(prev => ({ ...prev, [field]: value }));
    }
  };

  const handleExport = () => {
    // TODO: Implement export functionality
    console.log('Exporting financial reports...');
  };

  const handlePrintReport = (type: string, data: any, title: string) => {
    setPrintData(data);
    setPrintTitle(title);
    setPrintDialogOpen(true);
  };

  if (plLoading || cfLoading || bsLoading || ratiosLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading financial data...</Typography>
      </Box>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" gutterBottom>
            Financial Reporting
          </Typography>
          <Box display="flex" gap={2}>
            <Tooltip title="Filter Reports">
              <IconButton onClick={() => setFilterDialogOpen(true)}>
                <FilterList />
              </IconButton>
            </Tooltip>
            <Tooltip title="Refresh Data">
              <IconButton>
                <Refresh />
              </IconButton>
            </Tooltip>
            <Button
              variant="outlined"
              startIcon={<Assessment />}
              onClick={() => handlePrintReport('financial', plStatement, 'Profit & Loss Statement')}
            >
              Print P&L
            </Button>
            <Button
              variant="contained"
              startIcon={<Download />}
              onClick={handleExport}
            >
              Export
            </Button>
          </Box>
        </Box>

        {/* Key Metrics Cards */}
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <TrendingUp color="success" sx={{ mr: 1 }} />
                  <Typography color="textSecondary" variant="body2">
                    Total Revenue
                  </Typography>
                </Box>
                <Typography variant="h5" color="success.main" fontWeight="bold">
                  {formatCurrency(plStatement?.revenue?.total || 0)}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {formatCurrency(plStatement?.revenue?.cash_sales || 0)} cash
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
                    Total Costs
                  </Typography>
                </Box>
                <Typography variant="h5" color="error.main" fontWeight="bold">
                  {formatCurrency(plStatement?.costs?.total || 0)}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  COGS: {formatCurrency(plStatement?.costs?.cogs || 0)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <AttachMoney color="primary" sx={{ mr: 1 }} />
                  <Typography color="textSecondary" variant="body2">
                    Net Profit
                  </Typography>
                </Box>
                <Typography variant="h5" color="primary.main" fontWeight="bold">
                  {formatCurrency(plStatement?.net_profit || 0)}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Margin: {plStatement?.net_profit_margin?.toFixed(1) || 0}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <AccountBalance color="info" sx={{ mr: 1 }} />
                  <Typography color="textSecondary" variant="body2">
                    Cash Flow
                  </Typography>
                </Box>
                <Typography variant="h5" color="info.main" fontWeight="bold">
                  {formatCurrency(cashFlow?.net_cash_flow || 0)}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  Operating: {formatCurrency(cashFlow?.operating_cash_flow || 0)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Tabs for different reports */}
        <Card>
          <Tabs value={tabValue} onChange={handleTabChange} variant="fullWidth">
            <Tab label="Profit & Loss" icon={<Assessment />} />
            <Tab label="Cash Flow" icon={<TrendingUp />} />
            <Tab label="Balance Sheet" icon={<AccountBalance />} />
            <Tab label="Financial Ratios" icon={<TrendingDown />} />
          </Tabs>

          <Box p={3}>
            {tabValue === 0 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Profit & Loss Statement
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                {/* Revenue Section */}
                <Box mb={3}>
                  <Typography variant="subtitle1" color="success.main" gutterBottom>
                    REVENUE
                  </Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableBody>
                        <TableRow>
                          <TableCell>Cash Sales</TableCell>
                          <TableCell align="right">
                            {formatCurrency(plStatement?.revenue?.cash_sales || 0)}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Bank Transfer Sales</TableCell>
                          <TableCell align="right">
                            {formatCurrency(plStatement?.revenue?.bank_transfer_sales || 0)}
                          </TableCell>
                        </TableRow>
                        <TableRow sx={{ backgroundColor: 'success.light', '& .MuiTableCell-root': { fontWeight: 'bold' } }}>
                          <TableCell>Total Revenue</TableCell>
                          <TableCell align="right">
                            {formatCurrency(plStatement?.revenue?.total || 0)}
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>

                {/* Costs Section */}
                <Box mb={3}>
                  <Typography variant="subtitle1" color="error.main" gutterBottom>
                    COSTS
                  </Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableBody>
                        <TableRow>
                          <TableCell>Cost of Goods Sold</TableCell>
                          <TableCell align="right">
                            {formatCurrency(plStatement?.costs?.cogs || 0)}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell>Operating Expenses</TableCell>
                          <TableCell align="right">
                            {formatCurrency(plStatement?.costs?.operating_expenses || 0)}
                          </TableCell>
                        </TableRow>
                        <TableRow sx={{ backgroundColor: 'error.light', '& .MuiTableCell-root': { fontWeight: 'bold' } }}>
                          <TableCell>Total Costs</TableCell>
                          <TableCell align="right">
                            {formatCurrency(plStatement?.costs?.total || 0)}
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>

                {/* Net Profit */}
                <Box>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableBody>
                        <TableRow sx={{ backgroundColor: 'primary.light', '& .MuiTableCell-root': { fontWeight: 'bold', fontSize: '1.1rem' } }}>
                          <TableCell>Net Profit</TableCell>
                          <TableCell align="right">
                            {formatCurrency(plStatement?.net_profit || 0)}
                          </TableCell>
                        </TableRow>
                        <TableRow sx={{ backgroundColor: 'primary.light' }}>
                          <TableCell>Net Profit Margin</TableCell>
                          <TableCell align="right">
                            {plStatement?.net_profit_margin?.toFixed(2) || 0}%
                          </TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              </Box>
            )}

            {tabValue === 1 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Cash Flow Statement
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Category</TableCell>
                        <TableCell align="right">Amount</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell><strong>Operating Cash Flow</strong></TableCell>
                        <TableCell align="right">
                          {formatCurrency(cashFlow?.operating_cash_flow || 0)}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Cash from Sales</TableCell>
                        <TableCell align="right">
                          {formatCurrency(cashFlow?.cash_from_sales || 0)}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Cash Paid for Purchases</TableCell>
                        <TableCell align="right">
                          {formatCurrency(cashFlow?.cash_paid_purchases || 0)}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Investing Cash Flow</strong></TableCell>
                        <TableCell align="right">
                          {formatCurrency(cashFlow?.investing_cash_flow || 0)}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell><strong>Financing Cash Flow</strong></TableCell>
                        <TableCell align="right">
                          {formatCurrency(cashFlow?.financing_cash_flow || 0)}
                        </TableCell>
                      </TableRow>
                      <TableRow sx={{ backgroundColor: 'primary.light', '& .MuiTableCell-root': { fontWeight: 'bold' } }}>
                        <TableCell><strong>Net Cash Flow</strong></TableCell>
                        <TableCell align="right">
                          {formatCurrency(cashFlow?.net_cash_flow || 0)}
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}

            {tabValue === 2 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Balance Sheet
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" color="success.main" gutterBottom>
                      ASSETS
                    </Typography>
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableBody>
                          <TableRow>
                            <TableCell>Current Assets</TableCell>
                            <TableCell align="right">
                              {formatCurrency(balanceSheet?.assets?.current_assets?.total_current_assets || 0)}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell sx={{ pl: 4 }}>Inventory</TableCell>
                            <TableCell align="right">
                              {formatCurrency(balanceSheet?.assets?.current_assets?.inventory || 0)}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell sx={{ pl: 4 }}>Cash</TableCell>
                            <TableCell align="right">
                              {formatCurrency(balanceSheet?.assets?.current_assets?.cash || 0)}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell sx={{ pl: 4 }}>Bank Balance</TableCell>
                            <TableCell align="right">
                              {formatCurrency(balanceSheet?.assets?.current_assets?.bank_balance || 0)}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Fixed Assets</TableCell>
                            <TableCell align="right">
                              {formatCurrency(balanceSheet?.assets?.fixed_assets?.total_fixed_assets || 0)}
                            </TableCell>
                          </TableRow>
                          <TableRow sx={{ backgroundColor: 'success.light', '& .MuiTableCell-root': { fontWeight: 'bold' } }}>
                            <TableCell><strong>Total Assets</strong></TableCell>
                            <TableCell align="right">
                              {formatCurrency(balanceSheet?.assets?.total_assets || 0)}
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" color="error.main" gutterBottom>
                      LIABILITIES & EQUITY
                    </Typography>
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableBody>
                          <TableRow>
                            <TableCell>Liabilities</TableCell>
                            <TableCell align="right">
                              {formatCurrency(balanceSheet?.liabilities?.total_liabilities || 0)}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell sx={{ pl: 4 }}>Accounts Payable</TableCell>
                            <TableCell align="right">
                              {formatCurrency(balanceSheet?.liabilities?.accounts_payable || 0)}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Owner's Equity</TableCell>
                            <TableCell align="right">
                              {formatCurrency(balanceSheet?.equity?.owners_equity || 0)}
                            </TableCell>
                          </TableRow>
                          <TableRow sx={{ backgroundColor: 'error.light', '& .MuiTableCell-root': { fontWeight: 'bold' } }}>
                            <TableCell><strong>Total Liabilities + Equity</strong></TableCell>
                            <TableCell align="right">
                              {formatCurrency((balanceSheet?.liabilities?.total_liabilities || 0) + (balanceSheet?.equity?.owners_equity || 0))}
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>
                </Grid>
              </Box>
            )}

            {tabValue === 3 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Financial Ratios
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" color="primary.main" gutterBottom>
                      PROFITABILITY RATIOS
                    </Typography>
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableBody>
                          <TableRow>
                            <TableCell>Gross Profit Margin</TableCell>
                            <TableCell align="right">
                              {ratios?.gross_profit_margin?.toFixed(2) || 0}%
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Net Profit Margin</TableCell>
                            <TableCell align="right">
                              {ratios?.net_profit_margin?.toFixed(2) || 0}%
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Return on Assets</TableCell>
                            <TableCell align="right">
                              {ratios?.return_on_assets?.toFixed(2) || 0}%
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle1" color="info.main" gutterBottom>
                      LIQUIDITY RATIOS
                    </Typography>
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableBody>
                          <TableRow>
                            <TableCell>Current Ratio</TableCell>
                            <TableCell align="right">
                              {ratios?.current_ratio?.toFixed(2) || 0}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Quick Ratio</TableCell>
                            <TableCell align="right">
                              {ratios?.quick_ratio?.toFixed(2) || 0}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Cash Ratio</TableCell>
                            <TableCell align="right">
                              {ratios?.cash_ratio?.toFixed(2) || 0}
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Grid>
                </Grid>
              </Box>
            )}
          </Box>
        </Card>

        {/* Filter Dialog */}
        <Dialog open={filterDialogOpen} onClose={() => setFilterDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Filter Reports</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <DatePicker
                  label="Start Date"
                  value={dateRange.startDate}
                  onChange={(value) => handleDateRangeChange('startDate', value)}
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <DatePicker
                  label="End Date"
                  value={dateRange.endDate}
                  onChange={(value) => handleDateRangeChange('endDate', value)}
                  slotProps={{ textField: { fullWidth: true } }}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Shop</InputLabel>
                  <Select
                    value={selectedShop || ''}
                    onChange={(e) => setSelectedShop(e.target.value ? Number(e.target.value) : null)}
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
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setFilterDialogOpen(false)}>Cancel</Button>
            <Button variant="contained" onClick={() => setFilterDialogOpen(false)}>
              Apply Filters
            </Button>
          </DialogActions>
        </Dialog>

        {/* Printable Report Dialog */}
        <PrintableReport
          open={printDialogOpen}
          onClose={() => setPrintDialogOpen(false)}
          title={printTitle}
          data={printData}
          type="financial"
        />
      </Box>
    </LocalizationProvider>
  );
};

export default Finance;