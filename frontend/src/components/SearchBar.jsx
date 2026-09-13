import React, { useState } from 'react';
import { Search, MapPin, SlidersHorizontal } from 'lucide-react';

export const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) onSearch(query);
  };

  return (
    <form onSubmit={handleSubmit} className="glass-panel" style={{ padding: '12px 20px', display: 'flex', alignItems: 'center', gap: '16px', maxWidth: '800px', margin: '0 auto' }}>
      <Search color="var(--accent-primary)" size={24} />
      <input
        type="text"
        placeholder="Search by location, amenities, or 'sunny 1BR near tech park'..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{
          flex: 1,
          background: 'transparent',
          border: 'none',
          outline: 'none',
          color: 'white',
          fontSize: '1rem'
        }}
      />
      <button type="submit" className="btn-primary">Search</button>
    </form>
  );
};
