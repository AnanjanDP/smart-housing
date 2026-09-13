import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Search, Users, User, ShieldCheck } from 'lucide-react';

export const Header = () => {
  return (
    <header className="glass-panel" style={{ margin: '16px 24px', padding: '16px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ width: '40px', height: '40px', background: 'var(--accent-gradient)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Home color="white" size={22} />
        </div>
        <span style={{ fontSize: '1.4rem', fontWeight: 800 }} className="gradient-text">StayMatch</span>
      </div>

      <nav style={{ display: 'flex', gap: '32px' }}>
        <Link to="/" style={{ color: 'var(--text-main)', textDecoration: 'none', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Home size={18} /> Home
        </Link>
        <Link to="/listings" style={{ color: 'var(--text-muted)', textDecoration: 'none', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Search size={18} /> Properties
        </Link>
        <Link to="/roommates" style={{ color: 'var(--text-muted)', textDecoration: 'none', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Users size={18} /> Roommates
        </Link>
      </nav>

      <button className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <User size={18} /> Sign In
      </button>
    </header>
  );
};
