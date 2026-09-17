import React, { useState, useContext } from 'react';
import { X, MapPin, Bed, Bath, DollarSign, Star, CheckCircle, MessageSquare, Send } from 'lucide-react';
import { CompatibilityBadge } from './CompatibilityBadge';
import { LandlordTenantChatModal } from './LandlordTenantChatModal';
import { AuthContext } from '../context/AuthContext';
import { createApplicationApi } from '../services/api';

const initialReviews = [];

export const ListingDetailModal = ({ listing, isOpen, onClose }) => {
    const { addSentRequest, user } = useContext(AuthContext);
    const [reviews, setReviews] = useState(initialReviews);
    const [newComment, setNewComment] = useState('');
    const [newRating, setNewRating] = useState(5);
    const [applied, setApplied] = useState(false);
    const [submittingApp, setSubmittingApp] = useState(false);
    const [isChatOpen, setIsChatOpen] = useState(false);

    if (!isOpen || !listing) return null;

    const handleApply = async () => {
        setSubmittingApp(true);
        try {
            if (listing.id && !String(listing.id).startsWith('landlord-prop') && !String(listing.id).startsWith('prop-')) {
                await createApplicationApi({
                    listing: listing.id,
                    move_in_date: new Date(Date.now() + 86400000 * 14).toISOString().split('T')[0],
                    notes: 'Submitted via StayMatch housing portal.'
                });
            }
        } catch (e) {
            console.warn('Backend application create fallback to context state:', e);
        } finally {
            addSentRequest({
                id: `req-${Date.now()}`,
                type: "PROPERTY_APPLICATION",
                title: listing.title,
                location: `${listing.city}, ${listing.state || 'CA'}`,
                price: listing.price,
                status: "PENDING",
                submittedAt: new Date().toISOString().split('T')[0],
                recipient: listing.owner?.email || "landlord@staymatch.com"
            });
            setApplied(true);
            setSubmittingApp(false);
        }
    };

    const handleAddReview = (e) => {
        e.preventDefault();
        if (!newComment.trim()) return;
        const rev = {
            id: `rev-${Date.now()}`,
            author: user?.name || user?.username || 'Verified Resident',
            rating: newRating,
            date: 'Just now',
            comment: newComment.trim()
        };
        setReviews([rev, ...reviews]);
        setNewComment('');
    };

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            backdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
        }}>
            <div className="glass-panel" style={{
                width: '100%',
                maxWidth: '680px',
                maxHeight: '90vh',
                overflowY: 'auto',
                padding: '32px',
                borderRadius: '20px',
                position: 'relative',
                background: '#1a1d24'
            }}>
                <button
                    onClick={onClose}
                    style={{
                        position: 'absolute',
                        top: '20px',
                        right: '20px',
                        background: 'rgba(255, 255, 255, 0.1)',
                        border: 'none',
                        color: 'white',
                        borderRadius: '50%',
                        width: '36px',
                        height: '36px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        zIndex: 10
                    }}
                >
                    <X size={20} />
                </button>

                {/* Image Banner Header */}
                <div style={{
                    width: '100%',
                    height: '220px',
                    borderRadius: '16px',
                    background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                    marginBottom: '20px',
                    display: 'flex',
                    alignItems: 'flex-end',
                    justifyContent: 'space-between',
                    padding: '16px'
                }}>
                    <CompatibilityBadge score={listing.score || 94} />
                    <span style={{ background: 'rgba(0, 0, 0, 0.6)', padding: '6px 12px', borderRadius: '20px', color: 'white', fontSize: '0.85rem', fontWeight: 600 }}>
                        Verified Listing
                    </span>
                </div>

                {/* Title & Location */}
                <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: 'white', margin: '0 0 8px' }}>
                    {listing.title}
                </h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '20px' }}>
                    <MapPin size={18} color="#3b82f6" /> {listing.address ? `${listing.address}, ` : ''}{listing.city}, {listing.state || 'CA'}
                </p>

                {/* Key Metrics */}
                <div style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid var(--border-color)',
                    padding: '16px 24px',
                    borderRadius: '14px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '24px'
                }}>
                    <div style={{ display: 'flex', gap: '24px', color: 'white' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><Bed size={18} color="#3b82f6" /> <strong>{listing.bedrooms}</strong> Bedrooms</span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><Bath size={18} color="#8b5cf6" /> <strong>{listing.bathrooms}</strong> Bathrooms</span>
                    </div>
                    <div>
                        <span style={{ fontSize: '1.6rem', fontWeight: 800, color: '#10b981' }}>${listing.price}<small style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>/mo</small></span>
                    </div>
                </div>

                {/* Description */}
                <div style={{ marginBottom: '24px' }}>
                    <h4 style={{ color: 'white', margin: '0 0 8px', fontSize: '1.1rem' }}>Description</h4>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', lineHeight: '1.6', margin: 0 }}>
                        {listing.description || 'Modern sunny studio apartment featuring updated appliances, floor-to-ceiling windows, high-speed fiber internet, and access to luxury building amenities.'}
                    </p>
                </div>

                {/* Amenities */}
                <div style={{ marginBottom: '28px' }}>
                    <h4 style={{ color: 'white', margin: '0 0 12px', fontSize: '1.1rem' }}>Building Amenities</h4>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                        {['Gym & Fitness', 'Rooftop Pool', '24/7 Security', 'In-unit Laundry', 'High-speed Fiber WiFi', 'Pet Friendly'].map((amenity, idx) => (
                            <span key={idx} style={{ padding: '6px 14px', borderRadius: '20px', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', color: '#60a5fa', fontSize: '0.85rem', fontWeight: 600 }}>
                                ✓ {amenity}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Reviews & Ratings Section */}
                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '24px', marginBottom: '24px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                        <h4 style={{ color: 'white', margin: 0, fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <MessageSquare size={20} color="#f59e0b" /> Tenant Reviews & Ratings ({reviews.length})
                        </h4>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#f59e0b', fontWeight: 700 }}>
                            <Star size={18} fill="#f59e0b" /> 4.8 / 5.0
                        </div>
                    </div>

                    {/* Add Review Form */}
                    <form onSubmit={handleAddReview} style={{ marginBottom: '20px', background: 'rgba(255, 255, 255, 0.03)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Write a review for this property</span>
                            <select
                                value={newRating}
                                onChange={(e) => setNewRating(Number(e.target.value))}
                                style={{ background: '#252932', color: 'white', border: '1px solid var(--border-color)', padding: '4px 8px', borderRadius: '6px', fontSize: '0.85rem' }}
                            >
                                <option value={5}>5 Stars ⭐⭐⭐⭐⭐</option>
                                <option value={4}>4 Stars ⭐⭐⭐⭐</option>
                                <option value={3}>3 Stars ⭐⭐⭐</option>
                            </select>
                        </div>
                        <div style={{ display: 'flex', gap: '10px' }}>
                            <input
                                type="text"
                                value={newComment}
                                onChange={(e) => setNewComment(e.target.value)}
                                placeholder="Share your feedback..."
                                style={{ flex: 1, padding: '10px 14px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.9rem' }}
                            />
                            <button className="btn-secondary" type="submit" style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '10px 16px' }}>
                                <Send size={16} /> Post
                            </button>
                        </div>
                    </form>

                    {/* Reviews List */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {reviews.map((rev) => (
                            <div key={rev.id} style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '14px 16px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                                    <strong style={{ color: 'white', fontSize: '0.95rem' }}>{rev.author}</strong>
                                    <div style={{ display: 'flex', gap: '2px', color: '#f59e0b' }}>
                                        {[...Array(rev.rating)].map((_, i) => <Star key={i} size={14} fill="#f59e0b" />)}
                                    </div>
                                </div>
                                <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.88rem' }}>"{rev.comment}"</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Actions: Message Landlord & Submit Application */}
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button
                        onClick={() => setIsChatOpen(true)}
                        style={{
                            flex: 1,
                            padding: '14px',
                            borderRadius: '12px',
                            background: 'rgba(59, 130, 246, 0.15)',
                            border: '1px solid rgba(59, 130, 246, 0.4)',
                            color: '#60a5fa',
                            fontWeight: 700,
                            fontSize: '0.98rem',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px',
                            cursor: 'pointer',
                            transition: 'all 0.2s ease'
                        }}
                    >
                        <MessageSquare size={18} /> Message Landlord
                    </button>

                    {applied ? (
                        <div style={{
                            flex: 1,
                            padding: '14px',
                            background: 'rgba(16, 185, 129, 0.15)',
                            border: '1px solid rgba(16, 185, 129, 0.4)',
                            color: '#10b981',
                            borderRadius: '12px',
                            textAlign: 'center',
                            fontWeight: 700,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px'
                        }}>
                            <CheckCircle size={20} /> Application Submitted!
                        </div>
                    ) : (
                        <button
                            onClick={handleApply}
                            className="btn-primary"
                            style={{
                                flex: 1,
                                padding: '14px',
                                borderRadius: '12px',
                                fontWeight: 700,
                                fontSize: '0.98rem'
                            }}
                        >
                            Submit Application
                        </button>
                    )}
                </div>
            </div>

            {/* Landlord Tenant Chat Modal */}
            <LandlordTenantChatModal
                listing={listing}
                isOpen={isChatOpen}
                onClose={() => setIsChatOpen(false)}
            />
        </div>
    );
};
