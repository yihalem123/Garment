import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import { useAuth } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import Login from './pages/Auth/Login';
import Dashboard from './pages/Dashboard/Dashboard';
import Products from './pages/Products/Products';
import RawMaterials from './pages/RawMaterials/RawMaterials';
import Inventory from './pages/Inventory/Inventory';
import Purchases from './pages/Purchases/Purchases';
import Production from './pages/Production/Production';
import Transfers from './pages/Transfers/Transfers';
import Sales from './pages/Sales/Sales';
import Returns from './pages/Returns/Returns';
import Analytics from './pages/Analytics/Analytics';
import BusinessIntelligence from './pages/BusinessIntelligence/BusinessIntelligence';
import Finance from './pages/Finance/Finance';
import HR from './pages/HR/HR';
import Shops from './pages/Shops/Shops';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <Box sx={{ height: '100vh' }}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </Box>
    );
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        <Route path="/products" element={
          <ProtectedRoute>
            <Products />
          </ProtectedRoute>
        } />
        <Route path="/raw-materials" element={
          <ProtectedRoute>
            <RawMaterials />
          </ProtectedRoute>
        } />
        <Route path="/inventory" element={
          <ProtectedRoute>
            <Inventory />
          </ProtectedRoute>
        } />
        <Route path="/purchases" element={
          <ProtectedRoute>
            <Purchases />
          </ProtectedRoute>
        } />
        <Route path="/production" element={
          <ProtectedRoute>
            <Production />
          </ProtectedRoute>
        } />
        <Route path="/transfers" element={
          <ProtectedRoute>
            <Transfers />
          </ProtectedRoute>
        } />
        <Route path="/sales" element={
          <ProtectedRoute>
            <Sales />
          </ProtectedRoute>
        } />
        <Route path="/returns" element={
          <ProtectedRoute>
            <Returns />
          </ProtectedRoute>
        } />
        <Route path="/analytics" element={
          <ProtectedRoute>
            <Analytics />
          </ProtectedRoute>
        } />
        <Route path="/business-intelligence" element={
          <ProtectedRoute>
            <BusinessIntelligence />
          </ProtectedRoute>
        } />
        <Route path="/finance" element={
          <ProtectedRoute>
            <Finance />
          </ProtectedRoute>
        } />
        <Route path="/hr" element={
          <ProtectedRoute>
            <HR />
          </ProtectedRoute>
        } />
        <Route path="/shops" element={
          <ProtectedRoute>
            <Shops />
          </ProtectedRoute>
        } />
        <Route path="/login" element={<Navigate to="/dashboard" />} />
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Layout>
  );
};

export default App;

