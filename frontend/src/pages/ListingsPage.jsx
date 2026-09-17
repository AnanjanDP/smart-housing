import React, { useState, useEffect, useContext } from 'react';
import { ListingCard } from '../components/ListingCard';
import { useFetchListings } from '../hooks/useFetchListings';
import { AuthContext } from '../context/AuthContext';
import { Search, MapPin, SlidersHorizontal, Navigation, DollarSign, Bed, Bath, Sparkles, Filter, X, ArrowUpDown } from 'lucide-react';

const cityCoordinates = {
  'san francisco': { lat: 37.7749, lon: -122.4194 },
  'palo alto': { lat: 37.4419, lon: -122.1430 },
  'san jose': { lat: 37.3382, lon: -121.8863 },
  'berkeley': { lat: 37.8715, lon: -122.2730 },
  'oakland': { lat: 37.8044, lon: -122.2712 }
};

const calculateDistanceKm = (lat1, lon1, lat2, lon2) => {
  if (!lat1 || !lon1 || !lat2 || !lon2) return null;
  const R = 6371; // Earth radius in km
  const dLat = (lat2 - lat1) * (Math.PI / 180);
  const dLon = (lon2 - lon1) * (Math.PI / 180);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c * 10) / 10;
};

export const ListingsPage = () => {
  const { listings: apiListings } = useFetchListings();
  const { landlordListings } = useContext(AuthContext);

  // Combine API listings and Landlord created listings
  const allListings = [...(landlordListings || []), ...(apiListings || [])];

  // Search & Filter State
  const [searchTerm, setSearchTerm] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [bedrooms, setBedrooms] = useState('ALL');
  const [bathrooms, setBathrooms] = useState('ALL');
  const [propertyType, setPropertyType] = useState('ALL');
  const [selectedAmenities, setSelectedAmenities] = useState([]);
  const [sortBy, setSortBy] = useState('recommended'); // 'recommended', 'price_asc', 'price_desc', 'distance'

  // Geolocation API State
  const [userCoords, setUserCoords] = useState(null);
  const [geoStatus, setGeoStatus] = useState('');
  const [isGettingGeo, setIsGettingGeo] = useState(false);

  const availableAmenities = [
    'WiFi',
    'Parking',
    'Air Conditioning',
    'Laundry',
    'Gym',
    'Pet Friendly',
    'Balcony',
    'Swimming Pool',
    'Couples Allowed',
    'Bachelor Friendly',
    '24/7 Security',
    'Smoke Alarm'
  ];

  // Geolocation API Handler
  const handleGetLocation = () => {
    if (!navigator.geolocation) {
      setGeoStatus('Geolocation is not supported by your browser.');
      return;
    }

    setIsGettingGeo(true);
    setGeoStatus('Fetching location...');

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const coords = {
          lat: position.coords.latitude,
          lon: position.coords.longitude
        };
        setUserCoords(coords);
        setGeoStatus(`📍 Location acquired (${coords.lat.toFixed(2)}°, ${coords.lon.toFixed(2)}°)`);
        setSortBy('distance');
        setIsGettingGeo(false);
      },
      (error) => {
        console.warn('Geolocation error:', error);
        setGeoStatus('Unable to retrieve location. Using default city search.');
        setIsGettingGeo(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const toggleAmenity = (amenity) => {
    if (selectedAmenities.includes(amenity)) {
      setSelectedAmenities(selectedAmenities.filter(a => a !== amenity));
    } else {
      setSelectedAmenities([...selectedAmenities, amenity]);
    }
  };

  const resetFilters = () => {
    setSearchTerm('');
    setMinPrice('');
    setMaxPrice('');
    setBedrooms('ALL');
    setBathrooms('ALL');
    setPropertyType('ALL');
    setSelectedAmenities([]);
    setSortBy('recommended');
  };

  // Filter Logic
  const filteredListings = allListings.map(item => {
    // Determine property coordinates
    let propLat = item.latitude;
    let propLon = item.longitude;
    if (!propLat || !propLon) {
      const cityKey = item.city?.toLowerCase();
      const matchedCoords = cityCoordinates[cityKey] || cityCoordinates['san francisco'];
      propLat = matchedCoords.lat;
      propLon = matchedCoords.lon;
    }

    let distance = null;
    if (userCoords) {
      distance = calculateDistanceKm(userCoords.lat, userCoords.lon, propLat, propLon);
    }

    return { ...item, distance };
  }).filter(item => {
    // Text search
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      const titleMatch = item.title?.toLowerCase().includes(q);
      const cityMatch = item.city?.toLowerCase().includes(q);
      const descMatch = item.description?.toLowerCase().includes(q);
      if (!titleMatch && !cityMatch && !descMatch) return false;
    }

    // Price range filter
    if (minPrice && Number(item.price) < Number(minPrice)) return false;
    if (maxPrice && Number(item.price) > Number(maxPrice)) return false;

    // Bedrooms filter
    if (bedrooms !== 'ALL') {
      if (bedrooms === '4+' && item.bedrooms < 4) return false;
      if (bedrooms !== '4+' && item.bedrooms !== Number(bedrooms)) return false;
    }

    // Bathrooms filter
    if (bathrooms !== 'ALL') {
      if (item.bathrooms < Number(bathrooms)) return false;
    }

    // Property Type filter
    if (propertyType !== 'ALL' && item.property_type && item.property_type.toLowerCase() !== propertyType.toLowerCase()) {
      return false;
    }

    // Amenities filter
    if (selectedAmenities.length > 0) {
      const itemAmenities = item.amenities || [];
      const hasAllSelected = selectedAmenities.every(a => itemAmenities.includes(a));
      if (!hasAllSelected) return false;
    }

    return true;
  });

  // Sorting Logic
  const sortedListings = [...filteredListings].sort((a, b) => {
    if (sortBy === 'price_asc') return a.price - b.price;
    if (sortBy === 'price_desc') return b.price - a.price;
    if (sortBy === 'distance') {
      if (a.distance === null) return 1;
      if (b.distance === null) return -1;
      return a.distance - b.distance;
    }
    return 0;
  });

  return (
    <div style={{ padding: '40px 48px', maxWidth: '1280px', margin: '0 auto' }}>
      {/* Header & Title */}
      <div style={{ marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '20px' }}>
        <div>
          <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: '2.4rem', fontWeight: 800, margin: 0, color: 'var(--text-bright)', letterSpacing: '-0.02em' }}>
            Verified Housing Listings
          </h1>
          <p style={{ color: 'var(--text-muted)', margin: '8px 0 0', fontSize: '0.98rem' }}>
            Find available apartments, studios, and private rooms with live AI matching and precise distance calculations.
          </p>
        </div>

        {/* Geolocation API Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={handleGetLocation}
            disabled={isGettingGeo}
            className="btn-emerald"
            style={{
              padding: '12px 22px',
              borderRadius: '10px',
              fontWeight: 700,
              fontSize: '0.88rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              cursor: isGettingGeo ? 'wait' : 'pointer'
            }}
          >
            <Navigation size={16} className={isGettingGeo ? 'spin' : ''} />
            {isGettingGeo ? 'Detecting Location...' : userCoords ? 'Location Active' : 'Use My Location'}
          </button>
        </div>
      </div>

      {geoStatus && (
        <div className="glass-card" style={{ marginBottom: '24px', padding: '12px 18px', borderRadius: '12px', borderLeft: '4px solid var(--accent-emerald)', background: '#ecfdf5', color: '#047857', fontSize: '0.88rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <MapPin size={16} color="var(--accent-emerald)" /> {geoStatus}
        </div>
      )}

      {/* Main Search & Filter Control Bar */}
      <div className="glass-card" style={{ padding: '28px', borderRadius: '16px', marginBottom: '36px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Search Bar Input & Sort */}
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '280px', position: 'relative', display: 'flex', alignItems: 'center' }}>
            <Search size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '16px' }} />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by city, neighborhood, or keyword (e.g. San Francisco, Studio)..."
              style={{
                width: '100%',
                padding: '12px 16px 12px 46px',
                borderRadius: '10px',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
                fontSize: '0.92rem',
                outline: 'none'
              }}
            />
          </div>

          {/* Sort Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ArrowUpDown size={16} color="var(--text-muted)" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              style={{
                padding: '12px 18px',
                borderRadius: '10px',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
                fontWeight: 700,
                fontSize: '0.88rem',
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              <option value="recommended" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Best Match / Recommended</option>
              <option value="price_asc" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Price: Low to High</option>
              <option value="price_desc" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Price: High to Low</option>
              {userCoords && <option value="distance" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Distance: Nearest First</option>}
            </select>
          </div>
        </div>

        {/* Multi-Parameter Filters Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', paddingTop: '20px', borderTop: '1px solid var(--border-color)' }}>
          {/* Price Range Filter */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Price Range ($/mo)</label>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <input
                type="number"
                placeholder="Min $"
                value={minPrice}
                onChange={(e) => setMinPrice(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', background: 'var(--bg-surface)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontSize: '0.88rem', outline: 'none' }}
              />
              <span style={{ color: 'var(--text-muted)' }}>-</span>
              <input
                type="number"
                placeholder="Max $"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', background: 'var(--bg-surface)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontSize: '0.88rem', outline: 'none' }}
              />
            </div>
          </div>

          {/* Property Type Filter */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Property Type</label>
            <select
              value={propertyType}
              onChange={(e) => setPropertyType(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', background: 'var(--bg-surface)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontSize: '0.88rem', outline: 'none', cursor: 'pointer' }}
            >
              <option value="ALL" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>All Types</option>
              <option value="Apartment" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Apartment</option>
              <option value="Studio" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Studio</option>
              <option value="House" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>House</option>
              <option value="Room" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Private Room</option>
            </select>
          </div>

          {/* Bedrooms Filter */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Bedrooms</label>
            <select
              value={bedrooms}
              onChange={(e) => setBedrooms(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', background: 'var(--bg-surface)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontSize: '0.88rem', outline: 'none', cursor: 'pointer' }}
            >
              <option value="ALL" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Any Bedrooms</option>
              <option value="1" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>1 Bedroom</option>
              <option value="2" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>2 Bedrooms</option>
              <option value="3" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>3 Bedrooms</option>
              <option value="4+" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>4+ Bedrooms</option>
            </select>
          </div>

          {/* Bathrooms Filter */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Bathrooms</label>
            <select
              value={bathrooms}
              onChange={(e) => setBathrooms(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', background: 'var(--bg-surface)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', fontSize: '0.88rem', outline: 'none', cursor: 'pointer' }}
            >
              <option value="ALL" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Any Bathrooms</option>
              <option value="1.0" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>1+ Bath</option>
              <option value="1.5" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>1.5+ Baths</option>
              <option value="2.0" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>2+ Baths</option>
            </select>
          </div>
        </div>

        {/* Amenities Chips Filter Row with Consistent Spacing & Vertical Rhythm */}
        <div>
          <label style={{ display: 'block', marginBottom: '12px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Filter by Amenities</label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center' }}>
            {availableAmenities.map((amenity) => {
              const isSelected = selectedAmenities.includes(amenity);
              return (
                <button
                  key={amenity}
                  onClick={() => toggleAmenity(amenity)}
                  style={{
                    padding: '8px 16px',
                    borderRadius: '10px',
                    border: isSelected ? '1px solid var(--accent-emerald)' : '1px solid var(--border-color)',
                    background: isSelected ? 'rgba(5, 150, 105, 0.12)' : 'var(--bg-surface-elevated)',
                    color: isSelected ? 'var(--accent-emerald)' : 'var(--text-secondary)',
                    fontSize: '0.84rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    boxShadow: isSelected ? '0 2px 8px rgba(5, 150, 105, 0.15)' : 'none'
                  }}
                >
                  {isSelected ? '✓ ' : '+ '}{amenity}
                </button>
              );
            })}

            {(searchTerm || minPrice || maxPrice || bedrooms !== 'ALL' || propertyType !== 'ALL' || selectedAmenities.length > 0) && (
              <button
                onClick={resetFilters}
                style={{
                  padding: '8px 16px',
                  borderRadius: '10px',
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  color: 'var(--accent-rose)',
                  fontSize: '0.84rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <X size={14} /> Clear Filters
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Results Header Count */}
      <div style={{ marginBottom: '24px', color: 'var(--text-muted)', fontSize: '0.92rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span>Showing <strong style={{ color: 'var(--text-primary)' }}>{sortedListings.length}</strong> verified properties</span>
      </div>

      {/* Property Cards Grid */}
      {sortedListings.length === 0 ? (
        <div className="glass-card" style={{ padding: '60px', textAlign: 'center', borderRadius: '16px' }}>
          <Search size={44} color="var(--text-muted)" style={{ marginBottom: '16px', opacity: 0.5 }} />
          <h3 style={{ fontFamily: 'Syne, sans-serif', color: 'var(--text-primary)', margin: '0 0 8px', fontSize: '1.25rem' }}>No matching properties</h3>
          <p style={{ color: 'var(--text-muted)', margin: '0 0 20px', fontSize: '0.9rem' }}>Try broadening your filter criteria or search for a different city.</p>
          <button onClick={resetFilters} className="btn-emerald" style={{ padding: '10px 24px', fontSize: '0.88rem' }}>Reset Filters</button>
        </div>
      ) : (
        <div className="grid-layout">
          {sortedListings.map((item) => (
            <div key={item.id} style={{ position: 'relative' }}>
              <ListingCard listing={item} />
              {item.distance !== null && (
                <div style={{
                  position: 'absolute',
                  top: '34px',
                  left: '34px',
                  padding: '6px 12px',
                  borderRadius: '10px',
                  background: 'rgba(15, 23, 42, 0.85)',
                  border: '1px solid rgba(5, 150, 105, 0.4)',
                  backdropFilter: 'blur(8px)',
                  color: '#34d399',
                  fontSize: '0.78rem',
                  fontWeight: 800,
                  pointerEvents: 'none',
                  zIndex: 5,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
                }}>
                  <Navigation size={13} /> {item.distance} km away
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
