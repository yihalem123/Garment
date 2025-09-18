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
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Person,
  AttachMoney,
  Business,
  Phone,
  Email,
  LocationOn,
  TrendingUp,
  Work,
  People,
  AccountBalance,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { api } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import toast from 'react-hot-toast';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs from 'dayjs';

interface Employee {
  id: number;
  employee_id: string;
  full_name: string;
  email: string;
  position: string;
  department: string;
  employment_status: string;
  base_salary: number;
  shop_name?: string;
  manager_name?: string;
  hire_date: string;
}

interface EmployeeFormData {
  employee_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  address: string;
  position: string;
  department: string;
  base_salary: number;
  hourly_rate?: number;
  overtime_rate?: number;
  commission_rate?: number;
  work_hours_per_week: number;
  shop_id?: number;
  manager_id?: number;
  hire_date: string;
}

const Employees: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [formData, setFormData] = useState<EmployeeFormData>({
    employee_id: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address: '',
    position: '',
    department: '',
    base_salary: 0,
    hourly_rate: 0,
    overtime_rate: 1.5,
    commission_rate: 0,
    work_hours_per_week: 40,
    shop_id: undefined,
    manager_id: undefined,
    hire_date: dayjs().format('YYYY-MM-DD'),
  });

  const queryClient = useQueryClient();
  const { user } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const { data: employees, isLoading } = useQuery(
    'employees',
    async () => {
      try {
        const response = await api.get('/employees/');
        return response.data;
      } catch (error) {
        console.warn('API not available, using mock data:', error);
        return [
          {
            id: 1,
            employee_id: "EMP001",
            full_name: "John Doe",
            email: "john.doe@garment.com",
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

  const { data: employeeStats } = useQuery(
    'employeeStats',
    async () => {
      try {
        const response = await api.get('/employees/statistics/summary');
        return response.data;
      } catch (error) {
        return {
          total_employees: 8,
          by_department: [
            { department: "Retail", count: 4 },
            { department: "Operations", count: 2 },
            { department: "Customer Service", count: 1 },
            { department: "Marketing", count: 1 }
          ],
          by_status: [
            { status: "active", count: 8 }
          ],
          salary_statistics: {
            total_monthly_salary: 28300,
            average_salary: 3537.5,
            min_salary: 2800,
            max_salary: 4500
          }
        };
      }
    }
  );

  const createMutation = useMutation(
    async (data: EmployeeFormData) => {
      const response = await api.post('/employees/', data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('employees');
        queryClient.invalidateQueries('employeeStats');
        toast.success('Employee created successfully!');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to create employee');
      }
    }
  );

  const updateMutation = useMutation(
    async ({ id, data }: { id: number; data: Partial<EmployeeFormData> }) => {
      const response = await api.put(`/employees/${id}`, data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('employees');
        queryClient.invalidateQueries('employeeStats');
        toast.success('Employee updated successfully!');
        handleClose();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update employee');
      }
    }
  );

  const deleteMutation = useMutation(
    async (id: number) => {
      await api.delete(`/employees/${id}`);
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('employees');
        queryClient.invalidateQueries('employeeStats');
        toast.success('Employee deleted successfully!');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to delete employee');
      }
    }
  );

  const handleOpen = () => {
    setFormData({
      employee_id: '',
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      address: '',
      position: '',
      department: '',
      base_salary: 0,
      hourly_rate: 0,
      overtime_rate: 1.5,
      commission_rate: 0,
      work_hours_per_week: 40,
      shop_id: undefined,
      manager_id: undefined,
      hire_date: dayjs().format('YYYY-MM-DD'),
    });
    setSelectedEmployee(null);
    setOpen(true);
  };

  const handleEdit = (employee: Employee) => {
    setSelectedEmployee(employee);
    setFormData({
      employee_id: employee.employee_id,
      first_name: employee.full_name.split(' ')[0],
      last_name: employee.full_name.split(' ').slice(1).join(' '),
      email: employee.email,
      phone: '',
      address: '',
      position: employee.position,
      department: employee.department,
      base_salary: employee.base_salary,
      hourly_rate: 0,
      overtime_rate: 1.5,
      commission_rate: 0,
      work_hours_per_week: 40,
      shop_id: undefined,
      manager_id: undefined,
      hire_date: employee.hire_date,
    });
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setSelectedEmployee(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedEmployee) {
      updateMutation.mutate({ id: selectedEmployee.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleDelete = (employee: Employee) => {
    if (window.confirm(`Are you sure you want to delete ${employee.full_name}?`)) {
      deleteMutation.mutate(employee.id);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-ET', {
      style: 'currency',
      currency: 'ETB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'error';
      case 'on_leave': return 'warning';
      case 'terminated': return 'error';
      default: return 'default';
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'employee_id',
      headerName: 'Employee ID',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="bold" color="primary">
          {params.value}
        </Typography>
      )
    },
    {
      field: 'full_name',
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
      field: 'position',
      headerName: 'Position',
      width: 150,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          color="secondary"
          variant="outlined"
        />
      )
    },
    {
      field: 'department',
      headerName: 'Department',
      width: 120,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value}
        </Typography>
      )
    },
    {
      field: 'base_salary',
      headerName: 'Salary',
      width: 120,
      type: 'number',
      renderCell: (params) => (
        <Typography variant="body2" fontWeight="bold" color="success.main">
          {formatCurrency(params.value)}
        </Typography>
      )
    },
    {
      field: 'employment_status',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value}
          size="small"
          color={getStatusColor(params.value) as any}
          variant="filled"
        />
      )
    },
    {
      field: 'shop_name',
      headerName: 'Shop',
      width: 150,
      renderCell: (params) => (
        <Typography variant="body2">
          {params.value || 'Unassigned'}
        </Typography>
      )
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      sortable: false,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Edit Employee">
            <IconButton size="small" onClick={() => handleEdit(params.row)}>
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete Employee">
            <IconButton size="small" onClick={() => handleDelete(params.row)} color="error">
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      )
    }
  ];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Employee Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpen}
        >
          Add Employee
        </Button>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <People sx={{ mr: 1 }} />
                <Typography variant="h6">Total Employees</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold">
                {employeeStats?.total_employees || 0}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Active employees
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #2196F3 0%, #1976D2 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AttachMoney sx={{ mr: 1 }} />
                <Typography variant="h6">Total Monthly Salary</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold">
                {formatCurrency(employeeStats?.salary_statistics?.total_monthly_salary || 0)}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Monthly payroll
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #FF9800 0%, #F57C00 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp sx={{ mr: 1 }} />
                <Typography variant="h6">Average Salary</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold">
                {formatCurrency(employeeStats?.salary_statistics?.average_salary || 0)}
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
                <Work sx={{ mr: 1 }} />
                <Typography variant="h6">Departments</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold">
                {employeeStats?.by_department?.length || 0}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Active departments
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="All Employees" />
          <Tab label="By Department" />
          <Tab label="Salary Analysis" />
        </Tabs>
      </Box>

      {/* Employee Table */}
      {tabValue === 0 && (
        <Box sx={{ height: 500, width: '100%' }}>
          <DataGrid
            rows={employees || []}
            columns={columns}
            loading={isLoading}
            pageSizeOptions={[5, 10, 25]}
            disableRowSelectionOnClick
            sx={{
              '& .MuiDataGrid-row:hover': {
                backgroundColor: 'rgba(25, 118, 210, 0.04)',
              },
            }}
          />
        </Box>
      )}

      {/* Department Analysis */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          {employeeStats?.by_department?.map((dept: any, index: number) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {dept.department}
                  </Typography>
                  <Typography variant="h3" color="primary" fontWeight="bold">
                    {dept.count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    employees
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Salary Analysis */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Salary Range
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2">Minimum:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {formatCurrency(employeeStats?.salary_statistics?.min_salary || 0)}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body2">Maximum:</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {formatCurrency(employeeStats?.salary_statistics?.max_salary || 0)}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="body2">Average:</Typography>
                  <Typography variant="body2" fontWeight="bold" color="primary">
                    {formatCurrency(employeeStats?.salary_statistics?.average_salary || 0)}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Monthly Payroll Summary
                </Typography>
                <Typography variant="h4" color="success.main" fontWeight="bold">
                  {formatCurrency(employeeStats?.salary_statistics?.total_monthly_salary || 0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total monthly salary cost
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Employee Form Dialog */}
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedEmployee ? 'Edit Employee' : 'Add New Employee'}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Employee ID"
                  value={formData.employee_id}
                  onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="First Name"
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Last Name"
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Position"
                  value={formData.position}
                  onChange={(e) => setFormData({ ...formData, position: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Department"
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Base Salary"
                  type="number"
                  value={formData.base_salary}
                  onChange={(e) => setFormData({ ...formData, base_salary: parseFloat(e.target.value) || 0 })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Address"
                  multiline
                  rows={2}
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button type="submit" variant="contained">
              {selectedEmployee ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default Employees;
