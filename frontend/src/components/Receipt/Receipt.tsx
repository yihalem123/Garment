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
} from '@mui/material';
import { Print, Close } from '@mui/icons-material';

interface SaleLine {
  id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

interface Sale {
  id: number;
  sale_number: string;
  customer_name?: string;
  customer_phone?: string;
  total_amount: number;
  discount_amount: number;
  final_amount: number;
  sale_date: string;
  payment_method?: string;
  notes?: string;
  sale_lines: SaleLine[];
  shop?: {
    name: string;
    address?: string;
    phone?: string;
  };
}

interface ReceiptProps {
  open: boolean;
  onClose: () => void;
  sale: Sale | null;
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
    hour: '2-digit',
    minute: '2-digit',
  });
};

const Receipt: React.FC<ReceiptProps> = ({ open, onClose, sale }) => {
  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    if (printWindow && sale) {
      const receiptContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <title>Receipt - ${sale.sale_number}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 20px; }
            .shop-info { margin-bottom: 15px; }
            .sale-info { margin-bottom: 15px; }
            .customer-info { margin-bottom: 15px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f5f5f5; }
            .total-section { margin-top: 15px; }
            .footer { margin-top: 30px; text-align: center; font-size: 12px; }
            @media print { body { margin: 0; } }
          </style>
        </head>
        <body>
          <div class="header">
            <h2>${sale.shop?.name || 'Garment Store'}</h2>
            ${sale.shop?.address ? `<p>${sale.shop.address}</p>` : ''}
            ${sale.shop?.phone ? `<p>Tel: ${sale.shop.phone}</p>` : ''}
          </div>
          
          <div class="sale-info">
            <p><strong>Receipt #:</strong> ${sale.sale_number}</p>
            <p><strong>Date:</strong> ${formatDate(sale.sale_date)}</p>
          </div>
          
          ${sale.customer_name ? `
            <div class="customer-info">
              <p><strong>Customer:</strong> ${sale.customer_name}</p>
              ${sale.customer_phone ? `<p><strong>Phone:</strong> ${sale.customer_phone}</p>` : ''}
            </div>
          ` : ''}
          
          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              ${sale.sale_lines.map(line => `
                <tr>
                  <td>${line.product_name}</td>
                  <td>${line.quantity}</td>
                  <td>${formatCurrency(line.unit_price)}</td>
                  <td>${formatCurrency(line.total_price)}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
          
          <div class="total-section">
            <p><strong>Subtotal:</strong> ${formatCurrency(sale.total_amount)}</p>
            ${sale.discount_amount > 0 ? `<p><strong>Discount:</strong> -${formatCurrency(sale.discount_amount)}</p>` : ''}
            <p><strong>Total:</strong> ${formatCurrency(sale.final_amount)}</p>
            ${sale.payment_method ? `<p><strong>Payment:</strong> ${sale.payment_method.toUpperCase()}</p>` : ''}
          </div>
          
          ${sale.notes ? `<p><strong>Notes:</strong> ${sale.notes}</p>` : ''}
          
          <div class="footer">
            <p>Thank you for your business!</p>
            <p>Generated on ${new Date().toLocaleString('en-ET')}</p>
          </div>
        </body>
        </html>
      `;
      
      printWindow.document.write(receiptContent);
      printWindow.document.close();
      printWindow.focus();
      printWindow.print();
    }
  };

  if (!sale) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Receipt - {sale.sale_number}</Typography>
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
          {/* Header */}
          <Box textAlign="center" mb={3}>
            <Typography variant="h5" fontWeight="bold">
              {sale.shop?.name || 'Garment Store'}
            </Typography>
            {sale.shop?.address && (
              <Typography variant="body2" color="text.secondary">
                {sale.shop.address}
              </Typography>
            )}
            {sale.shop?.phone && (
              <Typography variant="body2" color="text.secondary">
                Tel: {sale.shop.phone}
              </Typography>
            )}
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Sale Info */}
          <Box mb={2}>
            <Typography variant="body2" color="text.secondary">
              <strong>Receipt #:</strong> {sale.sale_number}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>Date:</strong> {formatDate(sale.sale_date)}
            </Typography>
          </Box>

          {/* Customer Info */}
          {sale.customer_name && (
            <Box mb={2}>
              <Typography variant="body2">
                <strong>Customer:</strong> {sale.customer_name}
              </Typography>
              {sale.customer_phone && (
                <Typography variant="body2">
                  <strong>Phone:</strong> {sale.customer_phone}
                </Typography>
              )}
            </Box>
          )}

          <Divider sx={{ my: 2 }} />

          {/* Items Table */}
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell><strong>Item</strong></TableCell>
                  <TableCell align="right"><strong>Qty</strong></TableCell>
                  <TableCell align="right"><strong>Price</strong></TableCell>
                  <TableCell align="right"><strong>Total</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sale.sale_lines.map((line) => (
                  <TableRow key={line.id}>
                    <TableCell>{line.product_name}</TableCell>
                    <TableCell align="right">{line.quantity}</TableCell>
                    <TableCell align="right">{formatCurrency(line.unit_price)}</TableCell>
                    <TableCell align="right">{formatCurrency(line.total_price)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <Divider sx={{ my: 2 }} />

          {/* Totals */}
          <Box>
            <Box display="flex" justifyContent="space-between" mb={1}>
              <Typography variant="body2">Subtotal:</Typography>
              <Typography variant="body2">{formatCurrency(sale.total_amount)}</Typography>
            </Box>
            {sale.discount_amount > 0 && (
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2">Discount:</Typography>
                <Typography variant="body2" color="error">
                  -{formatCurrency(sale.discount_amount)}
                </Typography>
              </Box>
            )}
            <Box display="flex" justifyContent="space-between" mb={1}>
              <Typography variant="h6"><strong>Total:</strong></Typography>
              <Typography variant="h6"><strong>{formatCurrency(sale.final_amount)}</strong></Typography>
            </Box>
            {sale.payment_method && (
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2">Payment:</Typography>
                <Typography variant="body2">{sale.payment_method.toUpperCase()}</Typography>
              </Box>
            )}
          </Box>

          {sale.notes && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="body2">
                <strong>Notes:</strong> {sale.notes}
              </Typography>
            </>
          )}

          <Divider sx={{ my: 2 }} />

          {/* Footer */}
          <Box textAlign="center" mt={3}>
            <Typography variant="body2" color="text.secondary">
              Thank you for your business!
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Generated on {new Date().toLocaleString('en-ET')}
            </Typography>
          </Box>
        </Paper>
      </DialogContent>

      <DialogActions>
        <Button onClick={handlePrint} startIcon={<Print />} variant="contained">
          Print Receipt
        </Button>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default Receipt;

