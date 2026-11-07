import React, { useState, useEffect, useContext, useRef } from 'react';
import { AuthContext } from '../context/AuthContext';
import { ProfileCompletionCard } from '../components/ProfileCompletionCard';
import { ListingDetailModal } from '../components/ListingDetailModal';
import { LandlordTenantChatModal } from '../components/LandlordTenantChatModal';
import { fetchApplicationsApi, updateApplicationStatusApi } from '../services/api';
import { Home, Plus, Users, CheckCircle, XCircle, Clock, Image, MapPin, DollarSign, BedDouble, Bath, Tag, X, Sparkles, Upload, Eye, MessageSquare, Building2, Camera, Trash2, RefreshCw } from 'lucide-react';

export const LandlordDashboard = () => {
  const { user, landlordListings, addNewListing, setShowOnboarding } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('properties'); // 'properties', 'applicants', or 'chats'
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [selectedChatListing, setSelectedChatListing] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loadingApps, setLoadingApps] = useState(true);
  const fileInputRef = useRef(null);

  const samplePropertyPresets = [
    { name: 'Modern Loft', url: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80' },
    { name: 'Urban Studio', url: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80' },
    { name: 'Luxury Apartment', url: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80' },
    { name: 'High-Rise Penthouse', url: 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80' }
  ];

  const handleImageFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImageUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  useEffect(() => {
    fetchApplicationsApi()
      .then((data) => {
        setApplications(Array.isArray(data) ? data : (data?.results || []));
      })
      .catch((err) => {
        console.error('Failed to fetch landlord applications:', err);
        setApplications([]);
      })
      .finally(() => setLoadingApps(false));
  }, []);

  const handleUpdateStatus = async (appId, status) => {
    try {
      await updateApplicationStatusApi(appId, status);
      setApplications(prev => prev.map(a => a.id === appId ? { ...a, status } : a));
    } catch (e) {
      console.error('Failed to update status:', e);
    }
  };

  // Form State for New Property
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [city, setCity] = useState('');
  const [address, setAddress] = useState('');
  const [bedrooms, setBedrooms] = useState('1');
  const [bathrooms, setBathrooms] = useState('1.0');
  const [propertyType, setPropertyType] = useState('Apartment');
  const [imageUrl, setImageUrl] = useState('');
  const [selectedAmenities, setSelectedAmenities] = useState(['WiFi', 'Air Conditioning']);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [selectedPropertyForDetail, setSelectedPropertyForDetail] = useState(null);

  const availableAmenities = ['WiFi', 'Parking', 'Air Conditioning', 'Laundry', 'Gym', 'Pet Friendly', 'Balcony', 'Swimming Pool'];

  const toggleAmenity = (amenity) => {
    if (selectedAmenities.includes(amenity)) {
      setSelectedAmenities(selectedAmenities.filter(a => a !== amenity));
    } else {
      setSelectedAmenities([...selectedAmenities, amenity]);
    }
  };

  const handleAddProperty = (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const defaultImage = imageUrl.trim() || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80';

    addNewListing({
      title,
      description,
      price: Number(price),
      city,
      address,
      bedrooms: Number(bedrooms),
      bathrooms: Number(bathrooms),
      property_type: propertyType,
      amenities: selectedAmenities,
      images: [defaultImage]
    });

    setIsSubmitting(false);
    setIsAddModalOpen(false);

    // Reset Form
    setTitle('');
    setDescription('');
    setPrice('');
    setCity('');
    setAddress('');
    setImageUrl('');
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'APPROVED':
      case 'ACCEPTED':
        return (
          <span style={{ padding: '6px 12px', borderRadius: '20px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', color: '#10b981', fontSize: '0.85rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <CheckCircle size={14} /> Approved
          </span>
        );
      case 'DECLINED':
      case 'REJECTED':
        return (
          <span style={{ padding: '6px 12px', borderRadius: '20px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', color: '#ef4444', fontSize: '0.85rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <XCircle size={14} /> Declined
          </span>
        );
      default:
        return (
          <span style={{ padding: '6px 12px', borderRadius: '20px', background: 'rgba(245, 158, 11, 0.15)', border: '1px solid rgba(245, 158, 11, 0.4)', color: '#f59e0b', fontSize: '0.85rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <Clock size={14} /> Pending Review
          </span>
        );
    }
  };

  return (
    <div style={{ padding: '40px 48px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header Banner */}
      <div className="glass-card" style={{ padding: '32px', borderRadius: '16px', marginBottom: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 14px', borderRadius: '6px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', color: 'var(--accent-emerald)', fontSize: '0.8rem', fontWeight: 700, marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            <Sparkles size={14} /> Landlord Management Portal
          </div>
          <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: '2.2rem', fontWeight: 800, margin: 0, color: 'white', letterSpacing: '-0.02em' }}>
            Property Owner Dashboard
          </h1>
          <p style={{ color: 'var(--text-muted)', margin: '8px 0 0', fontSize: '0.98rem' }}>
            Welcome back, <strong style={{ color: 'white' }}>{user?.name || user?.username || 'Landlord'}</strong>! Manage your properties and review interested tenant applications.
          </p>
        </div>

        <button
          onClick={() => setIsAddModalOpen(true)}
          className="btn-emerald"
          style={{ padding: '12px 24px', borderRadius: '10px', fontSize: '0.92rem', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 800 }}
        >
          <Plus size={18} /> List New Property
        </button>
      </div>

      {/* Profile Completion Widget */}
      <ProfileCompletionCard user={user} onOpenOnboarding={() => setShowOnboarding(true)} />

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '28px', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
        <button
          onClick={() => setActiveTab('properties')}
          style={{
            padding: '12px 22px',
            borderRadius: '10px',
            background: activeTab === 'properties' ? 'var(--accent-emerald)' : '#07080b',
            border: activeTab === 'properties' ? 'none' : '1px solid var(--border-color)',
            color: activeTab === 'properties' ? '#07080b' : 'var(--text-muted)',
            fontWeight: 800,
            fontSize: '0.9rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.15s ease'
          }}
        >
          <Home size={16} /> My Properties ({landlordListings.length})
        </button>

        <button
          onClick={() => setActiveTab('applicants')}
          style={{
            padding: '12px 22px',
            borderRadius: '10px',
            background: activeTab === 'applicants' ? 'var(--accent-emerald)' : '#07080b',
            border: activeTab === 'applicants' ? 'none' : '1px solid var(--border-color)',
            color: activeTab === 'applicants' ? '#07080b' : 'var(--text-muted)',
            fontWeight: 800,
            fontSize: '0.9rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.15s ease'
          }}
        >
          <Users size={16} /> Interested Applicants ({applications.length})
        </button>

        <button
          onClick={() => setActiveTab('chats')}
          style={{
            padding: '12px 22px',
            borderRadius: '10px',
            background: activeTab === 'chats' ? 'var(--accent-emerald)' : '#07080b',
            border: activeTab === 'chats' ? 'none' : '1px solid var(--border-color)',
            color: activeTab === 'chats' ? '#07080b' : 'var(--text-muted)',
            fontWeight: 800,
            fontSize: '0.9rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.15s ease'
          }}
        >
          <MessageSquare size={16} /> Tenant Inquiries ({applications.length})
        </button>
      </div>

      {/* Tab 1: My Listed Properties */}
      {activeTab === 'properties' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '24px' }}>
          {landlordListings.map((prop) => (
            <div
              key={prop.id}
              className="glass-panel"
              onClick={() => setSelectedPropertyForDetail(prop)}
              style={{ borderRadius: '18px', overflow: 'hidden', display: 'flex', flexDirection: 'column', cursor: 'pointer', transition: 'transform 0.2s ease' }}
            >
              <div style={{ position: 'relative', height: '200px', width: '100%' }}>
                <img
                  src={prop.images?.[0] || 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80'}
                  alt={prop.title}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
                <span style={{ position: 'absolute', top: '12px', right: '12px', padding: '4px 12px', borderRadius: '14px', background: 'rgba(16, 185, 129, 0.9)', color: 'white', fontSize: '0.8rem', fontWeight: 700 }}>
                  {prop.status || 'ACTIVE'}
                </span>
                <span style={{ position: 'absolute', bottom: '12px', left: '12px', padding: '6px 14px', borderRadius: '10px', background: 'rgba(0, 0, 0, 0.75)', backdropFilter: 'blur(4px)', color: '#38bdf8', fontSize: '1.1rem', fontWeight: 800 }}>
                  ${prop.price}/mo
                </span>
              </div>

              <div style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <h3 style={{ margin: '0 0 6px', color: 'white', fontSize: '1.15rem', fontWeight: 700 }}>{prop.title}</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: '0 0 12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <MapPin size={14} color="#38bdf8" /> {prop.address || prop.city}
                  </p>

                  <div style={{ display: 'flex', gap: '16px', color: 'var(--text-main)', fontSize: '0.85rem', marginBottom: '14px' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><BedDouble size={16} color="#a855f7" /> {prop.bedrooms} Beds</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Bath size={16} color="#a855f7" /> {prop.bathrooms} Baths</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Tag size={16} color="#a855f7" /> {prop.property_type || 'Apartment'}</span>
                  </div>

                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: '0 0 16px', lineClamp: 2, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {prop.description}
                  </p>
                </div>

                <div style={{ paddingTop: '12px', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: '#a855f7', fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Users size={16} /> {prop.applicants_count || 0} Interested Applicants
                  </span>
                  <button className="btn-secondary" style={{ padding: '6px 14px', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Eye size={14} /> View Details
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 2: Interested Applicants */}
      {activeTab === 'applicants' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {applications.length === 0 ? (
            <div className="glass-panel" style={{ padding: '40px', textAlign: 'center' }}>
              <Users size={36} color="var(--text-muted)" style={{ marginBottom: '12px' }} />
              <p style={{ color: 'var(--text-muted)', margin: 0 }}>No tenant applications received yet.</p>
            </div>
          ) : (
            applications.map((app) => {
              const applicantName = app.applicant?.first_name ? `${app.applicant.first_name} ${app.applicant.last_name || ''}` : app.applicant?.username || app.applicant?.email || 'Tenant Applicant';
              const listingTitle = app.listing_detail?.title || 'Property Listing';
              const price = app.listing_detail?.price;
              const city = app.listing_detail?.city || 'San Francisco';

              return (
                <div key={app.id} className="glass-panel" style={{ padding: '24px', borderRadius: '18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                    <div style={{ width: '52px', height: '52px', borderRadius: '50%', background: 'var(--accent-gradient)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 800, fontSize: '1.2rem' }}>
                      {applicantName[0]}
                    </div>

                    <div>
                      <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700, color: 'white' }}>{listingTitle}</h3>
                      <p style={{ margin: '4px 0 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                        Applicant: <strong style={{ color: 'white' }}>{applicantName}</strong> • {city} {price ? `• $${price}/mo` : ''} • Target Move-in: {app.move_in_date || 'Flexible'}
                      </p>
                      {app.notes && (
                        <p style={{ margin: '8px 0 0', color: 'var(--text-main)', fontSize: '0.85rem', background: 'rgba(255, 255, 255, 0.04)', padding: '8px 12px', borderRadius: '8px', borderLeft: '3px solid #3b82f6' }}>
                          "{app.notes}"
                        </p>
                      )}
                    </div>
                  </div>

                  <div>
                    {app.status === 'PENDING' ? (
                      <div style={{ display: 'flex', gap: '10px' }}>
                        <button
                          onClick={() => handleUpdateStatus(app.id, 'APPROVED')}
                          className="btn-primary"
                          style={{ padding: '10px 20px', borderRadius: '10px', fontSize: '0.88rem' }}
                        >
                          Accept Tenant
                        </button>
                        <button
                          onClick={() => handleUpdateStatus(app.id, 'REJECTED')}
                          className="btn-secondary"
                          style={{ padding: '10px 20px', borderRadius: '10px', fontSize: '0.88rem', color: '#ef4444' }}
                        >
                          Decline
                        </button>
                      </div>
                    ) : (
                      getStatusBadge(app.status)
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Tab 3: Tenant Inquiries & Chat */}
      {activeTab === 'chats' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {applications.length === 0 ? (
            <div className="glass-panel" style={{ padding: '40px', textAlign: 'center' }}>
              <MessageSquare size={36} color="var(--text-muted)" style={{ marginBottom: '12px' }} />
              <p style={{ color: 'var(--text-muted)', margin: 0 }}>No active tenant inquiries or messages yet.</p>
            </div>
          ) : (
            applications.map((app) => {
              const applicantName = app.applicant?.first_name ? `${app.applicant.first_name} ${app.applicant.last_name || ''}` : app.applicant?.username || app.applicant?.email || 'Tenant Applicant';
              const listingObj = app.listing_detail || { title: 'Property Listing', city: 'San Francisco', price: 2500 };

              return (
                <div
                  key={app.id}
                  className="glass-panel"
                  style={{
                    padding: '24px',
                    borderRadius: '16px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    border: '1px solid var(--border-color)',
                    background: '#1a1d24'
                  }}
                  onClick={() => setSelectedChatListing({ ...listingObj, chatTenantId: app.applicant?.id })}
                >
                  <div style={{ display: 'flex', gap: '18px', alignItems: 'center' }}>
                    <div style={{
                      width: '52px',
                      height: '52px',
                      borderRadius: '50%',
                      background: 'var(--accent-gradient)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontWeight: 800,
                      fontSize: '1.2rem',
                      flexShrink: 0
                    }}>
                      {applicantName[0]}
                    </div>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 800, color: 'white' }}>{applicantName}</h3>
                      </div>
                      <p style={{ margin: '4px 0 0', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                        Property: <strong style={{ color: 'white' }}>{listingObj.title}</strong> • {listingObj.city} • ${listingObj.price}/mo
                      </p>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <button
                      className="btn-primary"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedChatListing({ ...listingObj, chatTenantId: app.applicant?.id });
                      }}
                      style={{
                        padding: '10px 16px',
                        borderRadius: '10px',
                        fontSize: '0.88rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontWeight: 700
                      }}
                    >
                      <MessageSquare size={16} /> Reply to Tenant
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Modal: List New Property */}
      {isAddModalOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          backgroundColor: 'rgba(7, 8, 11, 0.85)',
          backdropFilter: 'blur(12px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1100
        }}>
          <div className="glass-card" style={{
            width: '100%',
            maxWidth: '680px',
            maxHeight: '90vh',
            overflowY: 'auto',
            padding: '36px',
            borderRadius: '20px',
            position: 'relative',
            background: '#0e1017',
            border: '1px solid var(--border-color)'
          }}>
            <button
              onClick={() => setIsAddModalOpen(false)}
              style={{ position: 'absolute', top: '24px', right: '24px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
            >
              <X size={22} />
            </button>

            <div style={{ marginBottom: '24px' }}>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 12px', borderRadius: '6px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', color: 'var(--accent-emerald)', fontSize: '0.78rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>
                <Building2 size={14} /> Property Management
              </div>
              <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.8rem', fontWeight: 800, color: 'white', margin: '0 0 6px', letterSpacing: '-0.02em' }}>
                List New Property
              </h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', margin: 0 }}>
                Provide listing details, rental pricing, high-res photos, and included amenities.
              </p>
            </div>

            <form onSubmit={handleAddProperty} style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
              {/* Section 1: Overview */}
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Property Title
                </label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Modern High-Rise Studio in Downtown SF"
                  style={{ width: '100%', padding: '12px 16px', borderRadius: '10px', background: '#07080b', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.92rem', outline: 'none' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Monthly Rent ($USD)
                  </label>
                  <input
                    type="number"
                    required
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    placeholder="e.g. 2400"
                    style={{ width: '100%', padding: '12px 16px', borderRadius: '10px', background: '#07080b', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.92rem', outline: 'none' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Property Type
                  </label>
                  <select
                    value={propertyType}
                    onChange={(e) => setPropertyType(e.target.value)}
                    style={{ width: '100%', padding: '12px 16px', borderRadius: '10px', background: '#07080b', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.92rem', outline: 'none', cursor: 'pointer' }}
                  >
                    <option value="Apartment">Apartment</option>
                    <option value="Studio">Studio</option>
                    <option value="House">House</option>
                    <option value="Room">Private Room</option>
                  </select>
                </div>
              </div>

              {/* Section 2: Location & Capacity */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    City
                  </label>
                  <input
                    type="text"
                    required
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="e.g. San Francisco"
                    style={{ width: '100%', padding: '12px 16px', borderRadius: '10px', background: '#07080b', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.92rem', outline: 'none' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Full Street Address
                  </label>
                  <input
                    type="text"
                    required
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    placeholder="e.g. 100 Market St, Apt 4B"
                    style={{ width: '100%', padding: '12px 16px', borderRadius: '10px', background: '#07080b', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.92rem', outline: 'none' }}
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Bedrooms
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={bedrooms}
                    onChange={(e) => setBedrooms(e.target.value)}
                    style={{ width: '100%', padding: '12px 16px', borderRadius: '10px', background: '#07080b', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.92rem', outline: 'none' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Bathrooms
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    min="1"
                    value={bathrooms}
                    onChange={(e) => setBathrooms(e.target.value)}
                    style={{ width: '100%', padding: '12px 16px', borderRadius: '10px', background: '#07080b', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.92rem', outline: 'none' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Property Description
                </label>
                <textarea
                  rows="3"
                  required
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe property features, floorplan layout, lease length, and neighborhood highlights..."
                  style={{ width: '100%', padding: '12px 16px', borderRadius: '10px', background: '#07080b', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.92rem', fontFamily: 'inherit', outline: 'none' }}
                />
              </div>

              {/* Section 3: Interactive Picture Upload & Change Controls */}
              <div style={{ background: '#07080b', padding: '20px', borderRadius: '14px', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <label style={{ fontSize: '0.82rem', color: 'var(--accent-emerald)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Property Picture (Upload or Web URL)
                  </label>
                  {imageUrl && (
                    <span style={{ fontSize: '0.78rem', color: '#a7f3d0', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <CheckCircle size={14} /> Photo Active
                    </span>
                  )}
                </div>

                {/* Hidden File Input for Device Disk Upload */}
                <input
                  type="file"
                  ref={fileInputRef}
                  accept="image/*"
                  onChange={handleImageFileChange}
                  style={{ display: 'none' }}
                />

                {imageUrl ? (
                  <div style={{ position: 'relative', borderRadius: '12px', overflow: 'hidden', border: '2px solid var(--accent-emerald)', height: '210px' }}>
                    <img src={imageUrl} alt="Property Preview" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    <div style={{
                      position: 'absolute',
                      bottom: 0,
                      left: 0,
                      right: 0,
                      padding: '12px 18px',
                      background: 'linear-gradient(to top, rgba(7, 8, 11, 0.95) 0%, transparent 100%)',
                      display: 'flex',
                      justify: 'space-between',
                      alignItems: 'center'
                    }}>
                      <span style={{ color: 'white', fontSize: '0.85rem', fontWeight: 700 }}>Cover Photo Preview</span>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          type="button"
                          onClick={() => fileInputRef.current?.click()}
                          className="btn-emerald"
                          style={{ padding: '6px 14px', borderRadius: '8px', fontSize: '0.8rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '6px' }}
                        >
                          <RefreshCw size={14} /> Change Picture
                        </button>
                        <button
                          type="button"
                          onClick={() => setImageUrl('')}
                          style={{ padding: '6px 14px', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', color: '#f87171', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
                        >
                          <Trash2 size={14} /> Remove
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    style={{
                      border: '2px dashed var(--border-color)',
                      borderRadius: '12px',
                      padding: '32px 20px',
                      textAlign: 'center',
                      background: 'rgba(255, 255, 255, 0.02)',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <Upload size={32} color="var(--accent-emerald)" style={{ marginBottom: '10px' }} />
                    <h4 style={{ margin: '0 0 4px', color: 'white', fontSize: '0.98rem', fontWeight: 700 }}>Click to Upload Picture from Computer</h4>
                    <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.82rem' }}>Supports PNG, JPG, WEBP formats</p>
                  </div>
                )}

                {/* Paste URL Field */}
                <div>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Or Paste Image Web URL</label>
                  <input
                    type="url"
                    value={imageUrl}
                    onChange={(e) => setImageUrl(e.target.value)}
                    placeholder="https://images.unsplash.com/photo-..."
                    style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', background: '#0e1017', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.88rem', outline: 'none' }}
                  />
                </div>

                {/* 1-Click Sample Presets */}
                <div>
                  <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Sample Photo Presets (1-Click Selection)</label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {samplePropertyPresets.map((preset) => (
                      <button
                        key={preset.name}
                        type="button"
                        onClick={() => setImageUrl(preset.url)}
                        style={{
                          padding: '6px 14px',
                          borderRadius: '8px',
                          background: imageUrl === preset.url ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                          border: imageUrl === preset.url ? '1px solid var(--accent-emerald)' : '1px solid var(--border-color)',
                          color: imageUrl === preset.url ? 'var(--accent-emerald)' : 'var(--text-muted)',
                          fontSize: '0.8rem',
                          fontWeight: 600,
                          cursor: 'pointer'
                        }}
                      >
                        📷 {preset.name}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Section 4: Amenities Checklist */}
              <div>
                <label style={{ display: 'block', marginBottom: '10px', fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Amenities Included
                </label>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {availableAmenities.map((amenity) => {
                    const isSelected = selectedAmenities.includes(amenity);
                    return (
                      <button
                        key={amenity}
                        type="button"
                        onClick={() => toggleAmenity(amenity)}
                        style={{
                          padding: '7px 16px',
                          borderRadius: '8px',
                          border: isSelected ? '1px solid rgba(16, 185, 129, 0.5)' : '1px solid var(--border-color)',
                          background: isSelected ? 'rgba(16, 185, 129, 0.12)' : '#07080b',
                          color: isSelected ? 'var(--accent-emerald)' : 'var(--text-muted)',
                          fontSize: '0.84rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                          transition: 'all 0.15s ease'
                        }}
                      >
                        {isSelected ? '✓ ' : '+ '}{amenity}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                className="btn-emerald"
                disabled={isSubmitting}
                style={{ width: '100%', padding: '14px', borderRadius: '10px', marginTop: '10px', fontWeight: 800, fontSize: '0.98rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
              >
                <Plus size={18} />
                {isSubmitting ? 'Publishing Listing...' : 'Publish Property Listing'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Property Details Modal */}
      {selectedPropertyForDetail && (
        <ListingDetailModal
          listing={selectedPropertyForDetail}
          isOpen={Boolean(selectedPropertyForDetail)}
          onClose={() => setSelectedPropertyForDetail(null)}
        />
      )}

      {/* Landlord Tenant Chat Modal */}
      {selectedChatListing && (
        <LandlordTenantChatModal
          listing={selectedChatListing}
          isOpen={Boolean(selectedChatListing)}
          onClose={() => setSelectedChatListing(null)}
        />
      )}
    </div>
  );
};
