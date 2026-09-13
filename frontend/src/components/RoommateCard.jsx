import React from 'react';
import { UserCheck, Moon, Sun, DollarSign } from 'lucide-react';
import { CompatibilityBadge } from './CompatibilityBadge';

export const RoommateCard = ({ roommate }) => {
  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <div style={{ width: '56px', height: '56px', borderRadius: '50%', background: 'var(--accent-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', fontWeight: 800 }}>
            {roommate.name ? roommate.name[0] : 'A'}
          </div>
          <div>
            <h4 style={{ fontSize: '1.1rem', fontWeight: 700 }}>{roommate.name || 'Alice Smith'}</h4>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{roommate.preferred_location || 'San Francisco, CA'}</span>
          </div>
        </div>
        <CompatibilityBadge score={roommate.score || 96} />
      </div>

      <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '12px 16px', borderRadius: '12px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px', fontSize: '0.85rem' }}>
        <div>
          <span style={{ color: 'var(--text-muted)', display: 'block' }}>Budget Range</span>
          <strong>${roommate.budget_min || 1500} - ${roommate.budget_max || 2200}/mo</strong>
        </div>
        <div>
          <span style={{ color: 'var(--text-muted)', display: 'block' }}>Schedule</span>
          <strong>{roommate.sleep_schedule || 'Early Bird'}</strong>
        </div>
      </div>

      <button className="btn-primary" style={{ width: '100%' }}>Connect & View Profile</button>
    </div>
  );
};
