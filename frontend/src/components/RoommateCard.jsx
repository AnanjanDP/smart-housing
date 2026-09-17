import React, { useState, useContext } from 'react';
import { UserCheck, MessageSquare, MapPin, DollarSign, Calendar, Sparkles, CheckCircle2, ShieldCheck, Heart, Info } from 'lucide-react';
import { CompatibilityBadge } from './CompatibilityBadge';
import { ProfileModal } from './ProfileModal';
import { RoommateChatModal } from './RoommateChatModal';
import { AuthContext } from '../context/AuthContext';

export const RoommateCard = ({ roommate, onConnectChange, isInitiallyConnected = false }) => {
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isConnected, setIsConnected] = useState(isInitiallyConnected || roommate.isConnected || false);
  const { addSentRequest } = useContext(AuthContext);

  const handleConnect = (e) => {
    if (e) e.stopPropagation();
    setIsConnected(true);
    if (onConnectChange) onConnectChange(roommate.id, true);

    if (addSentRequest) {
      addSentRequest({
        id: `req-${Date.now()}`,
        type: "ROOMMATE_CONNECT",
        title: `Connection Request to ${roommate.name || 'Roommate'}`,
        location: roommate.preferred_location || 'San Francisco, CA',
        price: null,
        status: "ACCEPTED",
        submittedAt: new Date().toISOString().split('T')[0],
        recipient: roommate.name || 'Roommate'
      });
    }
  };

  const handleOpenChat = (e) => {
    if (e) e.stopPropagation();
    if (!isConnected) {
      handleConnect();
    }
    setIsChatOpen(true);
  };

  const getDealbreakerTags = () => {
    const tags = [];

    // Smoking dealbreaker
    if (roommate.is_smoker === false || roommate.smoking === 'Non-smoker' || roommate.non_smoker) {
      tags.push({ label: '🚭 Non-Smoker', bg: 'rgba(16, 185, 129, 0.12)', color: '#34d399', border: 'rgba(16, 185, 129, 0.3)' });
    } else {
      tags.push({ label: '🚬 Smoker OK', bg: 'rgba(245, 158, 11, 0.12)', color: '#fbbf24', border: 'rgba(245, 158, 11, 0.3)' });
    }

    // Pet dealbreaker
    if (roommate.pets_allowed || roommate.pets === 'Pet Friendly') {
      tags.push({ label: '🐶 Pet Friendly', bg: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8', border: 'rgba(56, 189, 248, 0.3)' });
    } else {
      tags.push({ label: '🚫 No Pets', bg: 'rgba(244, 63, 94, 0.12)', color: '#f43f5e', border: 'rgba(244, 63, 94, 0.3)' });
    }

    // Schedule
    const sched = roommate.sleep_schedule || 'Early Bird';
    if (sched.includes('Early')) {
      tags.push({ label: '🌅 Early Bird', bg: 'rgba(245, 158, 11, 0.12)', color: '#fcd34d', border: 'rgba(245, 158, 11, 0.3)' });
    } else if (sched.includes('Night')) {
      tags.push({ label: '🌙 Night Owl', bg: 'rgba(192, 132, 252, 0.12)', color: '#c084fc', border: 'rgba(192, 132, 252, 0.3)' });
    } else {
      tags.push({ label: '⚡ Flexible Schedule', bg: 'rgba(56, 189, 248, 0.12)', color: '#93c5fd', border: 'rgba(56, 189, 248, 0.3)' });
    }

    // Work style
    if (roommate.work_style === 'WFH' || roommate.wfh) {
      tags.push({ label: '💻 WFH', bg: 'rgba(14, 165, 233, 0.12)', color: '#38bdf8', border: 'rgba(14, 165, 233, 0.3)' });
    } else {
      tags.push({ label: '🏢 In-Office', bg: 'rgba(168, 85, 247, 0.12)', color: '#e879f9', border: 'rgba(168, 85, 247, 0.3)' });
    }

    // Cleanliness
    const cleanLevel = roommate.cleanliness_level || 4;
    tags.push({ label: `🧹 Cleanliness ${cleanLevel}/5`, bg: 'var(--bg-surface-elevated)', color: 'var(--text-primary)', border: 'var(--border-color)' });

    return tags;
  };

  const dealbreakerTags = getDealbreakerTags();

  return (
    <>
      <div
        className="glass-card-interactive"
        style={{
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          justify: 'space-between',
          position: 'relative',
          border: isConnected ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid var(--border-subtle)',
          background: isConnected ? 'rgba(5, 150, 105, 0.05)' : 'var(--bg-surface)'
        }}
      >
        {/* Connected Indicator Banner */}
        {isConnected && (
          <div style={{
            position: 'absolute',
            top: '-12px',
            right: '24px',
            background: 'var(--accent-emerald)',
            color: '#ffffff',
            fontSize: '0.75rem',
            fontWeight: 800,
            padding: '4px 12px',
            borderRadius: '12px',
            boxShadow: '0 4px 12px var(--accent-emerald-glow)',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            <CheckCircle2 size={12} /> Connected & Chat Active
          </div>
        )}

        <div>
          {/* Header row: Avatar, Name, Location & Compatibility */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
            <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
              <div style={{ position: 'relative' }}>
                <div style={{
                  width: '58px',
                  height: '58px',
                  borderRadius: '50%',
                  background: 'var(--accent-emerald)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.3rem',
                  fontWeight: 800,
                  color: '#ffffff',
                  border: '2px solid var(--border-color)',
                  boxShadow: 'var(--shadow-sm)',
                  overflow: 'hidden'
                }}>
                  {roommate.avatar ? (
                    <img src={roommate.avatar} alt={roommate.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    roommate.name ? roommate.name[0] : 'A'
                  )}
                </div>
                {isConnected && (
                  <div style={{
                    position: 'absolute',
                    bottom: 0,
                    right: 0,
                    width: '14px',
                    height: '14px',
                    borderRadius: '50%',
                    background: '#059669',
                    border: '2px solid #ffffff'
                  }} title="Connected" />
                )}
              </div>

              <div>
                <h4 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)', fontFamily: 'var(--font-header)' }}>
                  {roommate.name || 'Roommate Candidate'}
                </h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginTop: '3px' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.84rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <MapPin size={14} color="var(--accent-sky)" /> {roommate.preferred_location || 'San Francisco, CA'}
                  </span>
                </div>
              </div>
            </div>

            <CompatibilityBadge score={roommate.score || 96} />
          </div>

          {/* Budget & Move-in Banner */}
          <div style={{
            background: 'var(--bg-surface-elevated)',
            border: '1px solid var(--border-subtle)',
            padding: '12px 14px',
            borderRadius: '12px',
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '10px',
            marginBottom: '16px',
            fontSize: '0.85rem'
          }}>
            <div>
              <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem', fontWeight: 600 }}>Monthly Budget</span>
              <strong style={{ color: 'var(--accent-emerald)', fontSize: '0.98rem', fontWeight: 800 }}>
                ${roommate.budget_min || 1500} - ${roommate.budget_max || 2200}/mo
              </strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.75rem', fontWeight: 600 }}>Move-in Date</span>
              <strong style={{ color: 'var(--text-primary)', fontSize: '0.9rem', fontWeight: 700 }}>
                {roommate.move_in_date || 'Flexible'}
              </strong>
            </div>
          </div>

          {/* Lifestyle Dealbreaker Tags */}
          <div style={{ marginBottom: '16px' }}>
            <span style={{ display: 'block', color: 'var(--text-muted)', fontSize: '0.74rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px' }}>
              Lifestyle Dealbreakers
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {dealbreakerTags.map((tag, idx) => (
                <span
                  key={idx}
                  style={{
                    padding: '4px 10px',
                    borderRadius: '8px',
                    background: tag.bg,
                    color: tag.color,
                    border: `1px solid ${tag.border}`,
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  {tag.label}
                </span>
              ))}
            </div>
          </div>

          {/* Bio Preview */}
          <p style={{
            color: 'var(--text-secondary)',
            fontSize: '0.86rem',
            lineHeight: 1.5,
            marginBottom: '20px',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}>
            {roommate.bio || 'Verified StayMatch roommate candidate.'}
          </p>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', gap: '8px' }}>
          {isConnected ? (
            <>
              <button
                className="btn-emerald"
                onClick={handleOpenChat}
                style={{
                  flex: 1,
                  padding: '10px 14px',
                  borderRadius: '10px',
                  fontWeight: 800,
                  fontSize: '0.86rem',
                  justifyContent: 'center'
                }}
              >
                <MessageSquare size={16} /> Open Chat
              </button>
              <button
                className="btn-secondary"
                onClick={() => setIsProfileOpen(true)}
                style={{ padding: '10px 14px', borderRadius: '10px' }}
                title="View Full Profile"
              >
                <Info size={16} />
              </button>
            </>
          ) : (
            <button
              className="btn-emerald"
              onClick={() => setIsProfileOpen(true)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '10px',
                fontWeight: 800,
                fontSize: '0.9rem',
                justifyContent: 'center'
              }}
            >
              <UserCheck size={16} /> Connect & View Profile
            </button>
          )}
        </div>
      </div>

      {/* Profile Modal */}
      <ProfileModal
        roommate={{ ...roommate, isConnected }}
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        onConnect={() => {
          handleConnect();
          setIsProfileOpen(false);
          setIsChatOpen(true);
        }}
        onOpenChat={() => {
          setIsProfileOpen(false);
          setIsChatOpen(true);
        }}
      />

      {/* Chat Modal Drawer */}
      <RoommateChatModal
        roommate={roommate}
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />
    </>
  );
};

export default RoommateCard;
