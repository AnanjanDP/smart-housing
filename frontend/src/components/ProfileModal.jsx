import React, { useState, useEffect, useContext } from 'react';
import { X, UserCheck, ShieldCheck, Mail, MapPin, DollarSign, Calendar, Sparkles, CheckCircle2, MessageSquare, Heart, Moon, Sun, Briefcase } from 'lucide-react';
import { CompatibilityBadge } from './CompatibilityBadge';
import { AuthContext } from '../context/AuthContext';

export const ProfileModal = ({ roommate, isOpen, onClose, onConnect, onOpenChat }) => {
    const [connected, setConnected] = useState(roommate?.isConnected || false);
    const { addSentRequest } = useContext(AuthContext);

    useEffect(() => {
        if (roommate) {
            setConnected(roommate.isConnected || false);
        }
    }, [roommate]);

    if (!isOpen || !roommate) return null;

    const handleConnect = () => {
        setConnected(true);
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
        if (onConnect) {
            onConnect();
        }
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
            zIndex: 1000
        }}>
            <div className="glass-panel" style={{
                width: '92%',
                maxWidth: '540px',
                padding: '32px',
                borderRadius: '20px',
                position: 'relative',
                background: '#1a1d24',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                boxShadow: '0 20px 50px rgba(0, 0, 0, 0.7)'
            }}>
                <button
                    onClick={onClose}
                    style={{
                        position: 'absolute',
                        top: '20px',
                        right: '20px',
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: 'none',
                        borderRadius: '50%',
                        width: '36px',
                        height: '36px',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}
                >
                    <X size={20} />
                </button>

                {/* Header Profile Info */}
                <div style={{ display: 'flex', gap: '20px', alignItems: 'center', marginBottom: '24px' }}>
                    <div style={{
                        width: '76px',
                        height: '76px',
                        borderRadius: '50%',
                        background: 'var(--accent-gradient)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '1.8rem',
                        fontWeight: 800,
                        color: 'white',
                        overflow: 'hidden',
                        border: '2px solid rgba(255, 255, 255, 0.1)'
                    }}>
                        {roommate.avatar ? (
                            <img src={roommate.avatar} alt={roommate.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        ) : (
                            roommate.name ? roommate.name[0] : 'A'
                        )}
                    </div>
                    <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h3 style={{ margin: 0, fontSize: '1.4rem', fontWeight: 800, color: 'white' }}>
                                {roommate.name || 'Alice Smith'}
                            </h3>
                            <CompatibilityBadge score={roommate.score || 96} />
                        </div>
                        <p style={{ margin: '6px 0 0', color: 'var(--text-muted)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <MapPin size={16} color="#3b82f6" /> {roommate.preferred_location || 'San Francisco, CA'}
                        </p>
                        {connected && (
                            <span style={{ fontSize: '0.78rem', color: '#10b981', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
                                <CheckCircle2 size={14} /> Connected Roommate
                            </span>
                        )}
                    </div>
                </div>

                {/* Key Attributes */}
                <div style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid var(--border-color)',
                    padding: '16px',
                    borderRadius: '12px',
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '16px',
                    marginBottom: '20px'
                }}>
                    <div>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', display: 'block' }}>Monthly Budget</span>
                        <strong style={{ color: '#10b981', fontSize: '1.1rem' }}>
                            ${roommate.budget_min || 1500} - ${roommate.budget_max || 2200}/mo
                        </strong>
                    </div>
                    <div>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', display: 'block' }}>Sleep Schedule</span>
                        <strong style={{ color: 'white', fontSize: '1.1rem' }}>
                            {roommate.sleep_schedule || 'Early Bird'}
                        </strong>
                    </div>
                    <div>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', display: 'block' }}>Cleanliness Rating</span>
                        <strong style={{ color: 'white', fontSize: '1.1rem' }}>
                            {roommate.cleanliness_level ? `${roommate.cleanliness_level}/5 Stars` : '4/5 Stars'}
                        </strong>
                    </div>
                    <div>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', display: 'block' }}>Pet Preference</span>
                        <strong style={{ color: 'white', fontSize: '1.1rem' }}>
                            {roommate.pets_allowed || roommate.pets === 'Pet Friendly' ? 'Pet Friendly 🐶' : 'No Pets 🚫'}
                        </strong>
                    </div>
                </div>

                {/* Dealbreaker Highlights */}
                <div style={{ marginBottom: '20px' }}>
                    <h4 style={{ margin: '0 0 10px', color: 'white', fontSize: '0.95rem', fontWeight: 700 }}>
                        Lifestyle & Dealbreaker Tags
                    </h4>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        <span style={{ padding: '6px 12px', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.15)', color: '#34d399', fontSize: '0.82rem', fontWeight: 600 }}>
                            {roommate.is_smoker === false || roommate.non_smoker !== false ? '🚭 Non-Smoker' : '🚬 Smoker OK'}
                        </span>
                        <span style={{ padding: '6px 12px', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', fontSize: '0.82rem', fontWeight: 600 }}>
                            {roommate.pets_allowed || roommate.pets === 'Pet Friendly' ? '🐶 Pet Friendly' : '🚫 No Pets'}
                        </span>
                        <span style={{ padding: '6px 12px', borderRadius: '8px', background: 'rgba(245, 158, 11, 0.15)', color: '#fcd34d', fontSize: '0.82rem', fontWeight: 600 }}>
                            {roommate.sleep_schedule || '🌅 Early Bird'}
                        </span>
                        <span style={{ padding: '6px 12px', borderRadius: '8px', background: 'rgba(14, 165, 233, 0.15)', color: '#38bdf8', fontSize: '0.82rem', fontWeight: 600 }}>
                            {roommate.work_style === 'WFH' ? '💻 Work From Home' : '🏢 In-Office'}
                        </span>
                    </div>
                </div>

                {/* Bio / Description */}
                <div style={{ marginBottom: '24px' }}>
                    <h4 style={{ margin: '0 0 8px', color: 'white', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Sparkles size={16} color="#8b5cf6" /> About {roommate.name?.split(' ')[0] || 'Roommate'}
                    </h4>
                    <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.95rem', lineHeight: '1.5' }}>
                        {roommate.bio || 'Software professional looking for a clean, friendly roommate in a modern apartment.'}
                    </p>
                </div>

                {/* Actions */}
                {connected ? (
                    <button
                        onClick={() => {
                            if (onOpenChat) onOpenChat();
                            else if (onConnect) onConnect();
                        }}
                        className="btn-primary"
                        style={{
                            width: '100%',
                            padding: '14px',
                            borderRadius: '12px',
                            background: 'linear-gradient(135deg, #10b981, #059669)',
                            border: 'none',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '10px',
                            fontWeight: 700,
                            fontSize: '1rem',
                            cursor: 'pointer'
                        }}
                    >
                        <MessageSquare size={20} /> Open Chat & Message {roommate.name?.split(' ')[0] || 'Roommate'}
                    </button>
                ) : (
                    <button
                        onClick={handleConnect}
                        className="btn-primary"
                        style={{
                            width: '100%',
                            padding: '14px',
                            borderRadius: '12px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '10px',
                            fontWeight: 700,
                            fontSize: '1rem',
                            cursor: 'pointer'
                        }}
                    >
                        <UserCheck size={20} /> Connect & Unlock Chat
                    </button>
                )}
            </div>
        </div>
    );
};
