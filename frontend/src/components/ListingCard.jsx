import React, { useState } from 'react';
import { MapPin, Bed, Bath, MessageSquare, Eye, ShieldCheck } from 'lucide-react';
import { CompatibilityBadge } from './CompatibilityBadge';
import { ListingDetailModal } from './ListingDetailModal';
import { LandlordTenantChatModal } from './LandlordTenantChatModal';

export const ListingCard = ({ listing }) => {
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  const imageUrl = listing.images?.[0] || 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80';

  return (
    <>
      <div
        className="glass-card-interactive"
        style={{
          padding: '20px',
          cursor: 'pointer',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between'
        }}
        onClick={() => setIsDetailOpen(true)}
      >
        <div>
          {/* Property Image Header with Clean Badge Inset Margins */}
          <div style={{
            width: '100%',
            height: '190px',
            borderRadius: '14px',
            backgroundImage: `url(${imageUrl})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            padding: '14px',
            position: 'relative'
          }}>
            <CompatibilityBadge score={listing.score || listing.recommendation_score || 95} />
            <span style={{
              background: 'rgba(15, 23, 42, 0.85)',
              backdropFilter: 'blur(8px)',
              padding: '6px 12px',
              borderRadius: '12px',
              color: '#34d399',
              fontSize: '0.78rem',
              fontWeight: 800,
              border: '1px solid rgba(5, 150, 105, 0.4)',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
            }}>
              <ShieldCheck size={13} /> Verified Listing
            </span>
          </div>

          <h3 style={{ fontSize: '1.18rem', fontWeight: 800, marginBottom: '6px', color: 'var(--text-primary)', fontFamily: 'var(--font-header)' }}>
            {listing.title}
          </h3>

          <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MapPin size={15} color="var(--accent-sky)" /> {listing.city}, {listing.state || 'CA'}
          </p>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-subtle)', paddingTop: '14px', marginBottom: '18px' }}>
            <div style={{ display: 'flex', gap: '14px', color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600 }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><Bed size={15} color="var(--accent-sky)" /> {listing.bedrooms} Bed</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><Bath size={15} color="#c084fc" /> {listing.bathrooms} Bath</span>
            </div>

            <div>
              <span style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--accent-emerald)', fontFamily: 'var(--font-header)' }}>
                ${listing.price}
              </span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>/mo</span>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsChatOpen(true);
            }}
            className="btn-emerald"
            style={{
              flex: 1,
              padding: '10px 14px',
              borderRadius: '10px',
              fontWeight: 800,
              fontSize: '0.84rem',
              justifyContent: 'center'
            }}
          >
            <MessageSquare size={15} /> Chat Landlord
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsDetailOpen(true);
            }}
            className="btn-secondary"
            style={{
              padding: '10px 14px',
              borderRadius: '10px',
              fontSize: '0.84rem',
              fontWeight: 700
            }}
          >
            <Eye size={15} /> Details
          </button>
        </div>
      </div>

      <ListingDetailModal
        listing={listing}
        isOpen={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
      />

      <LandlordTenantChatModal
        listing={listing}
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />
    </>
  );
};

export default ListingCard;
