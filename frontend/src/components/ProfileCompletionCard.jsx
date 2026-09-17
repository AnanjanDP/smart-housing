import React from 'react';
import { CheckCircle2, AlertCircle, Sparkles, ArrowRight, ShieldCheck, UserCheck } from 'lucide-react';

export const ProfileCompletionCard = ({ user, onOpenOnboarding }) => {
  const role = user?.role || 'TENANT';
  const isLandlord = role === 'LANDLORD';

  const prefs = user?.preferences || {};

  const tenantChecklist = [
    { label: 'Personal & Contact Info', key: 'personal', done: Boolean(user?.name || user?.email) },
    { label: 'Phone & Emergency Contact', key: 'phone', done: Boolean(prefs.tenantPersonal?.phone || user?.phone_number) },
    { label: 'Identity Verification (Govt ID)', key: 'identity', done: Boolean(prefs.tenantIdentity?.idNumber) },
    { label: 'Employment & Income Proof', key: 'employment', done: Boolean(prefs.tenantEmployment?.employer) },
    { label: 'Background & Credit Consent', key: 'backgroundConsent', done: Boolean(prefs.tenantCreditConsent?.consentGiven) },
    { label: 'Housing Preferences & Budget', key: 'preferences', done: Boolean(prefs.budgetMin || prefs.budgetMax || prefs.tenantPreferences?.budgetMin) }
  ];

  const landlordChecklist = [
    { label: 'Personal & Business Details', key: 'contact', done: Boolean(user?.name || user?.email) },
    { label: 'Identity Verification (Govt ID)', key: 'identity', done: Boolean(prefs.landlordIdentity?.idNumber) },
    { label: 'Payout & Banking Setup', key: 'payout', done: Boolean(prefs.landlordPayout?.accountNumber || prefs.landlordPayout?.bankName) },
    { label: 'Property Ownership Proof', key: 'ownership', done: Boolean(prefs.landlordOwnership?.registrationNumber || prefs.landlordOwnership?.docType) },
    { label: 'Tax ID & W-9 Status', key: 'tax', done: Boolean(prefs.landlordTax?.taxId) },
    { label: 'Fair Housing Consent', key: 'compliance', done: Boolean(prefs.landlordCompliance?.fairHousingConsent) }
  ];

  const checklist = isLandlord ? landlordChecklist : tenantChecklist;
  const completedCount = checklist.filter(item => item.done).length;
  const completionPercentage = Math.round((completedCount / checklist.length) * 100);

  if (completionPercentage === 100) {
    return (
      <div className="glass-panel" style={{
        padding: '24px 32px',
        borderRadius: '20px',
        marginBottom: '32px',
        background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(15, 23, 42, 0.8) 100%)',
        border: '1px solid rgba(16, 185, 129, 0.4)',
        display: 'flex',
        justify: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '50%',
            background: 'rgba(16, 185, 129, 0.2)',
            border: '2px solid #10b981',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#10b981',
            boxShadow: '0 0 15px rgba(16, 185, 129, 0.3)'
          }}>
            <ShieldCheck size={30} />
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'white', fontWeight: 800 }}>
                Profile Verified
              </h3>
              <span style={{
                padding: '4px 12px',
                borderRadius: '14px',
                background: 'rgba(16, 185, 129, 0.25)',
                color: '#34d399',
                fontSize: '0.85rem',
                fontWeight: 800,
                border: '1px solid rgba(16, 185, 129, 0.5)'
              }}>
                ✓ 100% Complete & Verified
              </span>
            </div>
            <p style={{ margin: '4px 0 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              {isLandlord
                ? 'Your property owner credentials and payout details are fully verified.'
                : 'Your tenant identity, background consent, and preferences are fully verified.'}
            </p>
          </div>
        </div>

        <button
          onClick={onOpenOnboarding}
          className="btn-secondary"
          style={{
            padding: '10px 20px',
            borderRadius: '12px',
            fontSize: '0.88rem',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            borderColor: 'rgba(16, 185, 129, 0.4)',
            color: 'white'
          }}
        >
          Update Profile <ArrowRight size={16} />
        </button>
      </div>
    );
  }

  return (
    <div className="glass-panel" style={{
      padding: '24px 32px',
      borderRadius: '20px',
      marginBottom: '32px',
      background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.7) 100%)',
      border: '1px solid rgba(59, 130, 246, 0.3)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '50%',
            background: 'rgba(59, 130, 246, 0.2)',
            border: '2px solid #3b82f6',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#60a5fa',
            fontWeight: 800,
            fontSize: '1.1rem'
          }}>
            {completionPercentage}%
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'white', fontWeight: 800 }}>
                {isLandlord ? 'Homeowner Profile Completion' : 'Tenant Profile Completion'}
              </h3>
              <span style={{
                padding: '2px 10px',
                borderRadius: '12px',
                background: 'rgba(245, 158, 11, 0.2)',
                color: '#f59e0b',
                fontSize: '0.78rem',
                fontWeight: 700
              }}>
                In Progress ({completionPercentage}%)
              </span>
            </div>
            <p style={{ margin: '4px 0 0', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
              {isLandlord
                ? 'Complete your profile to instantly verify property listings and receive tenant applications.'
                : 'A completed profile increases your roommate & rental application match rate by up to 3x!'}
            </p>
          </div>
        </div>

        <button
          onClick={onOpenOnboarding}
          className="btn-primary"
          style={{
            padding: '10px 20px',
            borderRadius: '10px',
            fontSize: '0.88rem',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          Complete Setup <ArrowRight size={16} />
        </button>
      </div>

      {/* Progress Bar */}
      <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '6px', overflow: 'hidden', marginBottom: '20px' }}>
        <div style={{
          width: `${completionPercentage}%`,
          height: '100%',
          background: 'var(--accent-gradient)',
          transition: 'width 0.4s ease'
        }} />
      </div>

      {/* Interactive Checklist Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px' }}>
        {checklist.map((item, idx) => (
          <div key={idx} style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '8px 12px',
            borderRadius: '10px',
            background: item.done ? 'rgba(16, 185, 129, 0.08)' : 'rgba(255, 255, 255, 0.03)',
            border: item.done ? '1px solid rgba(16, 185, 129, 0.2)' : '1px solid var(--border-color)',
            fontSize: '0.85rem',
            color: item.done ? 'white' : 'var(--text-muted)'
          }}>
            {item.done ? (
              <CheckCircle2 size={16} color="#10b981" style={{ flexShrink: 0 }} />
            ) : (
              <AlertCircle size={16} color="#f59e0b" style={{ flexShrink: 0 }} />
            )}
            <span style={{ fontWeight: item.done ? 600 : 400 }}>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
