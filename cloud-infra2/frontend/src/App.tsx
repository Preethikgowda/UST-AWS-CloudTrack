/* ============================================================
   IntelliWealth – App Router
   ============================================================ */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import ProtectedRoute from './auth/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import PortfolioOverview from './pages/PortfolioOverview';
import PortfolioHistory from './pages/PortfolioHistory';
import AssetAllocation from './pages/AssetAllocation';
import Profile from './pages/Profile';
import Admin from './pages/Admin';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<Login />} />

          {/* Protected routes with sidebar layout */}
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/portfolio" element={<PortfolioOverview />} />
            <Route path="/history" element={<PortfolioHistory />} />
            <Route path="/allocation" element={<AssetAllocation />} />
            <Route path="/profile" element={<Profile />} />
            <Route
              path="/admin"
              element={
                <ProtectedRoute requiredRole="admin">
                  <Admin />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
