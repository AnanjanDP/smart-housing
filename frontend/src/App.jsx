import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Header } from './components/Header';
import { Home } from './pages/Home';
import { ListingsPage } from './pages/ListingsPage';
import { RoommatesPage } from './pages/RoommatesPage';
import { DashboardPage } from './pages/DashboardPage';
import { AuthProvider } from './context/AuthContext';

export const App = () => {
  return (
    <AuthProvider>
      <Router>
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
          <Header />
          <main style={{ flex: 1 }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/listings" element={<ListingsPage />} />
              <Route path="/roommates" element={<RoommatesPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
            </Routes>
          </main>
          <footer style={{ textAlign: 'center', padding: '24px', borderTop: '1px solid var(--border-color)', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            &copy; 2026 StayMatch Platform Inc. All rights reserved.
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
