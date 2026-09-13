import React from 'react';
import { MapPin, Bed, Bath, DollarSign } from 'lucide-react';
import { CompatibilityBadge } from './CompatibilityBadge';

export const ListingCard = ({ listing }) => {
  return (
    <div className="glass-panel" style={{ padding: '20px', transition: 'transform 0.3s ease', cursor: 'pointer' }}>
      <div style={{ width: '100%', height: '180px', borderRadius: '12px', background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', marginBottom: '16px', display: 'flex', alignItems: 'flex-end', padding: '12px' }}>
        <CompatibilityBadge score={listing.score || 94} />
      </div>
      <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '8px' }}>{listing.title}</h3>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <MapPin size={16} color="var(--accent-cyan)" /> {listing.city}, {listing.state || 'CA'}
      </p>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
        <div style={{ display: 'flex', gap: '16px', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Bed size={16} /> {listing.bedrooms} Bed</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Bath size={16} /> {listing.bathrooms} Bath</span>
        </div>
        <span style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--accent-emerald)' }}>${listing.price}<small style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>/mo</small></span>
      </div>
    </div>
  );
};
