import axios from 'axios';

export const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const endpoints = {
  // Auth
  login: '/auth/login',
  me: '/auth/users/me',
  
  // Products
  products: '/products/',
  rawMaterials: '/raw-materials/',
  
  // Inventory
  stocks: '/inventory/stocks',
  stockMovements: '/inventory/stock-movements',
  adjustStock: '/inventory/stocks/adjust',
  
  // Purchases
  purchases: '/purchases/',
  
  // Production
  production: '/production/',
  completeProduction: (id: number) => `/production/${id}/complete`,
  
  // Transfers
  transfers: '/transfers/',
  receiveTransfer: (id: number) => `/transfers/${id}/receive`,
  
  // Sales
  sales: '/sales/',
  
  // Returns
  returns: '/returns/',
  
  // Analytics
  dashboard: '/analytics/dashboard',
  profitLoss: '/analytics/profit-loss',
  
  // Business Intelligence
  kpis: '/business-intelligence/kpis',
  businessHealth: '/business-intelligence/business-health',
  
  // Finance
  profitLossStatement: '/finance/profit-loss-statement',
  
  // HR
  workforceSummary: '/hr/workforce-summary',
  
  // Shops
  shops: '/shops/',
};

