import React, { useState } from 'react';
import {
  Box,
  Typography,
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
  Chip,
  Avatar,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
  Tabs,
  Tab,
  Alert,
} from '@mui/material';
import {
  Person,
  AttachMoney,
  Business,
  Phone,
  Email,
  LocationOn,
  TrendingUp,
  TrendingDown,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { api } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

interface Employee {
  id: number;
  employee_id: string;
  full_name: string;
  email: string;
  phone?: string;
  address?: string;
  position: string;
  department: string;
  employment_status: string;
  base_salary: number;
  shop_name?: string;
  manager_name?: string;
  hire_date: string;
}

interface MonthlyCosts {
  total_monthly_salary: number;
  employee_count: number;
  breakdown_by_department: Array<{
    department: string;
    total_cost: number;
  }>;
  breakdown_by_shop: Array<{
    shop_name: string;
    total_cost: number;
  }>;
  employee_costs: Array<{
    id: number;
    full_name: string;
    position: string;
    department: string;
    shop_name: string;
    monthly_salary: number;
    role: string;
  }>;
  average_salary: number;
  highest_paid?: {
    full_name: string;
    monthly_salary: number;
    position: string;
  };
  lowest_paid?: {
    full_name: string;
    monthly_salary: number;
    position: string;
  };
}

const HR: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);

  const { data: employees, isLoading: employeesLoading } = useQuery(
    'employees',
    async () => {
      try {
        const response = await api.get('/employees/');
        return response.data;
      } catch (error) {
        console.warn('API not available, using mock data:', error);
        // Mock data for development
        return [
          {
            id: 1,
            employee_id: "EMP001",
            full_name: "John Doe",
            email: "john.doe@garment.com",
            phone: "+1-555-0101",
            address: "123 Main St, City",
            position: "Store Manager",
            department: "Retail",
            employment_status: "active",
            base_salary: 4500,
            shop_name: "Main Warehouse",
            manager_name: null,
            hire_date: "2023-01-15"
          },
          {
            id: 2,
            employee_id: "EMP002",
            full_name: "Jane Smith",
            email: "jane.smith@garment.com",
            phone: "+1-555-0102",
            address: "456 Oak Ave, City",
            position: "Sales Associate",
            department: "Retail",
            employment_status: "active",
            base_salary: 3200,
            shop_name: "Main Warehouse",
            manager_name: "John Doe",
            hire_date: "2023-07-15"
          }
        ];
      }
    }
  );

  const { data: monthlyCosts, isLoading: costsLoading } = useQuery(
    'monthlyCosts',
    async () => {
      try {
        const response = await api.get('/hr/monthly-costs');
        return response.data;
      } catch (error) {
        console.warn('API not available, using mock data:', error);
        return {
          total_monthly_salary: 28300,
          employee_count: 8,
          breakdown_by_department: [
            { department: "Retail", total_cost: 15000 },
            { department: "Operations", total_cost: 3000 },
            { department: "Customer Service", total_cost: 3500 },
            { department: "Marketing", total_cost: 3100 },
            { department: "Management", total_cost: 3700 }
          ],
          breakdown_by_shop: [
            { shop_name: "Main Warehouse", total_cost: 15000 },
            { shop_name: "Downtown Store", total_cost: 13300 }
          ],
          average_salary: 3537.5,
          highest_paid: {
            full_name: "John Doe",
            monthly_salary: 4500,
            position: "Store Manager"
          },
          lowest_paid: {
            full_name: "Mike Johnson",
            monthly_salary: 2800,
            position: "Cashier"
          }
        };
      }
    }
  );

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const getRoleColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'error';
      case 'on_leave': return 'warning';
      case 'terminated': return 'error';
      default: return 'default';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ET', {
      style: 'currency',
      currency: 'ETB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (employeesLoading || costsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Human Resources
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Employees" />
          <Tab label="Monthly Costs" />
          <Tab label="Analytics" />
        </Tabs>
      </Box>

      {tabValue === 0 && (
        <Box>
          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
            Employee Directory
          </Typography>
          
          <TableContainer component={Paper} sx={{ boxShadow: 2 }}>
            <Table>
              <TableHead>
                <TableRow sx={{ backgroundColor: 'primary.main' }}>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Employee</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Position</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Department</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Salary</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Shop</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
                  {!isMobile && (
                    <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Contact</TableCell>
                  )}
                </TableRow>
              </TableHead>
              <TableBody>
                {employees && Array.isArray(employees) ? employees.map((employee: Employee) => (
                  <TableRow key={employee.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          {employee.full_name.charAt(0)}
                        </Avatar>
                        <Box>
                          <Typography variant="subtitle2" fontWeight="bold">
                            {employee.full_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {employee.email}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {employee.position || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={employee.department || 'N/A'}
                        size="small"
                        color="secondary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold" color="success.main">
                        {employee.base_salary ? formatCurrency(employee.base_salary) : 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {employee.shop_name || 'Unassigned'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={employee.employment_status}
                        size="small"
                        color={getRoleColor(employee.employment_status) as any}
                        variant="filled"
                      />
                    </TableCell>
                    {!isMobile && (
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          {employee.phone && (
                            <Tooltip title={employee.phone}>
                              <IconButton size="small">
                                <Phone fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                          <Tooltip title={employee.email}>
                            <IconButton size="small">
                              <Email fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          {employee.address && (
                            <Tooltip title={employee.address}>
                              <IconButton size="small">
                                <LocationOn fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                        </Box>
                      </TableCell>
                    )}
                  </TableRow>
                )) : null}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {tabValue === 1 && monthlyCosts && (
        <Box>
          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
            Monthly Salary Costs
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card sx={{ background: 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AttachMoney sx={{ mr: 1 }} />
                    <Typography variant="h6">Total Monthly Cost</Typography>
                  </Box>
                  <Typography variant="h3" fontWeight="bold">
                    {formatCurrency(monthlyCosts.total_monthly_salary)}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    {monthlyCosts.employee_count} employees
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ background: 'linear-gradient(135deg, #2196F3 0%, #1976D2 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <TrendingUp sx={{ mr: 1 }} />
                    <Typography variant="h6">Average Salary</Typography>
                  </Box>
                  <Typography variant="h3" fontWeight="bold">
                    {formatCurrency(monthlyCosts.average_salary)}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    per employee
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ background: 'linear-gradient(135deg, #FF9800 0%, #F57C00 100%)', color: 'white' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Person sx={{ mr: 1 }} />
                    <Typography variant="h6">Highest Paid</Typography>
                  </Box>
                  <Typography variant="h5" fontWeight="bold">
                    {monthlyCosts.highest_paid?.full_name}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    {monthlyCosts.highest_paid?.position} - {formatCurrency(monthlyCosts.highest_paid?.monthly_salary || 0)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Costs by Department
                  </Typography>
                  {monthlyCosts.breakdown_by_department.map((dept: { department: string; total_cost: number }, index: number) => (
                    <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">{dept.department}</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {formatCurrency(dept.total_cost)}
                      </Typography>
                    </Box>
                  ))}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Costs by Shop
                  </Typography>
                  {monthlyCosts.breakdown_by_shop.map((shop: { shop_name: string; total_cost: number }, index: number) => (
                    <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">{shop.shop_name}</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {formatCurrency(shop.total_cost)}
                      </Typography>
                    </Box>
                  ))}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {tabValue === 2 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            HR Analytics
          </Typography>
          <Alert severity="info">
            Advanced HR analytics and reporting features will be available soon.
          </Alert>
        </Box>
      )}
    </Box>
  );
};

export default HR;

