import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { ListingCard } from '../components/ListingCard';
import { useFetchListings } from '../hooks/useFetchListings';
import { AuthContext } from '../context/AuthContext';
import { Sparkles, ShieldCheck, Zap, ArrowRight, Building2, Users, Search, MessageSquare, Compass } from 'lucide-react';

export const Home = () => {
  const { listings } = useFetchListings();
  const { user, isAuthenticated, landlordListings } = useContext(AuthContext);

  const displayListings = listings.length > 0 ? listings : (landlordListings || []);
  const isLandlord = user?.role === 'LANDLORD';

  return (
    <div style={{ maxWidth: '1360px', margin: '0 auto', padding: '24px 36px 80px' }}>
      
      {/* Editorial Asymmetric Hero Section */}
      <section style={{
        display: 'grid',
        gridTemplateColumns: '1.2fr 0.8fr',
        gap: '48px',
        alignItems: 'center',
        padding: '56px 0 64px',
        borderBottom: '1px solid var(--border-subtle)'
      }}>
        {/* Left Column: Headlines & Action CTA */}
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 14px', borderRadius: '20px', background: 'rgba(5, 150, 105, 0.1)', border: '1px solid rgba(5, 150, 105, 0.25)', marginBottom: '20px' }}>
            <Sparkles size={15} color="var(--accent-emerald)" />
            <span className="kicker-tag" style={{ fontSize: '0.75rem' }}>AI-Powered Housing & Roommate Matching</span>
          </div>

          <h1 style={{
            fontSize: '3.6rem',
            fontWeight: 800,
            lineHeight: 1.08,
            color: 'var(--text-primary)',
            marginBottom: '24px',
            fontFamily: 'var(--font-header)',
            letterSpacing: '-0.03em'
          }}>
            Find Your Next Home. <br />
            <span style={{ color: 'var(--accent-emerald)' }}>Match Compatible Roommates.</span>
          </h1>

          <p style={{ color: 'var(--text-secondary)', fontSize: '1.12rem', lineHeight: 1.65, maxWidth: '580px', marginBottom: '36px' }}>
            StayMatch connects verified housing listings with AI compatibility algorithms. Search by budget, sleep schedule, dealbreaker preferences, and location proximity.
          </p>

          {/* Action CTAs */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap', marginBottom: '40px' }}>
            {isAuthenticated ? (
              <Link to="/listings" className="btn-emerald" style={{ textDecoration: 'none', padding: '14px 28px', fontSize: '0.98rem' }}>
                <Search size={18} /> Explore Verified Listings <ArrowRight size={16} />
              </Link>
            ) : (
              <Link to="/listings" className="btn-emerald" style={{ textDecoration: 'none', padding: '14px 28px', fontSize: '0.98rem' }}>
                <Compass size={18} /> Browse Properties <ArrowRight size={16} />
              </Link>
            )}

            <Link to="/roommates" className="btn-secondary" style={{ textDecoration: 'none', padding: '14px 24px', fontSize: '0.94rem' }}>
              <Users size={18} color="var(--accent-emerald)" /> Find Roommates
            </Link>
          </div>
        </div>

        {/* Right Column: Hero Preview Card */}
        <div>
          <div className="glass-panel" style={{ padding: '32px', position: 'relative', overflow: 'hidden', background: 'var(--bg-surface)', boxShadow: 'var(--shadow-md)' }}>
            <div style={{ position: 'absolute', top: '-40px', right: '-40px', width: '200px', height: '200px', background: 'var(--accent-emerald-glow)', filter: 'blur(60px)', pointerEvents: 'none' }} />
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <span className="badge-emerald">Live AI Engine Active</span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>San Francisco, CA</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '24px' }}>
              <div style={{ padding: '16px', borderRadius: '14px', background: 'var(--bg-surface-elevated)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '14px' }}>
                <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'rgba(5, 150, 105, 0.12)', border: '1px solid rgba(5, 150, 105, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-emerald)', fontWeight: 800 }}>
                  96%
                </div>
                <div>
                  <h4 style={{ margin: 0, fontSize: '0.98rem', color: 'var(--text-primary)', fontWeight: 700 }}>High Compatibility Match</h4>
                  <p style={{ margin: '2px 0 0', fontSize: '0.82rem', color: 'var(--text-muted)' }}>Budget overlap $1,800/mo • Early Bird • Non-Smoker</p>
                </div>
              </div>

              <div style={{ padding: '16px', borderRadius: '14px', background: 'var(--bg-surface-elevated)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '14px' }}>
                <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'rgba(2, 132, 199, 0.12)', border: '1px solid rgba(2, 132, 199, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-sky)' }}>
                  <Building2 size={20} />
                </div>
                <div>
                  <h4 style={{ margin: 0, fontSize: '0.98rem', color: 'var(--text-primary)', fontWeight: 700 }}>Verified Landlord Listings</h4>
                  <p style={{ margin: '2px 0 0', fontSize: '0.82rem', color: 'var(--text-muted)' }}>Direct landlord applications & in-app WebSocket chat</p>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '16px', borderTop: '1px solid var(--border-color)', fontSize: '0.84rem', color: 'var(--text-muted)' }}>
              <span>✓ Instant Identity Verification</span>
              <span>✓ Zero Spam Policy</span>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Pillar Architecture Grid */}
      <section style={{ padding: '64px 0', borderBottom: '1px solid var(--border-subtle)' }}>
        <div style={{ marginBottom: '44px', textAlign: 'center' }}>
          <h2 style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--text-primary)', margin: '0 0 12px', fontFamily: 'Syne, sans-serif', letterSpacing: '-0.02em' }}>
            What StayMatch Delivers to You
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.02rem', margin: '0 auto', maxWidth: '640px', lineHeight: 1.6 }}>
            Everything you need to discover verified apartments, connect with compatible roommates, and deal directly with property owners.
          </p>
        </div>

        <div className="home-features-grid">
          
          <div className="glass-card-interactive" style={{ padding: '32px', borderRadius: '16px' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'rgba(5, 150, 105, 0.12)', border: '1px solid rgba(5, 150, 105, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-emerald)', marginBottom: '20px' }}>
              <Zap size={22} />
            </div>
            <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', fontWeight: 800, margin: '0 0 10px', fontFamily: 'Syne, sans-serif' }}>Smart Property Search</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.65, margin: 0 }}>
              Find verified apartments and studios tailored to your budget, target neighborhood, and required amenities in seconds.
            </p>
          </div>

          <div className="glass-card-interactive" style={{ padding: '32px', borderRadius: '16px' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'rgba(217, 119, 6, 0.12)', border: '1px solid rgba(217, 119, 6, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-amber)', marginBottom: '20px' }}>
              <Users size={22} />
            </div>
            <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', fontWeight: 800, margin: '0 0 10px', fontFamily: 'Syne, sans-serif' }}>Lifestyle Roommate Match</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.65, margin: 0 }}>
              Connect with compatible roommates based on sleep habits, cleanliness standards, pet friendliness, and work styles.
            </p>
          </div>

          <div className="glass-card-interactive" style={{ padding: '32px', borderRadius: '16px' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'rgba(2, 132, 199, 0.12)', border: '1px solid rgba(2, 132, 199, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-sky)', marginBottom: '20px' }}>
              <MessageSquare size={22} />
            </div>
            <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', fontWeight: 800, margin: '0 0 10px', fontFamily: 'Syne, sans-serif' }}>Direct Landlord Messaging</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.65, margin: 0 }}>
              Chat directly with verified property managers, schedule in-person or virtual tours, and submit rental applications.
            </p>
          </div>

          <div className="glass-card-interactive" style={{ padding: '32px', borderRadius: '16px' }}>
            <div style={{ width: '44px', height: '44px', borderRadius: '12px', background: 'rgba(225, 29, 72, 0.12)', border: '1px solid rgba(225, 29, 72, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-rose)', marginBottom: '20px' }}>
              <ShieldCheck size={22} />
            </div>
            <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', fontWeight: 800, margin: '0 0 10px', fontFamily: 'Syne, sans-serif' }}>Instant Status Updates</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.65, margin: 0 }}>
              Receive instant email and in-app notifications when your application is reviewed or when a new roommate match appears.
            </p>
          </div>

        </div>
      </section>

      {/* Featured Properties Showcase Section */}
      <section style={{ padding: '64px 0 0' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <h2 style={{ fontSize: '1.8rem', fontWeight: 800, margin: '0 0 6px', color: 'var(--text-primary)', fontFamily: 'var(--font-header)' }}>
              Active Properties
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', margin: 0 }}>
              Explore recently verified listings available for immediate occupancy.
            </p>
          </div>

          {displayListings.length > 0 && (
            <Link to="/listings" style={{ color: 'var(--accent-emerald)', textDecoration: 'none', fontWeight: 700, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
              View All Properties ({displayListings.length}) <ArrowRight size={16} />
            </Link>
          )}
        </div>

        {displayListings.length === 0 ? (
          <div className="glass-panel" style={{ padding: '56px 24px', textAlign: 'center', borderRadius: '20px' }}>
            <div style={{ width: '60px', height: '60px', borderRadius: '16px', background: 'var(--bg-surface-elevated)', border: '1px solid var(--border-color)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
              <Building2 size={30} color="var(--accent-emerald)" />
            </div>
            <h3 style={{ color: 'var(--text-primary)', fontSize: '1.3rem', fontWeight: 800, margin: '0 0 8px', fontFamily: 'Syne, sans-serif' }}>No Active Listings Yet</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.94rem', maxWidth: '480px', margin: '0 auto 24px', lineHeight: 1.6 }}>
              Be the first property owner to post a listing or discover verified roommate matches in your area.
            </p>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '14px', flexWrap: 'wrap' }}>
              <Link to="/listings" className="btn-emerald" style={{ textDecoration: 'none', padding: '12px 24px', fontSize: '0.92rem' }}>
                <Compass size={18} /> Browse All Properties <ArrowRight size={16} />
              </Link>
              <Link to={isLandlord ? "/mydashboard" : "/roommates"} className="btn-secondary" style={{ textDecoration: 'none', padding: '12px 24px', fontSize: '0.92rem' }}>
                {isLandlord ? <Building2 size={18} color="var(--accent-sky)" /> : <Users size={18} color="var(--accent-emerald)" />}
                {isLandlord ? "Post Property Listing" : "Explore Roommates"}
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid-listings">
            {displayListings.slice(0, 6).map((item) => (
              <ListingCard key={item.id} listing={item} />
            ))}
          </div>
        )}
      </section>

    </div>
  );
};
