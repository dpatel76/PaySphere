/**
 * GPS CDM React Application
 */
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SnackbarProvider } from 'notistack';

import theme from './theme';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AppLayout from './components/layout/AppLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ExceptionsPage from './pages/ExceptionsPage';
import ProcessFilePage from './pages/ProcessFilePage';
import LineagePage from './pages/LineagePage';

// Lazy load other pages
const DataQualityPage = React.lazy(() => import('./pages/DataQualityPage'));
const ReconciliationPage = React.lazy(() => import('./pages/ReconciliationPage'));
const ReprocessPage = React.lazy(() => import('./pages/ReprocessPage'));
const MonitoringDashboardPage = React.lazy(() => import('./pages/MonitoringDashboardPage'));
const ErrorsDashboardPage = React.lazy(() => import('./pages/ErrorsDashboardPage'));

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000, // 30 seconds
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SnackbarProvider
          maxSnack={3}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <BrowserRouter>
            <AuthProvider>
              <Routes>
                {/* Public route - Login */}
                <Route path="/login" element={<LoginPage />} />

                {/* Protected routes */}
                <Route path="/" element={
                  <ProtectedRoute>
                    <AppLayout />
                  </ProtectedRoute>
                }>
                  <Route index element={<DashboardPage />} />
                  <Route path="exceptions" element={<ExceptionsPage />} />
                  <Route path="data-quality" element={
                    <React.Suspense fallback={<div>Loading...</div>}>
                      <DataQualityPage />
                    </React.Suspense>
                  } />
                  <Route path="reconciliation" element={
                    <React.Suspense fallback={<div>Loading...</div>}>
                      <ReconciliationPage />
                    </React.Suspense>
                  } />
                  <Route path="lineage" element={<LineagePage />} />
                  <Route path="process" element={<ProcessFilePage />} />
                  <Route path="reprocess" element={
                    <React.Suspense fallback={<div>Loading...</div>}>
                      <ReprocessPage />
                    </React.Suspense>
                  } />
                  <Route path="monitoring" element={
                    <React.Suspense fallback={<div>Loading...</div>}>
                      <MonitoringDashboardPage />
                    </React.Suspense>
                  } />
                  <Route path="errors" element={
                    <React.Suspense fallback={<div>Loading...</div>}>
                      <ErrorsDashboardPage />
                    </React.Suspense>
                  } />
                </Route>
              </Routes>
            </AuthProvider>
          </BrowserRouter>
        </SnackbarProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
