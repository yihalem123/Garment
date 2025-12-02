import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import { Print, Close } from '@mui/icons-material';

interface PrintableReportProps {
  open: boolean;
  onClose: () => void;
  title: string;
  data: any;
  type: 'financial' | 'payroll' | 'sales';
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-ET', {
    style: 'currency',
    currency: 'ETB',
    minimumFractionDigits: 2,
  }).format(amount);
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-ET', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

const PrintableReport: React.FC<PrintableReportProps> = ({ 
  open, 
  onClose, 
  title, 
  data, 
  type 
}) => {
  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      let reportContent = '';

      if (type === 'financial') {
        reportContent = generateFinancialReportHTML(title, data);
      } else if (type === 'payroll') {
        reportContent = generatePayrollReportHTML(title, data);
      } else if (type === 'sales') {
        reportContent = generateSalesReportHTML(title, data);
      }

      printWindow.document.write(reportContent);
      printWindow.document.close();
      printWindow.focus();
      printWindow.print();
    }
  };

  const generateFinancialReportHTML = (title: string, data: any) => {
    if (!data) {
      return `
        <!DOCTYPE html>
        <html>
        <head>
          <title>${title}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .no-data { text-align: center; color: #666; padding: 40px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>${title}</h1>
            <p>Generated on: ${new Date().toLocaleString('en-ET')}</p>
          </div>
          <div class="no-data">
            <p>No financial data available</p>
          </div>
        </body>
        </html>
      `;
    }

    return `
      <!DOCTYPE html>
      <html>
      <head>
        <title>${title}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .header { text-align: center; margin-bottom: 30px; }
          .section { margin-bottom: 25px; }
          .section-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #1976d2; }
          table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
          th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
          th { background-color: #f5f5f5; font-weight: bold; }
          .total-row { font-weight: bold; background-color: #e3f2fd; }
          .footer { margin-top: 30px; text-align: center; font-size: 12px; color: #666; }
          @media print { body { margin: 0; } }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>${title}</h1>
          <p>Period: ${data.period?.start_date} to ${data.period?.end_date}</p>
          <p>Generated on: ${new Date().toLocaleString('en-ET')}</p>
        </div>
        
        <div class="section">
          <div class="section-title">Revenue</div>
          <table>
            <tr><td>Total Revenue</td><td>${formatCurrency(data.revenue?.total_revenue || 0)}</td></tr>
            ${data.revenue?.by_payment_method?.map((payment: any) => 
              `<tr><td>${payment.payment_method} Revenue</td><td>${formatCurrency(payment.amount)}</td></tr>`
            ).join('') || ''}
          </table>
        </div>
        
        <div class="section">
          <div class="section-title">Cost of Goods Sold</div>
          <table>
            <tr><td>Total COGS</td><td>${formatCurrency(data.cost_of_goods_sold?.total_cogs || 0)}</td></tr>
            <tr class="total-row"><td>Gross Profit</td><td>${formatCurrency(data.cost_of_goods_sold?.gross_profit || 0)}</td></tr>
            <tr><td>Gross Profit Margin</td><td>${(data.cost_of_goods_sold?.gross_profit_margin || 0).toFixed(2)}%</td></tr>
          </table>
        </div>
        
        <div class="section">
          <div class="section-title">Operating Expenses</div>
          <table>
            <tr><td>Raw Material Purchases</td><td>${formatCurrency(data.operating_expenses?.raw_material_purchases || 0)}</td></tr>
            <tr><td>Labor Costs</td><td>${formatCurrency(data.operating_expenses?.labor_costs || 0)}</td></tr>
            <tr><td>Overhead Costs</td><td>${formatCurrency(data.operating_expenses?.overhead_costs || 0)}</td></tr>
            <tr><td>Salary Costs</td><td>${formatCurrency(data.operating_expenses?.salary_costs || 0)}</td></tr>
            <tr class="total-row"><td>Total Operating Expenses</td><td>${formatCurrency(data.operating_expenses?.total_operating_expenses || 0)}</td></tr>
          </table>
        </div>
        
        <div class="section">
          <div class="section-title">Net Profit</div>
          <table>
            <tr class="total-row"><td>Net Profit</td><td>${formatCurrency(data.net_profit?.net_profit || 0)}</td></tr>
            <tr><td>Net Profit Margin</td><td>${(data.net_profit?.net_profit_margin || 0).toFixed(2)}%</td></tr>
          </table>
        </div>
        
        <div class="footer">
          <p>This report was generated by Garment Business Management System</p>
        </div>
      </body>
      </html>
    `;
  };

  const generatePayrollReportHTML = (title: string, data: any) => {
    if (!data) {
      return `
        <!DOCTYPE html>
        <html>
        <head>
          <title>${title}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .no-data { text-align: center; color: #666; padding: 40px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>${title}</h1>
            <p>Generated on: ${new Date().toLocaleString('en-ET')}</p>
          </div>
          <div class="no-data">
            <p>No payroll data available</p>
          </div>
        </body>
        </html>
      `;
    }

    return `
      <!DOCTYPE html>
      <html>
      <head>
        <title>${title}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .header { text-align: center; margin-bottom: 30px; }
          .section { margin-bottom: 25px; }
          .section-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #1976d2; }
          table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
          th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
          th { background-color: #f5f5f5; font-weight: bold; }
          .total-row { font-weight: bold; background-color: #e3f2fd; }
          .footer { margin-top: 30px; text-align: center; font-size: 12px; color: #666; }
          @media print { body { margin: 0; } }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>${title}</h1>
          <p>Generated on: ${new Date().toLocaleString('en-ET')}</p>
        </div>
        
        <div class="section">
          <div class="section-title">Payroll Summary</div>
          <table>
            <tr><td>Total Employees</td><td>${data.total_employees || 0}</td></tr>
            <tr><td>Total Paid Amount</td><td>${formatCurrency(data.total_paid || 0)}</td></tr>
            <tr><td>Average Pay</td><td>${formatCurrency(data.average_pay || 0)}</td></tr>
            <tr><td>Records Count</td><td>${data.records_count || 0}</td></tr>
          </table>
        </div>
        
        ${data.records?.length > 0 ? `
          <div class="section">
            <div class="section-title">Payroll Records</div>
            <table>
              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Period</th>
                  <th>Gross Pay</th>
                  <th>Deductions</th>
                  <th>Net Pay</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                ${data.records.map((record: any) => `
                  <tr>
                    <td>${record.employee_name || 'N/A'}</td>
                    <td>${record.payroll_period_start} - ${record.payroll_period_end}</td>
                    <td>${formatCurrency(record.gross_pay || 0)}</td>
                    <td>${formatCurrency(record.total_deductions || 0)}</td>
                    <td>${formatCurrency(record.net_pay || 0)}</td>
                    <td>${record.status || 'N/A'}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        ` : ''}
        
        <div class="footer">
          <p>This report was generated by Garment Business Management System</p>
        </div>
      </body>
      </html>
    `;
  };

  const generateSalesReportHTML = (title: string, data: any) => {
    if (!data || !Array.isArray(data)) {
      return `
        <!DOCTYPE html>
        <html>
        <head>
          <title>${title}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .no-data { text-align: center; color: #666; padding: 40px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>${title}</h1>
            <p>Generated on: ${new Date().toLocaleString('en-ET')}</p>
          </div>
          <div class="no-data">
            <p>No sales data available</p>
          </div>
        </body>
        </html>
      `;
    }

    return `
      <!DOCTYPE html>
      <html>
      <head>
        <title>${title}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .header { text-align: center; margin-bottom: 30px; }
          .section { margin-bottom: 25px; }
          .section-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #1976d2; }
          table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
          th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
          th { background-color: #f5f5f5; font-weight: bold; }
          .total-row { font-weight: bold; background-color: #e3f2fd; }
          .footer { margin-top: 30px; text-align: center; font-size: 12px; color: #666; }
          @media print { body { margin: 0; } }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>${title}</h1>
          <p>Generated on: ${new Date().toLocaleString('en-ET')}</p>
        </div>
        
        <div class="section">
          <div class="section-title">Sales Summary</div>
          <table>
            <tr><td>Total Sales</td><td>${data.length || 0}</td></tr>
            <tr><td>Total Revenue</td><td>${formatCurrency(data.reduce((sum: number, sale: any) => sum + (sale.final_amount || 0), 0))}</td></tr>
          </table>
        </div>
        
        <div class="section">
          <div class="section-title">Sales Details</div>
          <table>
            <thead>
              <tr>
                <th>Sale Number</th>
                <th>Customer</th>
                <th>Date</th>
                <th>Amount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              ${data.map((sale: any) => `
                <tr>
                  <td>${sale.sale_number || 'N/A'}</td>
                  <td>${sale.customer_name || 'N/A'}</td>
                  <td>${sale.sale_date || 'N/A'}</td>
                  <td>${formatCurrency(sale.final_amount || 0)}</td>
                  <td>${sale.status || 'N/A'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
        
        <div class="footer">
          <p>This report was generated by Garment Business Management System</p>
        </div>
      </body>
      </html>
    `;
  };

  const renderFinancialReport = () => {
    if (!data) {
      return (
        <Box>
          <Typography variant="body1" color="textSecondary">
            No financial data available
          </Typography>
        </Box>
      );
    }

    return (
      <Box>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Revenue</Typography>
                <Typography variant="h4" color="primary">
                  {formatCurrency(data.revenue?.total_revenue || 0)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Gross Profit</Typography>
                <Typography variant="h4" color="success.main">
                  {formatCurrency(data.cost_of_goods_sold?.gross_profit || 0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Margin: {(data.cost_of_goods_sold?.gross_profit_margin || 0).toFixed(2)}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Net Profit</Typography>
                <Typography variant="h4" color={data.net_profit?.net_profit >= 0 ? "success.main" : "error.main"}>
                  {formatCurrency(data.net_profit?.net_profit || 0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Margin: {(data.net_profit?.net_profit_margin || 0).toFixed(2)}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const renderPayrollReport = () => {
    if (!data) {
      return (
        <Box>
          <Typography variant="body1" color="textSecondary">
            No payroll data available
          </Typography>
        </Box>
      );
    }

    return (
      <Box>
        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Total Employees</Typography>
                <Typography variant="h4" color="primary">
                  {data.total_employees || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Total Paid</Typography>
                <Typography variant="h4" color="success.main">
                  {formatCurrency(data.total_paid || 0)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Average Pay</Typography>
                <Typography variant="h4" color="info.main">
                  {formatCurrency(data.average_pay || 0)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Records</Typography>
                <Typography variant="h4" color="warning.main">
                  {data.records_count || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };

  const renderSalesReport = () => {
    if (!data) {
      return (
        <Box>
          <Typography variant="body1" color="textSecondary">
            No sales data available
          </Typography>
        </Box>
      );
    }

    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          Total Sales: {data.length || 0}
        </Typography>
        <Typography variant="h6" gutterBottom>
          Total Revenue: {formatCurrency(data.reduce((sum: number, sale: any) => sum + (sale.final_amount || 0), 0))}
        </Typography>
      </Box>
    );
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">{title}</Typography>
          <Box>
            <IconButton onClick={handlePrint} color="primary" size="small">
              <Print />
            </IconButton>
            <IconButton onClick={onClose} size="small">
              <Close />
            </IconButton>
          </Box>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Paper elevation={1} sx={{ p: 3 }}>
          {type === 'financial' && renderFinancialReport()}
          {type === 'payroll' && renderPayrollReport()}
          {type === 'sales' && renderSalesReport()}
        </Paper>
      </DialogContent>

      <DialogActions>
        <Button onClick={handlePrint} startIcon={<Print />} variant="contained">
          Print Report
        </Button>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default PrintableReport;

