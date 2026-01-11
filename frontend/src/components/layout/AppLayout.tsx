/**
 * GPS CDM Main Application Layout
 */
import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Divider,
  Chip,
  Menu,
  MenuItem,
  Avatar,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  CompareArrows as CompareArrowsIcon,
  AccountTree as AccountTreeIcon,
  Upload as UploadIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Person as PersonIcon,
  Logout as LogoutIcon,
  MonitorHeart as MonitoringIcon,
  ErrorOutline as ErrorIcon,
  Description as MappingsIcon,
  Storage as CatalogIcon,
} from '@mui/icons-material';
import { colors } from '../../styles/design-system';
import { useAuth } from '../../contexts/AuthContext';

const DRAWER_WIDTH = 260;

const navItems = [
  { path: '/', label: 'Pipeline Dashboard', icon: <DashboardIcon /> },
  { path: '/monitoring', label: 'Full Monitoring', icon: <MonitoringIcon /> },
  { path: '/errors', label: 'Processing Errors', icon: <ErrorIcon /> },
  { path: '/exceptions', label: 'Exception Handling', icon: <WarningIcon /> },
  { path: '/data-quality', label: 'Data Quality', icon: <CheckCircleIcon /> },
  { path: '/reconciliation', label: 'Reconciliation', icon: <CompareArrowsIcon /> },
  { path: '/lineage', label: 'Data Lineage', icon: <AccountTreeIcon /> },
  { path: '/mappings', label: 'Mappings Documentation', icon: <MappingsIcon /> },
  { path: '/catalog', label: 'CDM Data Catalog', icon: <CatalogIcon /> },
  { path: '/process', label: 'Process File', icon: <UploadIcon /> },
  { path: '/reprocess', label: 'Reprocess', icon: <RefreshIcon /> },
];

const AppLayout: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleLogout = () => {
    handleUserMenuClose();
    logout();
    navigate('/login');
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: colors.primary.main,
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(!drawerOpen)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            GPS CDM - Data Pipeline Governance
          </Typography>
          <Chip
            label="PostgreSQL"
            size="small"
            sx={{
              backgroundColor: 'rgba(255,255,255,0.2)',
              color: 'white',
              mr: 1,
            }}
          />
          <Chip
            label="v1.0"
            size="small"
            sx={{
              backgroundColor: 'rgba(255,255,255,0.2)',
              color: 'white',
              mr: 2,
            }}
          />
          {/* User Menu */}
          <IconButton
            onClick={handleUserMenuOpen}
            sx={{ p: 0.5 }}
          >
            <Avatar
              sx={{
                width: 36,
                height: 36,
                bgcolor: colors.secondary.main,
                fontSize: '0.9rem',
              }}
            >
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </Avatar>
          </IconButton>
          <Menu
            anchorEl={userMenuAnchor}
            open={Boolean(userMenuAnchor)}
            onClose={handleUserMenuClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            <MenuItem disabled sx={{ opacity: 1 }}>
              <Box>
                <Typography variant="subtitle2" fontWeight={600}>
                  {user?.username || 'User'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {user?.email || ''}
                </Typography>
              </Box>
            </MenuItem>
            <Divider />
            <MenuItem onClick={() => { handleUserMenuClose(); handleNavigation('/settings'); }}>
              <ListItemIcon>
                <PersonIcon fontSize="small" />
              </ListItemIcon>
              Profile
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Side Drawer */}
      <Drawer
        variant="persistent"
        anchor="left"
        open={drawerOpen}
        sx={{
          width: drawerOpen ? DRAWER_WIDTH : 0,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            backgroundColor: colors.grey[50],
            borderRight: `1px solid ${colors.grey[200]}`,
          },
        }}
      >
        <Toolbar /> {/* Spacer for AppBar */}
        <Box sx={{ overflow: 'auto', mt: 1 }}>
          <List>
            {navItems.map((item) => (
              <ListItem key={item.path} disablePadding>
                <ListItemButton
                  selected={location.pathname === item.path}
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    mx: 1,
                    borderRadius: 1,
                    mb: 0.5,
                    '&.Mui-selected': {
                      backgroundColor: colors.primary.light,
                      color: 'white',
                      '& .MuiListItemIcon-root': {
                        color: 'white',
                      },
                      '&:hover': {
                        backgroundColor: colors.primary.main,
                      },
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: 40,
                      color: location.pathname === item.path ? 'white' : colors.grey[600],
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText primary={item.label} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
          <Divider sx={{ my: 2 }} />
          <List>
            <ListItem disablePadding>
              <ListItemButton
                onClick={() => handleNavigation('/settings')}
                sx={{ mx: 1, borderRadius: 1 }}
              >
                <ListItemIcon sx={{ minWidth: 40, color: colors.grey[600] }}>
                  <SettingsIcon />
                </ListItemIcon>
                <ListItemText primary="Settings" />
              </ListItemButton>
            </ListItem>
          </List>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          ml: drawerOpen ? 0 : `-${DRAWER_WIDTH}px`,
          transition: 'margin 0.2s ease-in-out',
          backgroundColor: colors.background.default,
          minHeight: '100vh',
        }}
      >
        <Toolbar /> {/* Spacer for AppBar */}
        <Outlet />
      </Box>
    </Box>
  );
};

export default AppLayout;
