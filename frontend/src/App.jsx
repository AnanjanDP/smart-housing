import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Header } from './components/Header';
import { Home } from './pages/Home';
import { ListingsPage } from './pages/ListingsPage';
import { RoommatesPage } from './pages/RoommatesPage';
import { DashboardPage } from './pages/DashboardPage';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import ErrorBoundary from './components/ErrorBoundary';

export const App = () => {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <Router
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true,
          }}
        >
          <AuthProvider>
          <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <Header />
            <main style={{ flex: 1 }}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route
                  path="/listings"
                  element={
                    <ProtectedRoute>
                      <ListingsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/roommates"
                  element={
                    <ProtectedRoute>
                      <RoommatesPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/mydashboard"
                  element={
                    <ProtectedRoute>
                      <DashboardPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <DashboardPage />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </main>
            <footer style={{ textAlign: 'center', padding: '24px', borderTop: '1px solid var(--border-color)', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              &copy; 2026 StayMatch Platform Inc. All rights reserved.
            </footer>
          </div>
        </AuthProvider>
      </Router>
    </ThemeProvider>
  </ErrorBoundary>
  );
};

export default App;