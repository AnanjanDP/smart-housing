import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { LandlordDashboard } from './LandlordDashboard';
import { ProfileCompletionCard } from '../components/ProfileCompletionCard';
import { LandlordTenantChatModal } from '../components/LandlordTenantChatModal';
import { fetchApplicationsApi } from '../services/api';
import { Send, Inbox, CheckCircle, Clock, XCircle, User, Home, Shield, ArrowUpRight, MessageSquare, Building2, ChevronRight } from 'lucide-react';

export const DashboardPage = () => {
  const { user, sentRequests, receivedRequests, setShowOnboarding } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('sent'); // 'sent', 'received', or 'messages'
  const [selectedChatListing, setSelectedChatListing] = useState(null);
  const [applications, setApplications] = useState([]);

  useEffect(() => {
    fetchApplicationsApi()
      .then((data) => {
        setApplications(Array.isArray(data) ? data : (data?.results || []));
      })
      .catch((err) => {
        console.error('Failed to fetch applications:', err);
        setApplications([]);
      });
  }, []);

  // If user role is LANDLORD, render Landlord Dashboard directly!
  if (user?.role === 'LANDLORD') {
    return <LandlordDashboard />;
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'APPROVED':
      case 'ACCEPTED':
        return (
          <span style={{ padding: '6px 12px', borderRadius: '20px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', color: '#10b981', fontSize: '0.85rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <CheckCircle size={14} /> Approved
          </span>
        );
      case 'DECLINED':
      case 'REJECTED':
        return (
          <span style={{ padding: '6px 12px', borderRadius: '20px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', color: '#ef4444', fontSize: '0.85rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <XCircle size={14} /> Declined
          </span>
        );
      default:
        return (
          <span style={{ padding: '6px 12px', borderRadius: '20px', background: 'rgba(245, 158, 11, 0.15)', border: '1px solid rgba(245, 158, 11, 0.4)', color: '#f59e0b', fontSize: '0.85rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <Clock size={14} /> Pending Review
          </span>
        );
    }
  };

  return (
    <div style={{ padding: '40px 48px', maxWidth: '1150px', margin: '0 auto' }}>
      {/* Header Banner */}
      <div className="glass-card" style={{ padding: '28px 32px', borderRadius: '18px', marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap', marginBottom: '8px' }}>
          <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: '2.2rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            My Dashboard
          </h1>
          <span className="badge-emerald" style={{ fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.06em', padding: '4px 12px' }}>
            Role: {user?.role || 'Tenant'}
          </span>
        </div>
        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.98rem' }}>
          Welcome back, <strong style={{ color: 'var(--text-primary)' }}>{user?.name || user?.first_name || user?.username || 'User'}</strong>! Track all your rental applications, roommate requests, and landlord messages.
        </p>
      </div>

      {/* Profile Completion Widget */}
      <ProfileCompletionCard user={user} onOpenOnboarding={() => setShowOnboarding(true)} />

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '28px', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px', flexWrap: 'wrap' }}>
        <button
          onClick={() => setActiveTab('sent')}
          style={{
            padding: '12px 22px',
            borderRadius: '12px',
            background: activeTab === 'sent' ? 'var(--accent-emerald)' : 'var(--bg-surface-elevated)',
            border: activeTab === 'sent' ? '1px solid var(--accent-emerald)' : '1px solid var(--border-color)',
            color: activeTab === 'sent' ? '#ffffff' : 'var(--text-secondary)',
            fontWeight: 700,
            fontSize: '0.9rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.15s ease',
            boxShadow: activeTab === 'sent' ? '0 4px 14px var(--accent-emerald-glow)' : 'none'
          }}
        >
          <Send size={16} color={activeTab === 'sent' ? '#ffffff' : 'var(--accent-emerald)'} /> Requests I Sent ({sentRequests.length})
        </button>

        <button
          onClick={() => setActiveTab('received')}
          style={{
            padding: '12px 22px',
            borderRadius: '12px',
            background: activeTab === 'received' ? 'var(--accent-emerald)' : 'var(--bg-surface-elevated)',
            border: activeTab === 'received' ? '1px solid var(--accent-emerald)' : '1px solid var(--border-color)',
            color: activeTab === 'received' ? '#ffffff' : 'var(--text-secondary)',
            fontWeight: 700,
            fontSize: '0.9rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.15s ease',
            boxShadow: activeTab === 'received' ? '0 4px 14px var(--accent-emerald-glow)' : 'none'
          }}
        >
          <Inbox size={16} color={activeTab === 'received' ? '#ffffff' : 'var(--accent-emerald)'} /> Requests I Received ({receivedRequests.length})
        </button>

        <button
          onClick={() => setActiveTab('messages')}
          style={{
            padding: '12px 22px',
            borderRadius: '12px',
            background: activeTab === 'messages' ? 'var(--accent-emerald)' : 'var(--bg-surface-elevated)',
            border: activeTab === 'messages' ? '1px solid var(--accent-emerald)' : '1px solid var(--border-color)',
            color: activeTab === 'messages' ? '#ffffff' : 'var(--text-secondary)',
            fontWeight: 700,
            fontSize: '0.9rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.15s ease',
            boxShadow: activeTab === 'messages' ? '0 4px 14px var(--accent-emerald-glow)' : 'none'
          }}
        >
          <MessageSquare size={16} color={activeTab === 'messages' ? '#ffffff' : 'var(--accent-emerald)'} /> Landlord Messages ({applications.length})
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === 'sent' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {applications.length === 0 && sentRequests.length === 0 ? (
            <div className="glass-card" style={{ padding: '36px 24px', textAlign: 'center', borderRadius: '16px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: 'var(--bg-surface-elevated)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Send size={22} color="var(--accent-emerald)" />
              </div>
              <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.94rem', fontWeight: 600 }}>No outgoing requests or applications submitted yet.</p>
            </div>
          ) : (
            [...applications.map(app => ({
              id: app.id,
              type: 'PROPERTY_APPLICATION',
              title: app.listing_detail?.title || 'Property Application',
              location: app.listing_detail?.city || 'San Francisco',
              price: app.listing_detail?.price,
              status: app.status,
              submittedAt: app.created_at ? app.created_at.split('T')[0] : 'Recent'
            })), ...sentRequests].map((req) => (
              <div key={req.id} className="glass-card" style={{ padding: '24px', borderRadius: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: '18px', alignItems: 'center' }}>
                  <div style={{ width: '46px', height: '46px', borderRadius: '12px', background: 'rgba(5, 150, 105, 0.1)', border: '1px solid rgba(5, 150, 105, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {req.type === 'PROPERTY_APPLICATION' ? <Home color="var(--accent-emerald)" size={22} /> : <User color="var(--accent-emerald)" size={22} />}
                  </div>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>{req.title}</h3>
                    <p style={{ margin: '4px 0 0', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                      Location: {req.location} {req.price ? `• $${req.price}/mo` : ''} • Submitted: {req.submittedAt}
                    </p>
                  </div>
                </div>
                <div>
                  {getStatusBadge(req.status)}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'received' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {receivedRequests.length === 0 ? (
            <div className="glass-card" style={{ padding: '36px 24px', textAlign: 'center', borderRadius: '16px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: 'var(--bg-surface-elevated)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Inbox size={22} color="var(--accent-emerald)" />
              </div>
              <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.94rem', fontWeight: 600 }}>No incoming requests received yet.</p>
            </div>
          ) : (
            receivedRequests.map((req) => (
              <div key={req.id} className="glass-card" style={{ padding: '24px', borderRadius: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: '18px', alignItems: 'center' }}>
                  <div style={{ width: '46px', height: '46px', borderRadius: '12px', background: 'rgba(5, 150, 105, 0.1)', border: '1px solid rgba(5, 150, 105, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <User color="var(--accent-emerald)" size={22} />
                  </div>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>{req.title}</h3>
                    <p style={{ margin: '4px 0 0', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                      From: <strong style={{ color: 'var(--text-primary)' }}>{req.sender}</strong> • {req.location} • Received: {req.receivedAt}
                    </p>
                    {req.notes && <p style={{ margin: '6px 0 0', color: 'var(--text-secondary)', fontSize: '0.85rem', fontStyle: 'italic' }}>"{req.notes}"</p>}
                  </div>
                </div>

                <div>
                  {getStatusBadge(req.status)}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'messages' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {applications.length === 0 ? (
            <div className="glass-card" style={{ padding: '36px 24px', textAlign: 'center', borderRadius: '16px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: 'var(--bg-surface-elevated)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <MessageSquare size={22} color="var(--accent-emerald)" />
              </div>
              <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.94rem', fontWeight: 600 }}>No landlord conversations yet. Submit an application or inquiry on a listing to open a chat!</p>
            </div>
          ) : (
            applications.map((app) => {
              const listingObj = app.listing_detail || { title: 'Property Listing', city: 'San Francisco', price: 2500 };
              const landlordName = app.listing_detail?.owner?.username || app.listing_detail?.owner?.first_name || 'Property Manager';

              return (
                <div
                  key={app.id}
                  className="glass-card-interactive"
                  style={{
                    padding: '24px',
                    borderRadius: '16px',
                    display: 'flex',
                    justify: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer'
                  }}
                  onClick={() => setSelectedChatListing(listingObj)}
                >
                  <div style={{ display: 'flex', gap: '18px', alignItems: 'center' }}>
                    <div style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '12px',
                      background: 'rgba(5, 150, 105, 0.1)',
                      border: '1px solid rgba(5, 150, 105, 0.3)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'var(--accent-emerald)',
                      flexShrink: 0
                    }}>
                      <Building2 size={24} />
                    </div>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>{listingObj.title}</h3>
                      </div>
                      <p style={{ margin: '4px 0 0', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                        Landlord: <strong style={{ color: 'var(--text-primary)' }}>{landlordName}</strong> • {listingObj.city} • ${listingObj.price}/mo
                      </p>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <button
                      className="btn-emerald"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedChatListing(listingObj);
                      }}
                      style={{
                        padding: '10px 18px',
                        borderRadius: '8px',
                        fontSize: '0.88rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontWeight: 700
                      }}
                    >
                      <MessageSquare size={16} /> Open Chat
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Landlord Tenant Chat Modal */}
      {selectedChatListing && (
        <LandlordTenantChatModal
          listing={selectedChatListing}
          isOpen={Boolean(selectedChatListing)}
          onClose={() => setSelectedChatListing(null)}
        />
      )}
    </div>
  );
};
