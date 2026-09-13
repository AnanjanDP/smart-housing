import React from 'react';
import { ListingCard } from '../components/ListingCard';
import { useFetchListings } from '../hooks/useFetchListings';

export const ListingsPage = () => {
  const { listings } = useFetchListings();

  return (
    <div style={{ padding: '32px' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '24px' }}>All Verified Housing Listings</h1>
      <div className="grid-layout">
        {listings.map((item) => (
          <ListingCard key={item.id} listing={item} />
        ))}
      </div>
    </div>
  );
};
