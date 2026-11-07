import React, { useState, useEffect, useRef, useContext } from 'react';
import { X, Send, Building2, ShieldCheck, MapPin, DollarSign, CheckCheck, Clock, Calendar, Phone, Mail, Wifi } from 'lucide-react';
import { useWebSocketChat } from '../hooks/useWebSocketChat';
import { AuthContext } from '../context/AuthContext';

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export const LandlordTenantChatModal = ({ listing, isOpen, onClose, initialMessage = '' }) => {
  const { user } = useContext(AuthContext);
  // A conversation is private to one tenant and the listing's owner. The landlord's screens pass the
  // applicant's id as listing.chatTenantId; a tenant is always themselves. Listings without real ids
  // (demo data) get no live room and stay local-only.
  const landlordView = Boolean(listing?.chatTenantId);
  const tenantId = listing?.chatTenantId || (user?.id && user.id !== listing?.owner?.id ? user.id : null);
  const roomId = listing && UUID.test(String(listing.id)) && UUID.test(String(tenantId))
    ? `listing.${String(listing.id).toLowerCase()}.${String(tenantId).toLowerCase()}`
    : null;
  const { messages, setMessages, isConnected, sendMessage } = useWebSocketChat(
    roomId,
    listing ? [
      {
        id: 1,
        sender: 'landlord',
        text: `Hello! I'm the property manager for "${listing.title || 'this property'}". Feel free to ask any questions regarding tours, move-in dates, or lease terms!`,
        timestamp: 'Just now'
      },
      ...(initialMessage ? [{
        id: 2,
        sender: 'user',
        text: initialMessage,
        timestamp: 'Just now'
      }] : [])
    ] : [],
    { selfId: user?.id, otherSender: landlordView ? 'tenant' : 'landlord' }
  );

  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const quickInquiries = [
    "Is this property available for immediate move-in?",
    "Can I schedule an in-person or virtual tour this week?",
    "Are utilities and parking included in the monthly rent?",
    "What are the lease term options and deposit requirements?"
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!isOpen || !listing) return null;

  const handleSendMessage = (textToSend) => {
    const text = textToSend || inputText;
    if (!text.trim()) return;

    sendMessage(text, 'user', 'Tenant');
    if (!textToSend) setInputText('');
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      backgroundColor: 'rgba(10, 12, 18, 0.85)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1050
    }}>
      <div className="glass-panel" style={{
        width: '92%',
        maxWidth: '580px',
        height: '640px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: '20px',
        position: 'relative',
        background: '#ffffff',
        border: '1px solid var(--border-color)',
        boxShadow: 'var(--shadow-lg)',
        overflow: 'hidden'
      }}>
        {/* Landlord Header */}
        <div style={{
          padding: '16px 20px',
          background: '#f8fafc',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{ position: 'relative' }}>
              <div style={{
                width: '46px',
                height: '46px',
                borderRadius: '12px',
                background: 'var(--accent-emerald)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white'
              }}>
                <Building2 size={24} />
              </div>
              <div style={{
                position: 'absolute',
                bottom: -2,
                right: -2,
                width: '14px',
                height: '14px',
                borderRadius: '50%',
                background: '#10b981',
                border: '2px solid #ffffff'
              }} title="Landlord Online" />
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h4 style={{ margin: 0, color: 'var(--text-primary)', fontSize: '1.05rem', fontWeight: 700 }}>
                  Landlord Property Chat
                </h4>
                <span style={{ padding: '2px 8px', borderRadius: '10px', background: 'rgba(5, 150, 105, 0.1)', color: 'var(--accent-emerald)', fontSize: '0.75rem', fontWeight: 700, border: '1px solid rgba(5, 150, 105, 0.25)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <ShieldCheck size={12} /> Verified Landlord
                </span>
              </div>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
                {listing.owner?.first_name ? `${listing.owner.first_name} ${listing.owner.last_name || ''}` : listing.owner?.username || listing.owner?.email || 'Property Owner'} • Verified Landlord
              </span>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: '#f1f5f9',
              border: '1px solid var(--border-color)',
              borderRadius: '50%',
              width: '36px',
              height: '36px',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s ease'
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Property Context Bar */}
        <div style={{
          padding: '12px 20px',
          background: '#ecfdf5',
          borderBottom: '1px solid rgba(5, 150, 105, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.86rem'
        }}>
          <div>
            <strong style={{ color: 'var(--text-primary)', display: 'block' }}>{listing.title}</strong>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <MapPin size={12} color="var(--accent-emerald)" /> {listing.city}, CA
            </span>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span style={{ color: '#059669', fontWeight: 800, fontSize: '1.05rem' }}>${listing.price}/mo</span>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', display: 'block' }}>{listing.bedrooms} Bed • {listing.bathrooms} Bath</span>
          </div>
        </div>

        {/* Messages List Area */}
        <div style={{
          flex: 1,
          padding: '20px',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '14px',
          background: '#f8fafc'
        }}>
          {messages.map((msg) => {
            const isUser = msg.sender === 'user';
            return (
              <div
                key={msg.id}
                style={{
                  display: 'flex',
                  justifyContent: isUser ? 'flex-end' : 'flex-start',
                  alignItems: 'flex-end',
                  gap: '8px'
                }}
              >
                {!isUser && (
                  <div style={{
                    width: '30px',
                    height: '30px',
                    borderRadius: '8px',
                    background: 'var(--accent-emerald)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    flexShrink: 0
                  }}>
                    <Building2 size={16} />
                  </div>
                )}
                <div style={{
                  maxWidth: '78%',
                  padding: '12px 16px',
                  borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                  background: isUser ? 'linear-gradient(135deg, #059669, #10b981)' : '#ffffff',
                  color: isUser ? '#ffffff' : 'var(--text-primary)',
                  fontSize: '0.92rem',
                  lineHeight: '1.45',
                  border: isUser ? 'none' : '1px solid var(--border-color)',
                  boxShadow: isUser ? '0 4px 12px rgba(5, 150, 105, 0.2)' : 'var(--shadow-sm)'
                }}>
                  <p style={{ margin: 0 }}>{msg.text}</p>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'flex-end',
                    gap: '4px',
                    marginTop: '4px',
                    fontSize: '0.7rem',
                    color: isUser ? 'rgba(255, 255, 255, 0.8)' : 'var(--text-muted)'
                  }}>
                    <span>{msg.timestamp}</span>
                    {isUser && <CheckCheck size={14} color="#a7f3d0" />}
                  </div>
                </div>
              </div>
            );
          })}

          {isTyping && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '0.82rem', padding: '6px 12px' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', border: '2px solid var(--accent-emerald)', borderTopColor: 'transparent', animation: 'spin 1s linear infinite' }} />
              Landlord is typing reply...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Inquiry Chips */}
        <div style={{
          padding: '8px 16px',
          background: '#ffffff',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          gap: '8px',
          overflowX: 'auto',
          scrollbarWidth: 'none'
        }}>
          {quickInquiries.map((inquiry, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSendMessage(inquiry)}
              style={{
                whiteSpace: 'nowrap',
                padding: '6px 12px',
                borderRadius: '16px',
                background: 'rgba(5, 150, 105, 0.1)',
                border: '1px solid rgba(5, 150, 105, 0.25)',
                color: 'var(--accent-emerald)',
                fontSize: '0.78rem',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                flexShrink: 0
              }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(5, 150, 105, 0.2)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(5, 150, 105, 0.1)'; }}
            >
              {inquiry}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          style={{
            padding: '16px 20px',
            background: '#ffffff',
            borderTop: '1px solid var(--border-color)',
            display: 'flex',
            gap: '12px',
            alignItems: 'center'
          }}
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask landlord about move-in, tours, or lease..."
            style={{
              flex: 1,
              padding: '12px 16px',
              borderRadius: '12px',
              background: '#ffffff',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              fontSize: '0.92rem',
              outline: 'none'
            }}
          />
          <button
            type="submit"
            disabled={!inputText.trim()}
            style={{
              padding: '12px 18px',
              borderRadius: '12px',
              background: inputText.trim() ? 'var(--accent-emerald)' : '#e2e8f0',
              border: 'none',
              color: inputText.trim() ? 'white' : 'var(--text-muted)',
              cursor: inputText.trim() ? 'pointer' : 'not-allowed',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              fontWeight: 600,
              fontSize: '0.9rem',
              transition: 'all 0.2s ease'
            }}
          >
            <Send size={16} /> Send
          </button>
        </form>
      </div>
    </div>
  );
};
