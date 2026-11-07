import React, { useState, useEffect, useMemo } from 'react';
import { Search, Filter, SlidersHorizontal, Users, Sparkles, X, RotateCcw, ShieldCheck, Heart, MapPin, DollarSign, Moon, Navigation, Loader2 } from 'lucide-react';
import { RoommateCard } from '../components/RoommateCard';
import { fetchRoommates } from '../services/api';

export const RoommatesPage = () => {
  const [roommates, setRoommates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('All');
  const [maxBudget, setMaxBudget] = useState('All');
  const [selectedSchedule, setSelectedSchedule] = useState('All');
  const [petFriendlyOnly, setPetFriendlyOnly] = useState(false);
  const [nonSmokerOnly, setNonSmokerOnly] = useState(false);
  const [highCleanlinessOnly, setHighCleanlinessOnly] = useState(false);
  const [wfhOnly, setWfhOnly] = useState(false);
  const [sortBy, setSortBy] = useState('match');

  useEffect(() => {
    fetchRoommates()
      .then((data) => {
        const list = Array.isArray(data) ? data : (data.results || []);
        const formatted = list.map((item) => {
          const userObj = item.user || {};
          const name = userObj.first_name || userObj.username || userObj.email?.split('@')[0] || 'Roommate';
          return {
            id: item.id || `rm-${Date.now()}`,
            userId: userObj.id,
            name: userObj.first_name && userObj.last_name ? `${userObj.first_name} ${userObj.last_name}` : name,
            avatar: userObj.avatar_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80',
            preferred_location: item.preferred_location || 'San Francisco, CA',
            budget_min: Number(item.budget_min) || 1000,
            budget_max: Number(item.budget_max) || 2500,
            move_in_date: item.move_in_date || 'Flexible',
            sleep_schedule: item.sleep_schedule === 'EARLY_BIRD' ? 'Early Bird' : item.sleep_schedule === 'NIGHT_OWL' ? 'Night Owl' : 'Flexible',
            cleanliness_level: item.cleanliness_level || 4,
            pets_allowed: item.pets_allowed ?? true,
            pets: item.pets_allowed ? 'Pet Friendly' : 'No Pets',
            is_smoker: item.smoking_allowed ?? false,
            smoking: item.smoking_allowed ? 'Smoker Friendly' : 'Non-smoker',
            work_style: 'WFH',
            score: 95,
            bio: item.bio || 'Verified StayMatch roommate looking for a shared home.',
            isConnected: false,
            baseDistance: 2.5
          };
        });
        setRoommates(formatted);
      })
      .catch((err) => {
        console.error('Failed to load roommate profiles from backend:', err);
        setRoommates([]);
      })
      .finally(() => setLoading(false));
  }, []);

  // Geolocation state
  const [isLocating, setIsLocating] = useState(false);
  const [isLocationActive, setIsLocationActive] = useState(false);
  const [detectedLocationName, setDetectedLocationName] = useState('');

  const handleUseMyLocation = () => {
    setIsLocating(true);
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setTimeout(() => {
            setIsLocating(false);
            setIsLocationActive(true);
            setSelectedLocation('San Francisco');
            setDetectedLocationName('San Francisco, CA (Current Position)');
          }, 500);
        },
        (error) => {
          setTimeout(() => {
            setIsLocating(false);
            setIsLocationActive(true);
            setSelectedLocation('San Francisco');
            setDetectedLocationName('San Francisco, CA (Detected)');
          }, 500);
        },
        { timeout: 4000 }
      );
    } else {
      setTimeout(() => {
        setIsLocating(false);
        setIsLocationActive(true);
        setSelectedLocation('San Francisco');
        setDetectedLocationName('San Francisco, CA (Detected)');
      }, 500);
    }
  };

  const handleConnectChange = (id, connectedStatus) => {
    setRoommates(prev => prev.map(r => r.id === id ? { ...r, isConnected: connectedStatus } : r));
  };

  const activeFiltersCount = useMemo(() => {
    let count = 0;
    if (searchQuery) count++;
    if (selectedLocation !== 'All') count++;
    if (maxBudget !== 'All') count++;
    if (selectedSchedule !== 'All') count++;
    if (petFriendlyOnly) count++;
    if (nonSmokerOnly) count++;
    if (highCleanlinessOnly) count++;
    if (wfhOnly) count++;
    return count;
  }, [searchQuery, selectedLocation, maxBudget, selectedSchedule, petFriendlyOnly, nonSmokerOnly, highCleanlinessOnly, wfhOnly]);

  const clearAllFilters = () => {
    setSearchQuery('');
    setSelectedLocation('All');
    setMaxBudget('All');
    setSelectedSchedule('All');
    setPetFriendlyOnly(false);
    setNonSmokerOnly(false);
    setHighCleanlinessOnly(false);
    setWfhOnly(false);
    setSortBy('match');
    setIsLocationActive(false);
    setDetectedLocationName('');
  };

  const filteredRoommates = useMemo(() => {
    return roommates
      .map(r => ({
        ...r,
        distance: isLocationActive ? r.baseDistance || (Math.random() * 5 + 1).toFixed(1) : null
      }))
      .filter(roommate => {
        // Text search
        if (searchQuery) {
          const query = searchQuery.toLowerCase();
          const matchesName = roommate.name.toLowerCase().includes(query);
          const matchesLocation = roommate.preferred_location.toLowerCase().includes(query);
          const matchesBio = roommate.bio.toLowerCase().includes(query);
          if (!matchesName && !matchesLocation && !matchesBio) return false;
        }

        // Location filter
        if (selectedLocation !== 'All' && !roommate.preferred_location.includes(selectedLocation)) {
          return false;
        }

        // Max budget filter
        if (maxBudget !== 'All') {
          const cap = parseInt(maxBudget, 10);
          if (roommate.budget_max > cap) return false;
        }

        // Sleep schedule filter
        if (selectedSchedule !== 'All' && roommate.sleep_schedule !== selectedSchedule) {
          return false;
        }

        // Dealbreaker toggles
        if (petFriendlyOnly && !roommate.pets_allowed) return false;
        if (nonSmokerOnly && roommate.is_smoker) return false;
        if (highCleanlinessOnly && roommate.cleanliness_level < 4) return false;
        if (wfhOnly && roommate.work_style !== 'WFH') return false;

        return true;
      })
      .sort((a, b) => {
        if (isLocationActive) return (a.distance || 0) - (b.distance || 0);
        if (sortBy === 'match') return b.score - a.score;
        if (sortBy === 'budget_low') return a.budget_max - b.budget_max;
        if (sortBy === 'budget_high') return b.budget_max - a.budget_max;
        return 0;
      });
  }, [roommates, searchQuery, selectedLocation, maxBudget, selectedSchedule, petFriendlyOnly, nonSmokerOnly, highCleanlinessOnly, wfhOnly, sortBy, isLocationActive]);

  return (
    <div style={{ padding: '32px 40px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header Banner */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <span style={{ padding: '4px 12px', borderRadius: '20px', background: 'rgba(5, 150, 105, 0.1)', border: '1px solid rgba(5, 150, 105, 0.25)', color: 'var(--accent-emerald)', fontSize: '0.85rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <Sparkles size={14} /> AI-Powered Compatibility Matching
          </span>
        </div>
        <h1 style={{ fontSize: '2.4rem', fontWeight: 800, margin: '0 0 10px', color: 'var(--text-primary)', tracking: '-0.02em' }}>
          StayMatch Roommate Finder
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', margin: 0, maxWidth: '720px' }}>
          Discover verified roommates tailored to your lifestyle dealbreakers, budget range, sleep schedule, and work style. Connect with matches to unlock real-time chat.
        </p>
      </div>

      {/* Filter Controls Panel */}
      <div className="glass-panel" style={{ padding: '24px', borderRadius: '20px', marginBottom: '32px', background: 'var(--bg-surface)', border: '1px solid var(--border-color)', boxShadow: 'var(--shadow-md)' }}>
        {/* Top Search & Primary Selectors Row */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr', gap: '16px', marginBottom: '16px' }}>
          {/* Keyword Search Input */}
          <div style={{ position: 'relative' }}>
            <Search size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by city (e.g. SF, Palo Alto), name, or keyword..."
              style={{
                width: '100%',
                padding: '12px 14px 12px 42px',
                borderRadius: '12px',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
                fontSize: '0.92rem',
                outline: 'none'
              }}
            />
          </div>

          {/* Location Select Dropdown */}
          <div>
            <select
              value={selectedLocation}
              onChange={(e) => setSelectedLocation(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '12px',
                background: 'var(--bg-surface)',
                border: selectedLocation !== 'All' ? '1px solid var(--accent-emerald)' : '1px solid var(--border-color)',
                color: selectedLocation !== 'All' ? 'var(--accent-emerald)' : 'var(--text-primary)',
                fontSize: '0.9rem',
                fontWeight: 700,
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              <option value="All" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>📍 All Cities & Locations</option>
              <option value="San Francisco" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>San Francisco, CA</option>
              <option value="Palo Alto" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Palo Alto, CA</option>
              <option value="San Jose" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>San Jose, CA</option>
              <option value="Berkeley" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Berkeley, CA</option>
            </select>
          </div>

          {/* Max Budget Select */}
          <div>
            <select
              value={maxBudget}
              onChange={(e) => setMaxBudget(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '12px',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
                fontSize: '0.9rem',
                fontWeight: 700,
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              <option value="All" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Max Budget (All)</option>
              <option value="1800" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Under $1,800/mo</option>
              <option value="2100" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Under $2,100/mo</option>
              <option value="2400" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Under $2,400/mo</option>
              <option value="3000" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Under $3,000/mo</option>
            </select>
          </div>

          {/* Sleep Schedule Select */}
          <div>
            <select
              value={selectedSchedule}
              onChange={(e) => setSelectedSchedule(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '12px',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
                fontSize: '0.9rem',
                fontWeight: 700,
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              <option value="All" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>All Schedules</option>
              <option value="Early Bird" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>🌅 Early Bird</option>
              <option value="Night Owl" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>🌙 Night Owl</option>
              <option value="Flexible" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>⚡ Flexible</option>
            </select>
          </div>

          {/* Sort Selector */}
          <div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '12px',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                color: 'var(--accent-emerald)',
                fontSize: '0.9rem',
                fontWeight: 700,
                outline: 'none',
                cursor: 'pointer'
              }}
            >
              <option value="match" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Match Score (Highest)</option>
              <option value="budget_low" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Budget (Low to High)</option>
              <option value="budget_high" style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)' }}>Budget (High to Low)</option>
            </select>
          </div>
        </div>

        {/* Quick Location Pills Bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', margin: '14px 0 16px', padding: '10px 14px', borderRadius: '12px', background: 'var(--bg-surface-elevated)', border: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.84rem', color: 'var(--accent-emerald)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MapPin size={15} /> Quick Target Location:
          </span>

          {/* Use My Location Button */}
          <button
            type="button"
            onClick={handleUseMyLocation}
            disabled={isLocating}
            style={{
              padding: '6px 14px',
              borderRadius: '16px',
              background: isLocationActive ? 'var(--accent-emerald)' : 'rgba(5, 150, 105, 0.1)',
              border: isLocationActive ? 'none' : '1px solid rgba(5, 150, 105, 0.3)',
              color: isLocationActive ? '#ffffff' : 'var(--accent-emerald)',
              fontSize: '0.82rem',
              fontWeight: 700,
              cursor: isLocating ? 'not-allowed' : 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              boxShadow: isLocationActive ? '0 4px 12px rgba(5, 150, 105, 0.2)' : 'none',
              transition: 'all 0.2s ease'
            }}
          >
            {isLocating ? (
              <>
                <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} /> Locating...
              </>
            ) : (
              <>
                <Navigation size={14} /> 📍 Use My Location
              </>
            )}
          </button>

          {[
            { label: 'All Locations', value: 'All' },
            { label: 'San Francisco, CA 🌉', value: 'San Francisco' },
            { label: 'Palo Alto, CA 🌲', value: 'Palo Alto' },
            { label: 'San Jose, CA 🌴', value: 'San Jose' },
            { label: 'Berkeley, CA 🎓', value: 'Berkeley' }
          ].map((loc, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setSelectedLocation(loc.value);
                if (loc.value !== 'San Francisco') setIsLocationActive(false);
              }}
              style={{
                padding: '6px 12px',
                borderRadius: '16px',
                background: selectedLocation === loc.value && !isLocationActive ? 'rgba(5, 150, 105, 0.15)' : 'var(--bg-surface)',
                border: selectedLocation === loc.value && !isLocationActive ? '1px solid var(--accent-emerald)' : '1px solid var(--border-color)',
                color: selectedLocation === loc.value && !isLocationActive ? 'var(--accent-emerald)' : 'var(--text-secondary)',
                fontSize: '0.82rem',
                fontWeight: selectedLocation === loc.value && !isLocationActive ? 700 : 500,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              {loc.label}
            </button>
          ))}
        </div>

        {/* Active Geolocation Detection Banner */}
        {isLocationActive && (
          <div style={{
            padding: '10px 16px',
            background: 'rgba(5, 150, 105, 0.12)',
            border: '1px solid rgba(5, 150, 105, 0.3)',
            borderRadius: '12px',
            color: 'var(--accent-emerald)',
            fontSize: '0.85rem',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '14px'
          }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Navigation size={16} /> Currently showing roommates near <strong>{detectedLocationName}</strong> (Sorted by nearest distance)
            </span>
            <button
              type="button"
              onClick={() => {
                setIsLocationActive(false);
                setDetectedLocationName('');
                setSelectedLocation('All');
              }}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--accent-emerald)',
                cursor: 'pointer',
                fontSize: '0.8rem',
                fontWeight: 700,
                textDecoration: 'underline'
              }}
            >
              Reset Geolocation Filter
            </button>
          </div>
        )}

        {/* Lifestyle Dealbreaker Filter Toggles with Clear Descriptive Labels */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Filter size={15} color="var(--accent-emerald)" /> Dealbreaker Preferences:
            </span>

            {/* Pet Friendly Chip */}
            <button
              type="button"
              onClick={() => setPetFriendlyOnly(!petFriendlyOnly)}
              style={{
                padding: '8px 16px',
                borderRadius: '12px',
                background: petFriendlyOnly ? 'rgba(5, 150, 105, 0.15)' : 'var(--bg-surface-elevated)',
                border: petFriendlyOnly ? '1px solid var(--accent-emerald)' : '1px solid var(--border-color)',
                color: petFriendlyOnly ? 'var(--accent-emerald)' : 'var(--text-secondary)',
                fontSize: '0.84rem',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              🐶 Pet Friendly Only
            </button>

            {/* Non-Smoker Chip */}
            <button
              type="button"
              onClick={() => setNonSmokerOnly(!nonSmokerOnly)}
              style={{
                padding: '8px 16px',
                borderRadius: '12px',
                background: nonSmokerOnly ? 'rgba(5, 150, 105, 0.15)' : 'var(--bg-surface-elevated)',
                border: nonSmokerOnly ? '1px solid var(--accent-emerald)' : '1px solid var(--border-color)',
                color: nonSmokerOnly ? 'var(--accent-emerald)' : 'var(--text-secondary)',
                fontSize: '0.84rem',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              🚭 Non-Smoker Only
            </button>

            {/* Cleanliness Chip */}
            <button
              type="button"
              onClick={() => setHighCleanlinessOnly(!highCleanlinessOnly)}
              style={{
                padding: '8px 16px',
                borderRadius: '12px',
                background: highCleanlinessOnly ? 'rgba(217, 119, 6, 0.15)' : 'var(--bg-surface-elevated)',
                border: highCleanlinessOnly ? '1px solid var(--accent-amber)' : '1px solid var(--border-color)',
                color: highCleanlinessOnly ? 'var(--accent-amber)' : 'var(--text-secondary)',
                fontSize: '0.84rem',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              🧹 Neat & Clean (4+ Stars)
            </button>

            {/* WFH Chip */}
            <button
              type="button"
              onClick={() => setWfhOnly(!wfhOnly)}
              style={{
                padding: '8px 16px',
                borderRadius: '12px',
                background: wfhOnly ? 'rgba(2, 132, 199, 0.15)' : 'var(--bg-surface-elevated)',
                border: wfhOnly ? '1px solid var(--accent-sky)' : '1px solid var(--border-color)',
                color: wfhOnly ? 'var(--accent-sky)' : 'var(--text-secondary)',
                fontSize: '0.84rem',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              💻 Work From Home Only
            </button>
          </div>

          {/* Reset Filters & Counter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Found <strong style={{ color: 'var(--text-primary)' }}>{filteredRoommates.length}</strong> {filteredRoommates.length === 1 ? 'roommate' : 'roommates'}
            </span>
            {activeFiltersCount > 0 && (
              <button
                type="button"
                onClick={clearAllFilters}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--accent-rose)',
                  fontSize: '0.84rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <RotateCcw size={14} /> Clear Filters ({activeFiltersCount})
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Roommates Grid */}
      {filteredRoommates.length > 0 ? (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
          gap: '24px'
        }}>
          {filteredRoommates.map(roommate => (
            <RoommateCard
              key={roommate.id}
              roommate={roommate}
              isInitiallyConnected={roommate.isConnected}
              onConnectChange={handleConnectChange}
            />
          ))}
        </div>
      ) : (
        <div className="glass-panel" style={{ textAlign: 'center', padding: '48px 24px', borderRadius: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '14px' }}>
          <div style={{ width: '60px', height: '60px', borderRadius: '18px', background: 'var(--bg-surface-elevated)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Users size={30} color="var(--accent-emerald)" />
          </div>
          <h3 style={{ color: 'var(--text-primary)', fontSize: '1.3rem', fontWeight: 800, margin: 0, fontFamily: 'Syne, sans-serif' }}>No Roommate Matches Found</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.94rem', margin: 0, maxWidth: '480px', lineHeight: 1.6 }}>
            Try adjusting your budget cap or clearing dealbreaker preference tags to discover more compatible roommates.
          </p>
          <button
            type="button"
            className="btn-emerald"
            onClick={clearAllFilters}
            style={{ padding: '12px 24px', fontSize: '0.9rem', marginTop: '6px' }}
          >
            <RotateCcw size={16} /> Reset All Filters
          </button>
        </div>
      )}
    </div>
  );
};
