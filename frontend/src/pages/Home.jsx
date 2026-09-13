import React from 'react';
import { SearchBar } from '../components/SearchBar';
import { ListingCard } from '../components/ListingCard';
import { RoommateCard } from '../components/RoommateCard';
import { useFetchListings } from '../hooks/useFetchListings';
import { Sparkles, Shield, Zap } from 'lucide-react';

export const Home = () => {
  const { listings } = useFetchListings();

  return (
    <div style={{ padding: '0 32px 64px 32px' }}>
      {/* Hero Section */}
      <section style={{ textAlign: 'center', padding: '64px 0 48px 0' }}>
        <h1 style={{ fontSize: '3.5rem', fontWeight: 800, marginBottom: '16px', lineHeight: 1.2 }}>
          Find Your Perfect Stay & <br />
          <span className="gradient-text">Compatible Roommate</span>
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto 36px auto' }}>
          AI-driven vector search and multi-factor compatibility scoring for modern, hassle-free smart housing.
        </p>
        <SearchBar />
      </section>

      {/* Featured Listings Section */}
      <section style={{ marginTop: '48px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 700 }}>Featured AI Recommendations</h2>
          <span style={{ color: 'var(--accent-cyan)', cursor: 'pointer', fontWeight: 600 }}>Explore All &rarr;</span>
        </div>
        <div className="grid-layout">
          {listings.map((item) => (
            <ListingCard key={item.id} listing={item} />
          ))}
        </div>
      </section>

      {/* Roommates Compatibility Section */}
      <section style={{ marginTop: '64px' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '24px' }}>Top Roommate Matches Near You</h2>
        <div className="grid-layout">
          <RoommateCard roommate={{ name: 'Sarah Connor', preferred_location: 'San Francisco, CA', budget_min: 1600, budget_max: 2300, sleep_schedule: 'Early Bird', score: 98 }} />
          <RoommateCard roommate={{ name: 'David Miller', preferred_location: 'Palo Alto, CA', budget_min: 1400, budget_max: 2000, sleep_schedule: 'Flexible', score: 91 }} />
        </div>
      </section>
    </div>
  );
};
