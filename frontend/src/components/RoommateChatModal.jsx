import React, { useState, useEffect, useRef } from 'react';
import { X, Send, Sparkles, CheckCheck, MessageSquare, ShieldCheck, MapPin, Calendar, Clock, Wifi } from 'lucide-react';
import { CompatibilityBadge } from './CompatibilityBadge';
import { useWebSocketChat } from '../hooks/useWebSocketChat';

export const RoommateChatModal = ({ roommate, isOpen, onClose }) => {
  const roomId = roommate ? `roommate-${roommate.id}` : 'roommate-general';
  const { messages, setMessages, isConnected, sendMessage } = useWebSocketChat(
    roomId,
    roommate ? [{
      id: 1,
      sender: 'roommate',
      text: `Hey there! Thanks for connecting. I'm looking for a compatible roommate in ${roommate.preferred_location || 'San Francisco, CA'}.`,
      timestamp: 'Just now'
    }] : []
  );

  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const quickReplies = [
    "Hi! When is your target move-in date?",
    "Hey! Are you looking in Downtown SF or nearby?",
    "Hi! What is your maximum monthly budget?",
    "Hey! Let's schedule a quick call to connect!"
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!isOpen || !roommate) return null;

  const handleSendMessage = (textToSend) => {
    const text = textToSend || inputText;
    if (!text.trim()) return;

    sendMessage(text, 'user', 'Me');
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
        maxWidth: '560px',
        height: '620px',
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
        {/* Chat Header */}
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
                borderRadius: '50%',
                background: 'var(--accent-emerald)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.2rem',
                fontWeight: 800,
                color: 'white'
              }}>
                {roommate.name ? roommate.name[0] : 'R'}
              </div>
              <div style={{
                position: 'absolute',
                bottom: 0,
                right: 0,
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                background: '#10b981',
                border: '2px solid #ffffff'
              }} title="Online" />
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h4 style={{ margin: 0, color: 'var(--text-primary)', fontSize: '1.05rem', fontWeight: 700 }}>
                  {roommate.name || 'Roommate Match'}
                </h4>
                <CompatibilityBadge score={roommate.score || 95} />
              </div>
              <span style={{ fontSize: '0.8rem', color: isConnected ? '#059669' : '#d97706', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: isConnected ? '#059669' : '#d97706', display: 'inline-block' }}></span>
                {isConnected ? '⚡ Live WebSocket Active' : 'Connecting WebSocket...'}
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

        {/* Roommate Info Banner */}
        <div style={{
          padding: '10px 20px',
          background: '#ecfdf5',
          borderBottom: '1px solid rgba(5, 150, 105, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.82rem',
          color: '#047857'
        }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MapPin size={14} /> {roommate.preferred_location || 'San Francisco'}
          </span>
          <span style={{ fontWeight: 600 }}>
            Budget: ${roommate.budget_min || 1500} - ${roommate.budget_max || 2200}/mo
          </span>
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
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    background: 'var(--accent-emerald)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: 'white',
                    flexShrink: 0
                  }}>
                    {roommate.name ? roommate.name[0] : 'R'}
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
              {roommate.name?.split(' ')[0] || 'Roommate'} is typing...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestion Chips */}
        <div style={{
          padding: '8px 16px',
          background: '#ffffff',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          gap: '8px',
          overflowX: 'auto',
          scrollbarWidth: 'none'
        }}>
          {quickReplies.map((reply, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSendMessage(reply)}
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
              {reply}
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
            placeholder={`Message ${roommate.name?.split(' ')[0] || 'roommate'}...`}
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
