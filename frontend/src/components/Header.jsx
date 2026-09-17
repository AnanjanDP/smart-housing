import React, { useState, useContext } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Search, Users, User, LogOut, LayoutDashboard, Building2, Sun, Moon } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { LoginModal } from './LoginModal';
import { OnboardingModal } from './OnboardingModal';

export const Header = () => {
  const { user, isAuthenticated, logout, showOnboarding, setShowOnboarding } = useContext(AuthContext);
  const { theme, toggleTheme } = useTheme();
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [loginInitialMode, setLoginInitialMode] = useState('login');
  const location = useLocation();

  const displayName = user?.name || user?.first_name || user?.username || 'User';
  const isLandlord = user?.role === 'LANDLORD';

  const isActive = (path) => location.pathname === path;

  return (
    <>
      <header style={{
        margin: '16px 24px',
        padding: '14px 28px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-color)',
        borderRadius: '20px',
        boxShadow: 'var(--shadow-md)',
        transition: 'all 0.25s ease'
      }}>
        {/* Logo */}
        <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '38px',
            height: '38px',
            background: 'var(--accent-emerald)',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 14px var(--accent-emerald-glow)'
          }}>
            <Building2 color="#ffffff" size={20} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'var(--font-header)', letterSpacing: '-0.02em' }}>
              StayMatch
            </span>
            <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Smart Housing Platform
            </span>
          </div>
        </Link>

        {/* Navigation Items */}
        <nav style={{ display: 'flex', gap: '6px', background: 'var(--bg-surface-elevated)', padding: '4px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <Link to="/" style={{
            color: isActive('/') ? 'var(--text-primary)' : 'var(--text-secondary)',
            background: isActive('/') ? 'var(--bg-surface)' : 'transparent',
            boxShadow: isActive('/') ? 'var(--shadow-sm)' : 'none',
            textDecoration: 'none',
            fontWeight: isActive('/') ? 700 : 600,
            fontSize: '0.88rem',
            padding: '8px 16px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.2s ease'
          }}>
            <Home size={16} color={isActive('/') ? 'var(--accent-emerald)' : 'var(--text-muted)'} /> Home
          </Link>

          {isAuthenticated && (
            <>
              <Link to="/listings" style={{
                color: isActive('/listings') ? 'var(--text-primary)' : 'var(--text-secondary)',
                background: isActive('/listings') ? 'var(--bg-surface)' : 'transparent',
                boxShadow: isActive('/listings') ? 'var(--shadow-sm)' : 'none',
                textDecoration: 'none',
                fontWeight: isActive('/listings') ? 700 : 600,
                fontSize: '0.88rem',
                padding: '8px 16px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'all 0.2s ease'
              }}>
                <Search size={16} color={isActive('/listings') ? 'var(--accent-emerald)' : 'var(--text-muted)'} /> Properties
              </Link>

              {!isLandlord && (
                <Link to="/roommates" style={{
                  color: isActive('/roommates') ? 'var(--text-primary)' : 'var(--text-secondary)',
                  background: isActive('/roommates') ? 'var(--bg-surface)' : 'transparent',
                  boxShadow: isActive('/roommates') ? 'var(--shadow-sm)' : 'none',
                  textDecoration: 'none',
                  fontWeight: isActive('/roommates') ? 700 : 600,
                  fontSize: '0.88rem',
                  padding: '8px 16px',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  transition: 'all 0.2s ease'
                }}>
                  <Users size={16} color={isActive('/roommates') ? 'var(--accent-emerald)' : 'var(--text-muted)'} /> Roommate Finder
                </Link>
              )}

              <Link to="/mydashboard" style={{
                color: isActive('/mydashboard') ? 'var(--text-primary)' : 'var(--text-secondary)',
                background: isActive('/mydashboard') ? 'var(--bg-surface)' : 'transparent',
                boxShadow: isActive('/mydashboard') ? 'var(--shadow-sm)' : 'none',
                textDecoration: 'none',
                fontWeight: isActive('/mydashboard') ? 700 : 600,
                fontSize: '0.88rem',
                padding: '8px 16px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'all 0.2s ease'
              }}>
                {isLandlord ? <Building2 size={16} color="var(--accent-sky)" /> : <LayoutDashboard size={16} color={isActive('/mydashboard') ? 'var(--accent-emerald)' : 'var(--text-muted)'} />}
                {isLandlord ? 'Landlord Portal' : 'My Dashboard'}
              </Link>
            </>
          )}
        </nav>

        {/* User Status, Theme Toggle & Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginLeft: 'auto' }}>
          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="theme-toggle-btn"
            title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
            aria-label="Toggle theme"
          >
            {theme === 'light' ? <Moon size={18} color="var(--text-primary)" /> : <Sun size={18} color="#f59e0b" />}
          </button>

          {isAuthenticated ? (
            <>
              <Link to="/mydashboard" style={{ color: 'var(--text-primary)', textDecoration: 'none', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '10px',
                  overflow: 'hidden',
                  background: isLandlord ? 'rgba(2, 132, 199, 0.1)' : 'rgba(5, 150, 105, 0.1)',
                  border: isLandlord ? '1px solid rgba(2, 132, 199, 0.3)' : '1px solid rgba(5, 150, 105, 0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.88rem',
                  fontWeight: 800,
                  color: isLandlord ? 'var(--accent-sky)' : 'var(--accent-emerald)'
                }}>
                  {user?.avatar_url ? (
                    <img src={user.avatar_url} alt={displayName} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    displayName[0]?.toUpperCase()
                  )}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 700, lineHeight: 1.2, color: 'var(--text-primary)', fontFamily: 'Plus Jakarta Sans, sans-serif' }}>{displayName}</span>
                  <span style={{ fontSize: '0.72rem', color: isLandlord ? 'var(--accent-sky)' : 'var(--text-muted)', fontWeight: 600 }}>
                    {isLandlord ? 'Landlord' : 'Tenant'}
                  </span>
                </div>
              </Link>

              <button
                onClick={logout}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 14px',
                  borderRadius: '10px',
                  background: 'rgba(239, 68, 68, 0.08)',
                  border: '1px solid rgba(239, 68, 68, 0.25)',
                  color: 'var(--accent-rose)',
                  fontSize: '0.82rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  fontFamily: 'Plus Jakarta Sans, sans-serif',
                  transition: 'all 0.2s ease'
                }}
              >
                <LogOut size={15} /> Sign Out
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => {
                  setLoginInitialMode('login');
                  setIsLoginOpen(true);
                }}
                style={{
                  padding: '10px 20px',
                  borderRadius: '10px',
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-strong)',
                  color: 'var(--text-primary)',
                  fontSize: '0.88rem',
                  fontWeight: 700,
                  fontFamily: 'Plus Jakarta Sans, sans-serif',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: 'var(--shadow-sm)',
                  transition: 'all 0.15s ease'
                }}
              >
                <User size={15} color="var(--accent-emerald)" /> Sign In
              </button>

              <button
                className="btn-emerald"
                onClick={() => {
                  setLoginInitialMode('register');
                  setIsLoginOpen(true);
                }}
                style={{
                  padding: '10px 24px',
                  borderRadius: '10px',
                  fontSize: '0.88rem',
                  fontWeight: 800,
                  fontFamily: 'Plus Jakarta Sans, sans-serif',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                Register
              </button>
            </>
          )}
        </div>
      </header>

      <LoginModal isOpen={isLoginOpen} onClose={() => setIsLoginOpen(false)} initialMode={loginInitialMode} />
      <OnboardingModal isOpen={showOnboarding} onClose={() => setShowOnboarding(false)} />
    </>
  );
};