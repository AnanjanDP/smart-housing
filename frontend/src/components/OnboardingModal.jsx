import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Sparkles, User, ShieldCheck, Briefcase, Home, FileText, Settings, CreditCard, Building, FileCheck, CheckCircle2, ArrowRight, ArrowLeft, X } from 'lucide-react';

export const OnboardingModal = ({ isOpen, onClose }) => {
  const { user, updatePreferences } = useContext(AuthContext);

  const [onboardingRole, setOnboardingRole] = useState(user?.role || 'TENANT');
  const [currentStep, setCurrentStep] = useState(1); // Steps 1 to 6

  // Tenant State
  const [tenantPersonal, setTenantPersonal] = useState({
    fullName: user?.name || '',
    isdCode: '+91',
    phone: '',
    emergencyContact: '',
    gender: 'Male',
    sexuality: 'Straight / Heterosexual',
    streetAddress: '',
    cityState: '',
    pincode: ''
  });
  const [tenantIdentity, setTenantIdentity] = useState({ idType: 'Driver License', idNumber: '', docUrl: '' });
  const [tenantEmployment, setTenantEmployment] = useState({ employer: '', jobTitle: '', monthlyIncome: '4500', status: 'FULL_TIME' });
  const [tenantRentalHistory, setTenantRentalHistory] = useState({ prevAddress: '', landlordName: '', landlordContact: '', moveReason: '' });
  const [tenantCreditConsent, setTenantCreditConsent] = useState({ consentGiven: true, lastFourSSN: '' });
  const [tenantPreferences, setTenantPreferences] = useState({ budgetMin: 1200, budgetMax: 2500, sleepSchedule: 'EARLY_BIRD', cleanlinessLevel: 4, preferredLocation: 'San Francisco' });

  // Landlord State
  const [landlordPersonal, setLandlordPersonal] = useState({ businessName: user?.name || '', phone: '', businessAddress: '', contactEmail: user?.email || '' });
  const [landlordIdentity, setLandlordIdentity] = useState({ idType: 'Driver License', idNumber: '', docUrl: '' });
  const [landlordPayout, setLandlordPayout] = useState({ bankName: 'JPMorgan Chase', accountName: '', routingNumber: '', accountNumber: '' });
  const [landlordOwnership, setLandlordOwnership] = useState({ docType: 'Property Deed', registrationNumber: '', docUrl: '' });
  const [landlordTax, setLandlordTax] = useState({ taxId: '', w9Status: 'VERIFIED' });
  const [landlordCompliance, setLandlordCompliance] = useState({ fairHousingConsent: true, screeningRule: 'STRICT_CREDIT' });

  useEffect(() => {
    if (user) {
      if (user.role) setOnboardingRole(user.role);
      const prefs = user.preferences || {};

      if (prefs.tenantPersonal) setTenantPersonal(prev => ({ ...prev, ...prefs.tenantPersonal }));
      else if (user.name || user.phone_number) {
        setTenantPersonal(prev => ({
          ...prev,
          fullName: user.name || prev.fullName,
          phone: user.phone_number || prev.phone
        }));
      }

      if (prefs.tenantIdentity) setTenantIdentity(prev => ({ ...prev, ...prefs.tenantIdentity }));
      if (prefs.tenantEmployment) setTenantEmployment(prev => ({ ...prev, ...prefs.tenantEmployment }));
      if (prefs.tenantRentalHistory) setTenantRentalHistory(prev => ({ ...prev, ...prefs.tenantRentalHistory }));
      if (prefs.tenantCreditConsent) setTenantCreditConsent(prev => ({ ...prev, ...prefs.tenantCreditConsent }));
      if (prefs.budgetMin || prefs.budgetMax || prefs.preferredLocation) {
        setTenantPreferences(prev => ({
          ...prev,
          budgetMin: prefs.budgetMin || prev.budgetMin,
          budgetMax: prefs.budgetMax || prev.budgetMax,
          preferredLocation: prefs.preferredLocation || prev.preferredLocation
        }));
      }

      if (prefs.landlordPersonal) setLandlordPersonal(prev => ({ ...prev, ...prefs.landlordPersonal }));
      if (prefs.landlordIdentity) setLandlordIdentity(prev => ({ ...prev, ...prefs.landlordIdentity }));
      if (prefs.landlordPayout) setLandlordPayout(prev => ({ ...prev, ...prefs.landlordPayout }));
      if (prefs.landlordOwnership) setLandlordOwnership(prev => ({ ...prev, ...prefs.landlordOwnership }));
      if (prefs.landlordTax) setLandlordTax(prev => ({ ...prev, ...prefs.landlordTax }));
      if (prefs.landlordCompliance) setLandlordCompliance(prev => ({ ...prev, ...prefs.landlordCompliance }));
    }
  }, [user, isOpen]);

  if (!isOpen) return null;


  const tenantStepTitles = [
    '1. Personal & Contact Info',
    '2. Identity Verification',
    '3. Employment & Income',
    '4. Rental History',
    '5. Credit & Background Check',
    '6. Housing Preferences'
  ];

  const landlordStepTitles = [
    '1. Personal & Contact Info',
    '2. Identity Verification',
    '3. Payout & Banking Info',
    '4. Property Ownership Proof',
    '5. Tax Information',
    '6. Legal & Fair Housing'
  ];

  const currentTitles = onboardingRole === 'LANDLORD' ? landlordStepTitles : tenantStepTitles;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onboardingRole === 'TENANT') {
      updatePreferences({
        ...tenantPreferences,
        tenantPersonal,
        tenantIdentity,
        tenantEmployment,
        tenantRentalHistory,
        tenantCreditConsent
      });
    } else {
      updatePreferences({
        landlordPersonal,
        landlordIdentity,
        landlordPayout,
        landlordOwnership,
        landlordTax,
        landlordCompliance
      });
    }
    if (onClose) onClose();
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      backgroundColor: 'rgba(0, 0, 0, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1100
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '680px',
        maxHeight: '92vh',
        overflowY: 'auto',
        padding: '36px',
        borderRadius: '24px',
        position: 'relative',
        background: '#ffffff',
        border: '1px solid var(--border-color)',
        boxShadow: 'var(--shadow-lg)'
      }}>
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: '20px', right: '20px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
        >
          <X size={22} />
        </button>

        {/* Role Toggle Selector */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={24} color="var(--accent-emerald)" />
            <h2 style={{ margin: 0, fontSize: '1.4rem', color: 'var(--text-primary)', fontWeight: 800 }}>
              {onboardingRole === 'LANDLORD' ? 'Landlord Onboarding' : 'Tenant Compatibility Setup'}
            </h2>
          </div>

          <div style={{ display: 'flex', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '12px', padding: '4px' }}>
            <button
              onClick={() => { setOnboardingRole('TENANT'); setCurrentStep(1); }}
              style={{
                padding: '6px 14px',
                borderRadius: '8px',
                border: 'none',
                background: onboardingRole === 'TENANT' ? '#3b82f6' : 'transparent',
                color: onboardingRole === 'TENANT' ? 'white' : 'var(--text-muted)',
                fontWeight: 600,
                cursor: 'pointer',
                fontSize: '0.85rem'
              }}
            >
              Tenant
            </button>
            <button
              onClick={() => { setOnboardingRole('LANDLORD'); setCurrentStep(1); }}
              style={{
                padding: '6px 14px',
                borderRadius: '8px',
                border: 'none',
                background: onboardingRole === 'LANDLORD' ? '#8b5cf6' : 'transparent',
                color: onboardingRole === 'LANDLORD' ? 'white' : 'var(--text-muted)',
                fontWeight: 600,
                cursor: 'pointer',
                fontSize: '0.85rem'
              }}
            >
              Landlord
            </button>
          </div>
        </div>

        {/* Step Progress Header */}
        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '8px', fontWeight: 600 }}>
            <span>Step {currentStep} of 6: {currentTitles[currentStep - 1]}</span>
            <span>{Math.round((currentStep / 6) * 100)}% Completed</span>
          </div>
          <div style={{ width: '100%', height: '6px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: `${(currentStep / 6) * 100}%`, height: '100%', background: onboardingRole === 'LANDLORD' ? 'linear-gradient(90deg, #8b5cf6, #ec4899)' : 'var(--accent-gradient)', transition: 'width 0.3s ease' }} />
          </div>
        </div>

        {/* Onboarding Wizard Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

          {/* TENANT STEPS */}
          {onboardingRole === 'TENANT' && (
            <>
              {/* Step 1: Personal & Contact */}
              {currentStep === 1 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <User size={20} color="#3b82f6" /> Personal & Contact Information
                  </h3>

                  {/* Full Legal Name - No Text Suggestions */}
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Full Legal Name</label>
                    <input
                      type="text"
                      required
                      name="full-legal-name-no-suggest"
                      autoComplete="off"
                      spellCheck="false"
                      value={tenantPersonal.fullName}
                      onChange={(e) => setTenantPersonal({ ...tenantPersonal, fullName: e.target.value })}
                      placeholder="Enter full legal name"
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                    />
                  </div>

                  {/* Phone Number with ISD Code Dropdown (+91) */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                    <div>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Phone Number</label>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <select
                          value={tenantPersonal.isdCode}
                          onChange={(e) => setTenantPersonal({ ...tenantPersonal, isdCode: e.target.value })}
                          style={{ padding: '12px 8px', borderRadius: '10px', background: '#252932', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.88rem' }}
                        >
                          <option value="+91">🇮🇳 +91</option>
                          <option value="+1">🇺🇸 +1</option>
                          <option value="+44">🇬🇧 +44</option>
                          <option value="+61">🇦🇺 +61</option>
                          <option value="+49">🇩🇪 +49</option>
                          <option value="+971">🇦🇪 +971</option>
                          <option value="+65">🇸🇬 +65</option>
                        </select>
                        <input
                          type="tel"
                          required
                          value={tenantPersonal.phone}
                          onChange={(e) => setTenantPersonal({ ...tenantPersonal, phone: e.target.value })}
                          placeholder="98765 43210"
                          style={{ flex: 1, padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                        />
                      </div>
                    </div>

                    <div>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Emergency Contact Phone</label>
                      <input
                        type="tel"
                        required
                        value={tenantPersonal.emergencyContact}
                        onChange={(e) => setTenantPersonal({ ...tenantPersonal, emergencyContact: e.target.value })}
                        placeholder="+91 99999 88888"
                        style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                      />
                    </div>
                  </div>

                  {/* Gender & Sexuality / Orientation */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                    <div>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Gender</label>
                      <select
                        value={tenantPersonal.gender}
                        onChange={(e) => setTenantPersonal({ ...tenantPersonal, gender: e.target.value })}
                        style={{ width: '100%', padding: '12px', borderRadius: '10px', background: '#252932', border: '1px solid var(--border-color)', color: 'white' }}
                      >
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Non-Binary">Non-Binary</option>
                        <option value="Prefer Not To Say">Prefer Not To Say</option>
                      </select>
                    </div>

                    <div>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Sexuality / Orientation</label>
                      <select
                        value={tenantPersonal.sexuality}
                        onChange={(e) => setTenantPersonal({ ...tenantPersonal, sexuality: e.target.value })}
                        style={{ width: '100%', padding: '12px', borderRadius: '10px', background: '#252932', border: '1px solid var(--border-color)', color: 'white' }}
                      >
                        <option value="Straight / Heterosexual">Straight / Heterosexual</option>
                        <option value="LGBTQ+">LGBTQ+</option>
                        <option value="Prefer Not To Say">Prefer Not To Say</option>
                      </select>
                    </div>
                  </div>

                  {/* Separate Address & Pincode Section */}
                  <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    <h4 style={{ margin: 0, color: '#38bdf8', fontSize: '0.95rem', fontWeight: 700 }}>Current Residence Address Details</h4>

                    <div>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>Street Address & Apartment</label>
                      <input
                        type="text"
                        required
                        value={tenantPersonal.streetAddress}
                        onChange={(e) => setTenantPersonal({ ...tenantPersonal, streetAddress: e.target.value })}
                        placeholder="e.g. 123 Park Avenue, Flat 4B"
                        style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                      />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '14px' }}>
                      <div>
                        <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>City & State</label>
                        <input
                          type="text"
                          required
                          value={tenantPersonal.cityState}
                          onChange={(e) => setTenantPersonal({ ...tenantPersonal, cityState: e.target.value })}
                          placeholder="e.g. Mumbai, Maharashtra"
                          style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                        />
                      </div>

                      <div>
                        <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>Address Pincode / ZIP</label>
                        <input
                          type="text"
                          required
                          value={tenantPersonal.pincode}
                          onChange={(e) => setTenantPersonal({ ...tenantPersonal, pincode: e.target.value })}
                          placeholder="e.g. 400001"
                          style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 2: Identity Verification */}
              {currentStep === 2 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <ShieldCheck size={20} color="#10b981" /> Identity Verification
                  </h3>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Government ID Type</label>
                    <select
                      value={tenantIdentity.idType}
                      onChange={(e) => setTenantIdentity({ ...tenantIdentity, idType: e.target.value })}
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: '#252932', border: '1px solid var(--border-color)', color: 'white' }}
                    >
                      <option value="Driver License">Driver's License</option>
                      <option value="Passport">Passport</option>
                      <option value="State ID">State / National ID</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>ID / Passport Number</label>
                    <input
                      type="text"
                      required
                      value={tenantIdentity.idNumber}
                      onChange={(e) => setTenantIdentity({ ...tenantIdentity, idNumber: e.target.value })}
                      placeholder="e.g. DL-987654321"
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                    />
                  </div>
                </div>
              )}

              {/* Step 3: Employment & Income */}
              {currentStep === 3 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Briefcase size={20} color="#a855f7" /> Employment & Income Verification
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                    <div>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Employer / Organization</label>
                      <input
                        type="text"
                        required
                        value={tenantEmployment.employer}
                        onChange={(e) => setTenantEmployment({ ...tenantEmployment, employer: e.target.value })}
                        placeholder="e.g. Tech Corp Inc."
                        style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Job Title</label>
                      <input
                        type="text"
                        required
                        value={tenantEmployment.jobTitle}
                        onChange={(e) => setTenantEmployment({ ...tenantEmployment, jobTitle: e.target.value })}
                        placeholder="Software Engineer"
                        style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                      />
                    </div>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Gross Monthly Income ($USD)</label>
                    <input
                      type="number"
                      required
                      value={tenantEmployment.monthlyIncome}
                      onChange={(e) => setTenantEmployment({ ...tenantEmployment, monthlyIncome: e.target.value })}
                      placeholder="4500"
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                    />
                  </div>
                </div>
              )}

              {/* Step 4: Rental History */}
              {currentStep === 4 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Home size={20} color="#f59e0b" /> Rental History & References
                  </h3>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Previous Landlord / Property Manager Name (Optional)</label>
                    <input
                      type="text"
                      value={tenantRentalHistory.landlordName}
                      onChange={(e) => setTenantRentalHistory({ ...tenantRentalHistory, landlordName: e.target.value })}
                      placeholder="Jane Doe Properties (Optional)"
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Landlord Contact Phone or Email (Optional)</label>
                    <input
                      type="text"
                      value={tenantRentalHistory.landlordContact}
                      onChange={(e) => setTenantRentalHistory({ ...tenantRentalHistory, landlordContact: e.target.value })}
                      placeholder="landlord@example.com (Optional)"
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                    />
                  </div>
                </div>
              )}

              {/* Step 5: Background & Credit Check */}
              {currentStep === 5 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileCheck size={20} color="#ec4899" /> Background & Credit Check Consent
                  </h3>
                  <div style={{ padding: '16px', borderRadius: '12px', background: 'rgba(236, 72, 153, 0.1)', border: '1px solid rgba(236, 72, 153, 0.3)', color: 'white', fontSize: '0.88rem' }}>
                    By continuing, you authorize StayMatch Platform to perform a soft credit check and FCRA-compliant background screening for rental applications.
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Last 4 Digits of SSN / National ID</label>
                    <input
                      type="password"
                      maxLength="4"
                      required
                      value={tenantCreditConsent.lastFourSSN}
                      onChange={(e) => setTenantCreditConsent({ ...tenantCreditConsent, lastFourSSN: e.target.value })}
                      placeholder="••••"
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                    />
                  </div>
                </div>
              )}

              {/* Step 6: Housing Preferences */}
              {currentStep === 6 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Settings size={20} color="#38bdf8" /> Housing Preferences & Compatibility
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                    <div>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Min Budget ($/mo)</label>
                      <input
                        type="number"
                        value={tenantPreferences.budgetMin}
                        onChange={(e) => setTenantPreferences({ ...tenantPreferences, budgetMin: Number(e.target.value) })}
                        style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Max Budget ($/mo)</label>
                      <input
                        type="number"
                        value={tenantPreferences.budgetMax}
                        onChange={(e) => setTenantPreferences({ ...tenantPreferences, budgetMax: Number(e.target.value) })}
                        style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                      />
                    </div>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Preferred City / Area</label>
                    <input
                      type="text"
                      value={tenantPreferences.preferredLocation}
                      onChange={(e) => setTenantPreferences({ ...tenantPreferences, preferredLocation: e.target.value })}
                      placeholder="e.g. San Francisco"
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                    />
                  </div>
                </div>
              )}
            </>
          )}

          {/* LANDLORD STEPS */}
          {onboardingRole === 'LANDLORD' && (
            <>
              {/* Step 1: Personal & Contact */}
              {currentStep === 1 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <User size={20} color="#8b5cf6" /> Landlord / Business Contact Info
                  </h3>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Landlord / Entity Name</label>
                    <input
                      type="text"
                      required
                      value={landlordPersonal.businessName}
                      onChange={(e) => setLandlordPersonal({ ...landlordPersonal, businessName: e.target.value })}
                      placeholder="e.g. Bay Area Properties LLC"
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                    />
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                    <div>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Contact Phone Number</label>
                      <input
                        type="tel"
                        required
                        value={landlordPersonal.phone}
                        onChange={(e) => setLandlordPersonal({ ...landlordPersonal, phone: e.target.value })}
                        placeholder="+1 (555) 444-3333"
                        style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Official Email</label>
                      <input
                        type="email"
                        required
                        value={landlordPersonal.contactEmail}
                        onChange={(e) => setLandlordPersonal({ ...landlordPersonal, contactEmail: e.target.value })}
                        placeholder="landlord@company.com"
                        style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Step 2: Identity Verification */}
              {currentStep === 2 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <ShieldCheck size={20} color="#10b981" /> Identity Verification
                  </h3>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Government License / ID Number</label>
                    <input
                      type="text"
                      required
                      value={landlordIdentity.idNumber}
                      onChange={(e) => setLandlordIdentity({ ...landlordIdentity, idNumber: e.target.value })}
                      placeholder="e.g. CA-LL-998877"
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                    />
                  </div>
                </div>
              )}

              {/* Step 3: Payout & Banking */}
              {currentStep === 3 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CreditCard size={20} color="#3b82f6" /> Payout & Banking Information
                  </h3>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Bank Name</label>
                    <input
                      type="text"
                      required
                      value={landlordPayout.bankName}
                      onChange={(e) => setLandlordPayout({ ...landlordPayout, bankName: e.target.value })}
                      placeholder="e.g. JPMorgan Chase"
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                    />
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                    <div>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Routing Number</label>
                      <input
                        type="password"
                        required
                        value={landlordPayout.routingNumber}
                        onChange={(e) => setLandlordPayout({ ...landlordPayout, routingNumber: e.target.value })}
                        placeholder="9 Digits"
                        style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Account Number</label>
                      <input
                        type="password"
                        required
                        value={landlordPayout.accountNumber}
                        onChange={(e) => setLandlordPayout({ ...landlordPayout, accountNumber: e.target.value })}
                        placeholder="Account Number"
                        style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Step 4: Property Ownership Proof */}
              {currentStep === 4 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Building size={20} color="#f59e0b" /> Property Ownership Verification
                  </h3>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Ownership Proof Document Type</label>
                    <select
                      value={landlordOwnership.docType}
                      onChange={(e) => setLandlordOwnership({ ...landlordOwnership, docType: e.target.value })}
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: '#252932', border: '1px solid var(--border-color)', color: 'white' }}
                    >
                      <option value="Property Deed">Property Grant Deed</option>
                      <option value="Tax Assessment Bill">Property Tax Bill</option>
                      <option value="Title Insurance">Title Insurance Policy</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>Deed / Parcel Registration Number</label>
                    <input
                      type="text"
                      required
                      value={landlordOwnership.registrationNumber}
                      onChange={(e) => setLandlordOwnership({ ...landlordOwnership, registrationNumber: e.target.value })}
                      placeholder="e.g. PARCEL-88776655"
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                    />
                  </div>
                </div>
              )}

              {/* Step 5: Tax Information */}
              {currentStep === 5 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileText size={20} color="#ec4899" /> Tax Information & W-9
                  </h3>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.88rem', color: 'var(--text-muted)' }}>EIN / Tax Identification Number (TIN)</label>
                    <input
                      type="text"
                      required
                      value={landlordTax.taxId}
                      onChange={(e) => setLandlordTax({ ...landlordTax, taxId: e.target.value })}
                      placeholder="XX-XXXXXXX"
                      style={{ width: '100%', padding: '12px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                    />
                  </div>
                </div>
              )}

              {/* Step 6: Legal & Compliance */}
              {currentStep === 6 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <h3 style={{ color: 'white', margin: 0, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileCheck size={20} color="#38bdf8" /> Legal Compliance & Fair Housing
                  </h3>
                  <div style={{ padding: '16px', borderRadius: '12px', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)', color: 'white', fontSize: '0.88rem' }}>
                    I certify that all property listings comply with local housing regulations, safety ordinances, and Fair Housing Act guidelines.
                  </div>
                </div>
              )}
            </>
          )}

          {/* Navigation Controls */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border-color)' }}>
            {currentStep > 1 ? (
              <button
                type="button"
                onClick={() => setCurrentStep(currentStep - 1)}
                className="btn-secondary"
                style={{ padding: '10px 20px', borderRadius: '10px', fontSize: '0.88rem', display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <ArrowLeft size={16} /> Back
              </button>
            ) : <div />}

            {currentStep < 6 ? (
              <button
                type="button"
                onClick={() => setCurrentStep(currentStep + 1)}
                className="btn-primary"
                style={{ padding: '10px 24px', borderRadius: '10px', fontSize: '0.88rem', display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                Continue <ArrowRight size={16} />
              </button>
            ) : (
              <button
                type="submit"
                className="btn-primary"
                style={{ padding: '12px 28px', borderRadius: '10px', fontSize: '0.92rem', fontWeight: 800, background: 'linear-gradient(135deg, #10b981, #059669)' }}
              >
                Complete Onboarding ✓
              </button>
            )}
          </div>

        </form>
      </div>
    </div>
  );
};
