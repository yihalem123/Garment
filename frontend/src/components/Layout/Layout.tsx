import React, { useState } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  useTheme,
  useMediaQuery,
  Badge,
  Chip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Inventory,
  ShoppingCart,
  Factory,
  LocalShipping,
  PointOfSale,
  AssignmentReturn,
  Analytics,
  Psychology,
  AccountBalance,
  People,
  Store,
  Logout,
  Notifications,
  Settings,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const drawerWidth = 240;
const mobileDrawerWidth = 200;

interface LayoutProps {
  children: React.ReactNode;
}

const menuItems = [
  { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard', color: '#4CAF50' },
  { text: 'Products', icon: <Inventory />, path: '/products', color: '#2196F3' },
  { text: 'Raw Materials', icon: <Inventory />, path: '/raw-materials', color: '#FF9800' },
  { text: 'Inventory', icon: <Inventory />, path: '/inventory', color: '#9C27B0' },
  { text: 'Purchases', icon: <ShoppingCart />, path: '/purchases', color: '#F44336' },
  { text: 'Production', icon: <Factory />, path: '/production', color: '#607D8B' },
  { text: 'Transfers', icon: <LocalShipping />, path: '/transfers', color: '#795548' },
  { text: 'Sales', icon: <PointOfSale />, path: '/sales', color: '#4CAF50' },
  { text: 'Returns', icon: <AssignmentReturn />, path: '/returns', color: '#FF5722' },
  { text: 'Analytics', icon: <Analytics />, path: '/analytics', color: '#3F51B5' },
  { text: 'Business Intelligence', icon: <Psychology />, path: '/business-intelligence', color: '#E91E63' },
  { text: 'Finance', icon: <AccountBalance />, path: '/finance', color: '#00BCD4' },
  { text: 'HR', icon: <People />, path: '/hr', color: '#8BC34A' },
  { text: 'Shops', icon: <Store />, path: '/shops', color: '#FFC107' },
];

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleMenuClose();
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box
        sx={{
          p: 2,
          background: 'linear-gradient(135deg, #1565C0 0%, #1976D2 50%, #42A5F5 100%)',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'url("data:image/svg+xml,%3Csvg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="%23ffffff" fill-opacity="0.05"%3E%3Cpath d="M20 20c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10 10-4.5 10-10zm10 0c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10 10-4.5 10-10z"/%3E%3C/g%3E%3C/svg%3E")',
          },
        }}
      >
        <Avatar
          sx={{
            bgcolor: 'rgba(255,255,255,0.15)',
            width: 36,
            height: 36,
            fontSize: '1.1rem',
            fontWeight: 700,
            backdropFilter: 'blur(10px)',
            border: '2px solid rgba(255,255,255,0.2)',
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
          }}
        >
          GB
        </Avatar>
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 700, lineHeight: 1.2, mb: 0.2 }}>
            Garment Business
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.9, fontWeight: 500, fontSize: '0.7rem' }}>
            Management System
          </Typography>
        </Box>
      </Box>

      {/* Navigation */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List sx={{ px: 1, py: 1.5 }}>
          {menuItems.map((item, index) => {
            const isSelected = location.pathname === item.path;
            const isLastCoreItem = index === 3; // After Production
            return (
              <React.Fragment key={item.text}>
                <ListItem disablePadding sx={{ mb: 0.5 }}>
                <ListItemButton
                  selected={isSelected}
                  onClick={() => {
                    navigate(item.path);
                    if (isMobile) {
                      setMobileOpen(false);
                    }
                  }}
                  sx={{
                    borderRadius: 2,
                    mx: 0.5,
                    py: 1,
                    px: 1.5,
                    mb: 0.3,
                    minHeight: 40,
                    transition: 'all 0.2s ease-in-out',
                    '&.Mui-selected': {
                      backgroundColor: `${item.color}12`,
                      borderLeft: `3px solid ${item.color}`,
                      boxShadow: `0 2px 8px ${item.color}20`,
                      '&:hover': {
                        backgroundColor: `${item.color}18`,
                        transform: 'translateX(2px)',
                      },
                      '& .MuiListItemIcon-root': {
                        color: item.color,
                        transform: 'scale(1.05)',
                      },
                      '& .MuiListItemText-primary': {
                        color: item.color,
                        fontWeight: 600,
                        fontSize: '0.9rem',
                      },
                    },
                    '&:hover': {
                      backgroundColor: 'rgba(0,0,0,0.06)',
                      transform: 'translateX(1px)',
                      '& .MuiListItemIcon-root': {
                        transform: 'scale(1.02)',
                      },
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: 32,
                      color: isSelected ? item.color : 'inherit',
                    }}
                  >
                    {React.cloneElement(item.icon, { fontSize: 'small' })}
                  </ListItemIcon>
                  <ListItemText
                    primary={item.text}
                    sx={{
                      '& .MuiTypography-root': {
                        fontSize: '0.85rem',
                        fontWeight: isSelected ? 600 : 500,
                      },
                    }}
                  />
                </ListItemButton>
                </ListItem>
                {isLastCoreItem && (
                  <Box sx={{ 
                    mx: 2, 
                    my: 1, 
                    height: '1px', 
                    backgroundColor: 'rgba(0,0,0,0.08)',
                    borderRadius: '0.5px',
                  }} />
                )}
              </React.Fragment>
            );
          })}
        </List>
      </Box>

      {/* User Info */}
      <Box sx={{ 
        p: 2, 
        borderTop: '1px solid', 
        borderColor: 'divider',
        background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.03) 0%, rgba(66, 165, 245, 0.03) 100%)',
      }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 2, 
          mb: 2,
          p: 1.5,
          borderRadius: 3,
          backgroundColor: 'rgba(25, 118, 210, 0.08)',
          border: '1px solid rgba(25, 118, 210, 0.15)',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
            pointerEvents: 'none',
          },
        }}>
          <Avatar sx={{ 
            bgcolor: 'primary.main',
            width: 40,
            height: 40,
            fontSize: '1rem',
            fontWeight: 700,
            boxShadow: '0 4px 12px rgba(25, 118, 210, 0.4)',
            border: '2px solid rgba(255,255,255,0.2)',
            position: 'relative',
            zIndex: 1,
          }}>
            {user?.full_name?.charAt(0) || 'U'}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0, position: 'relative', zIndex: 1 }}>
            <Typography variant="subtitle2" noWrap sx={{ 
              fontWeight: 700, 
              fontSize: '0.9rem',
              color: 'primary.main',
              mb: 0.5,
            }}>
              {user?.full_name || 'System Administrator'}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap sx={{ 
              fontSize: '0.75rem',
              fontWeight: 500,
            }}>
              {user?.email || 'admin@garment.com'}
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Chip
            label={user?.role || 'Admin'}
            size="small"
            color="primary"
            variant="filled"
            sx={{ 
              flex: 1,
              fontWeight: 600,
              fontSize: '0.8rem',
              height: 28,
              backgroundColor: 'primary.main',
              color: 'white',
              '&:hover': {
                backgroundColor: 'primary.dark',
                transform: 'translateY(-1px)',
              },
              transition: 'all 0.2s ease-in-out',
            }}
          />
          <Chip
            label="Online"
            size="small"
            color="success"
            variant="outlined"
            sx={{ 
              fontWeight: 500,
              fontSize: '0.75rem',
              height: 28,
              borderColor: 'success.main',
              color: 'success.main',
              '& .MuiChip-icon': {
                color: 'success.main',
              },
            }}
            icon={<Box sx={{ 
              width: 8, 
              height: 8, 
              borderRadius: '50%', 
              backgroundColor: 'success.main',
              animation: 'pulse 2s infinite',
              '@keyframes pulse': {
                '0%': { opacity: 1 },
                '50%': { opacity: 0.5 },
                '100%': { opacity: 1 },
              },
            }} />}
          />
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          backgroundColor: 'white',
          color: 'text.primary',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}
      >
        <Toolbar sx={{ px: { xs: 2, sm: 3 } }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ 
              mr: 2, 
              display: { md: 'none' },
              color: 'text.primary',
            }}
          >
            <MenuIcon />
          </IconButton>
          
          <Box sx={{ flexGrow: 1 }}>
            <Typography 
              variant="h6" 
              noWrap 
              component="div" 
              sx={{ 
                fontWeight: 600,
                color: 'text.primary',
                display: { xs: 'none', sm: 'block' }
              }}
            >
              Garment Business Management System
            </Typography>
            <Typography 
              variant="h6" 
              noWrap 
              component="div" 
              sx={{ 
                fontWeight: 600,
                color: 'text.primary',
                display: { xs: 'block', sm: 'none' }
              }}
            >
              GBMS
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton color="inherit" sx={{ color: 'text.secondary' }}>
              <Badge badgeContent={3} color="error">
                <Notifications />
              </Badge>
            </IconButton>
            
            <IconButton color="inherit" sx={{ color: 'text.secondary' }}>
              <Settings />
            </IconButton>

            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenuOpen}
              color="inherit"
              sx={{ ml: 1 }}
            >
              <Avatar sx={{ width: 36, height: 36, bgcolor: 'primary.main' }}>
                {user?.full_name?.charAt(0) || 'U'}
              </Avatar>
            </IconButton>
          </Box>

          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            PaperProps={{
              sx: {
                mt: 1,
                minWidth: 200,
                boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
                borderRadius: 2,
              }
            }}
          >
            <Box sx={{ px: 2, py: 1.5, borderBottom: '1px solid', borderColor: 'divider' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                {user?.full_name || 'User'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {user?.email || 'user@example.com'}
              </Typography>
            </Box>
            <MenuItem onClick={handleMenuClose} sx={{ py: 1.5 }}>
              <ListItemIcon>
                <Settings fontSize="small" />
              </ListItemIcon>
              Settings
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout} sx={{ py: 1.5 }}>
              <ListItemIcon>
                <Logout fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
        aria-label="mailbox folders"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: mobileDrawerWidth,
              border: 'none',
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              border: 'none',
              boxShadow: '2px 0 8px rgba(0,0,0,0.1)',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: { xs: 2, sm: 3 },
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          backgroundColor: 'background.default',
        }}
      >
        <Toolbar />
        <Box sx={{ maxWidth: '100%', overflow: 'hidden' }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;

