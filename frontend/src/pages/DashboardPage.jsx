import React from 'react';

export const DashboardPage = () => {
  return (
    <div style={{ padding: '32px' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '24px' }}>User Application Dashboard</h1>
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3>Your Pending Housing Applications</h3>
        <p style={{ color: 'var(--text-muted)', marginTop: '8px' }}>No active rental applications submitted yet.</p>
      </div>
    </div>
  );
};
