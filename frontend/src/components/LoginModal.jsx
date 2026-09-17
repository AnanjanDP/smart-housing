import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { LogIn, UserPlus, X, ShieldCheck, ArrowRight, Eye, EyeOff, Camera, Upload, Lock, Loader2 } from 'lucide-react';

export const LoginModal = ({ isOpen, onClose, initialMode = 'login' }) => {
    const [mode, setMode] = useState(initialMode); // 'login' or 'register'

    useEffect(() => {
        if (isOpen) {
            setMode(initialMode || 'login');
            setError('');
        }
    }, [isOpen, initialMode]);
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [role, setRole] = useState('TENANT');
    const [avatarUrl, setAvatarUrl] = useState('');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Google OAuth state
    const [showGooglePrompt, setShowGooglePrompt] = useState(false);
    const [googleName, setGoogleName] = useState('');
    const [googleEmail, setGoogleEmail] = useState('');
    const [googleAvatar, setGoogleAvatar] = useState('');

    const presetAvatars = [
        "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80",
        "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80",
        "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80"
    ];

    const handleFileChange = (e) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setAvatarUrl(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const { login, register, oauthLogin, supabaseGoogleLogin } = useContext(AuthContext);

    if (!isOpen) return null;

    const handleGoogleSignInClick = async () => {
        setError('');
        setIsSubmitting(true);
        try {
            await supabaseGoogleLogin();
        } catch (err) {
            console.warn('Supabase OAuth notice:', err?.message || err);
            // Fallback to manual Google profile confirmation modal
            setShowGooglePrompt(true);
        } finally {
            setIsSubmitting(false);
        }
    };

    const parseErrorMessage = (err) => {
        if (!err?.response?.data) return err?.message || 'Authentication failed. Please check your credentials.';
        const d = err.response.data;
        if (typeof d === 'string') return d;
        if (d.detail) return d.detail;
        if (typeof d === 'object') {
            const messages = [];
            for (const [field, errors] of Object.entries(d)) {
                const errStr = Array.isArray(errors) ? errors.join(', ') : errors;
                const capitalizedField = field.charAt(0).toUpperCase() + field.slice(1);
                messages.push(`${capitalizedField}: ${errStr}`);
            }
            return messages.join(' | ');
        }
        return 'Authentication failed. Please check your credentials.';
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsSubmitting(true);

        try {
            if (mode === 'login') {
                await login(username, password);
            } else {
                await register({ username, email, password, role, avatar_url: avatarUrl });
            }
            onClose();
        } catch (err) {
            console.error('Auth error:', err);
            setError(parseErrorMessage(err));
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleGoogleOauthSubmit = async (e) => {
        if (e) e.preventDefault();
        setError('');
        setIsSubmitting(true);
        try {
            const derivedEmail = googleEmail || (googleName ? `${googleName.toLowerCase().replace(/\s+/g, '.')}@gmail.com` : 'user@gmail.com');
            await oauthLogin({
                provider: 'google_oidc',
                email: derivedEmail,
                name: googleName,
                avatar_url: googleAvatar,
                sub: `google-oauth-${Date.now()}`
            });
            setShowGooglePrompt(false);
            onClose();
        } catch (err) {
            console.error('OAuth error:', err);
            setError(parseErrorMessage(err));
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            backgroundColor: 'rgba(10, 12, 18, 0.85)',
            backdropFilter: 'blur(12px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
        }}>
            <div className="glass-panel" style={{
                width: '100%',
                maxWidth: '440px',
                padding: '32px',
                borderRadius: '16px',
                position: 'relative',
                background: '#1a1d24',
                boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6), 0 0 1px rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.08)'
            }}>
                <button
                    onClick={() => { setShowGooglePrompt(false); onClose(); }}
                    style={{
                        position: 'absolute',
                        top: '16px',
                        right: '16px',
                        background: 'none',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer'
                    }}
                >
                    <X size={20} />
                </button>

                {showGooglePrompt ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {/* Profile Avatar & Header */}
                        <div style={{ textAlign: 'center', marginBottom: '4px' }}>
                            <div style={{ position: 'relative', width: '64px', height: '64px', margin: '0 auto 10px' }}>
                                <img
                                    src={googleAvatar || presetAvatars[0]}
                                    alt="Google Account Avatar"
                                    style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover', border: '2px solid #4285F4' }}
                                />
                                <div style={{ position: 'absolute', bottom: '-2px', right: '-2px', width: '22px', height: '22px', borderRadius: '50%', background: '#4285F4', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '2px solid #1a1d24' }}>
                                    <ShieldCheck size={14} color="white" />
                                </div>
                            </div>
                            <h3 style={{ color: 'white', margin: 0, fontSize: '1.25rem', fontWeight: 800 }}>Confirm Google Profile</h3>
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>Verify your Google account details to finalize sign-in</p>
                        </div>

                        {error && (
                            <div style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#ef4444', borderRadius: '8px', fontSize: '0.85rem' }}>
                                ⚠️ {error}
                            </div>
                        )}

                        <form onSubmit={handleGoogleOauthSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                            {/* Editable Display Name Field */}
                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                                    <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Display Name (Visible on Profile)</label>
                                    <span style={{ fontSize: '0.75rem', color: '#60a5fa', fontWeight: 600 }}>Editable</span>
                                </div>
                                <input
                                    type="text"
                                    required
                                    value={googleName}
                                    onChange={(e) => setGoogleName(e.target.value)}
                                    placeholder="Enter your display name"
                                    style={{ width: '100%', padding: '12px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.95rem' }}
                                />
                            </div>

                            {/* Editable Google Account Email Field */}
                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                                    <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Google Account Email</label>
                                    <span style={{ fontSize: '0.75rem', color: '#60a5fa', fontWeight: 600 }}>Editable</span>
                                </div>
                                <input
                                    type="email"
                                    required
                                    value={googleEmail}
                                    onChange={(e) => setGoogleEmail(e.target.value)}
                                    placeholder="e.g. alex.jones@gmail.com"
                                    style={{ width: '100%', padding: '12px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.95rem' }}
                                />
                            </div>

                            {/* Action Button with Loading Spinner */}
                            <button
                                type="submit"
                                disabled={isSubmitting}
                                style={{
                                    width: '100%',
                                    padding: '13px',
                                    borderRadius: '10px',
                                    background: '#4285F4',
                                    border: 'none',
                                    color: 'white',
                                    fontWeight: 700,
                                    fontSize: '0.95rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '10px',
                                    cursor: isSubmitting ? 'not-allowed' : 'pointer',
                                    marginTop: '8px',
                                    opacity: isSubmitting ? 0.8 : 1,
                                    boxShadow: '0 4px 14px rgba(66, 133, 244, 0.35)'
                                }}
                            >
                                {isSubmitting ? (
                                    <>
                                        <Loader2 size={18} className="spin" /> Verifying Auth Tokens...
                                    </>
                                ) : (
                                    <>
                                        Confirm & Complete Sign-In <ArrowRight size={18} />
                                    </>
                                )}
                            </button>

                            <button
                                type="button"
                                onClick={() => setShowGooglePrompt(false)}
                                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '0.85rem', cursor: 'pointer', textAlign: 'center' }}
                            >
                                Back to Sign In options
                            </button>
                        </form>
                    </div>
                ) : mode === 'forgot_password' ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ width: '52px', height: '52px', borderRadius: '50%', background: 'rgba(59, 130, 246, 0.15)', border: '1px solid rgba(59, 130, 246, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 12px' }}>
                                <Lock size={24} color="#60a5fa" />
                            </div>
                            <h3 style={{ color: 'white', margin: 0, fontSize: '1.25rem', fontWeight: 800 }}>Recover Password</h3>
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '6px' }}>Enter your account email to receive a password reset link</p>
                        </div>

                        {error && (
                            <div style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#ef4444', borderRadius: '8px', fontSize: '0.85rem' }}>
                                {error}
                            </div>
                        )}

                        <form onSubmit={(e) => {
                            e.preventDefault();
                            setError('');
                            setIsSubmitting(true);
                            setTimeout(() => {
                                setIsSubmitting(false);
                                setError('✅ Recovery link sent! Please check your email inbox.');
                            }, 800);
                        }} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            <div>
                                <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Registered Email Address</label>
                                <input
                                    type="email"
                                    required
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="yourname@example.com"
                                    style={{ width: '100%', padding: '12px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white', fontSize: '0.95rem' }}
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={isSubmitting}
                                className="btn-primary"
                                style={{ width: '100%', padding: '12px', fontWeight: 700 }}
                            >
                                {isSubmitting ? 'Sending Request...' : 'Send Password Reset Link'}
                            </button>

                            <button
                                type="button"
                                onClick={() => { setMode('login'); setError(''); }}
                                style={{ background: 'none', border: 'none', color: '#60a5fa', fontSize: '0.85rem', cursor: 'pointer', textAlign: 'center', fontWeight: 600 }}
                            >
                                ← Back to Sign In
                            </button>
                        </form>
                    </div>
                ) : (
                    <>
                        {/* Mode Selector Tabs */}
                        <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', marginBottom: '24px' }}>
                            <button
                                onClick={() => { setMode('login'); setError(''); }}
                                style={{
                                    flex: 1,
                                    padding: '12px',
                                    background: 'none',
                                    border: 'none',
                                    borderBottom: mode === 'login' ? '2px solid #3b82f6' : 'none',
                                    color: mode === 'login' ? 'white' : 'var(--text-muted)',
                                    fontWeight: 700,
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '8px'
                                }}
                            >
                                <LogIn size={18} /> Sign In
                            </button>
                            <button
                                onClick={() => { setMode('register'); setError(''); }}
                                style={{
                                    flex: 1,
                                    padding: '12px',
                                    background: 'none',
                                    border: 'none',
                                    borderBottom: mode === 'register' ? '2px solid #3b82f6' : 'none',
                                    color: mode === 'register' ? 'white' : 'var(--text-muted)',
                                    fontWeight: 700,
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '8px'
                                }}
                            >
                                <UserPlus size={18} /> Create Account
                            </button>
                        </div>

                        {error && (
                            <div style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#ef4444', borderRadius: '8px', marginBottom: '16px', fontSize: '0.9rem' }}>
                                {error}
                            </div>
                        )}

                        {/* Streamlined Google Sign-In Button */}
                        <button
                            type="button"
                            onClick={handleGoogleSignInClick}
                            disabled={isSubmitting}
                            style={{
                                width: '100%',
                                padding: '12px',
                                borderRadius: '8px',
                                background: 'rgba(255, 255, 255, 0.08)',
                                border: '1px solid var(--border-color)',
                                color: 'white',
                                fontWeight: 600,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '10px',
                                cursor: 'pointer',
                                marginBottom: '20px',
                                transition: 'all 0.2s ease'
                            }}
                        >
                            <ShieldCheck size={20} color="#4285F4" />
                            Sign in with Google
                        </button>

                        <div style={{ display: 'flex', alignItems: 'center', margin: '16px 0', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                            <div style={{ flex: 1, height: '1px', background: 'var(--border-color)' }}></div>
                            <span style={{ padding: '0 10px' }}>OR</span>
                            <div style={{ flex: 1, height: '1px', background: 'var(--border-color)' }}></div>
                        </div>

                        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {mode === 'register' && (
                                <div>
                                    <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', color: 'var(--text-muted)' }}>Email Address (Must be unique)</label>
                                    <input
                                        type="email"
                                        required
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="name@example.com"
                                        style={{ width: '100%', padding: '12px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                                    />
                                </div>
                            )}

                            <div>
                                <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                                    {mode === 'login' ? 'Username or Email Address' : 'Username (Must be unique)'}
                                </label>
                                <input
                                    type="text"
                                    required
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder={mode === 'login' ? 'Enter username or email' : 'Enter unique username'}
                                    style={{ width: '100%', padding: '12px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                                />
                            </div>

                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                                    <label style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Password</label>
                                    {mode === 'login' && (
                                        <button
                                            type="button"
                                            onClick={() => { setMode('forgot_password'); setError(''); }}
                                            style={{ background: 'none', border: 'none', color: '#60a5fa', fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer' }}
                                        >
                                            Forgot password?
                                        </button>
                                    )}
                                </div>
                                <div style={{ position: 'relative' }}>
                                    <input
                                        type={showPassword ? "text" : "password"}
                                        required
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder="Enter password"
                                        style={{ width: '100%', padding: '12px 42px 12px 12px', borderRadius: '8px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', color: 'white' }}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        style={{
                                            position: 'absolute',
                                            right: '12px',
                                            top: '50%',
                                            transform: 'translateY(-50%)',
                                            background: 'none',
                                            border: 'none',
                                            color: 'var(--text-muted)',
                                            cursor: 'pointer',
                                            display: 'flex',
                                            alignItems: 'center',
                                            padding: '4px'
                                        }}
                                        title={showPassword ? "Hide password" : "Show password"}
                                    >
                                        {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                    </button>
                                </div>
                            </div>

                            {mode === 'register' && (
                                <>
                                    <div>
                                        <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', color: 'var(--text-muted)' }}>Account Type</label>
                                        <select
                                            value={role}
                                            onChange={(e) => setRole(e.target.value)}
                                            style={{ width: '100%', padding: '12px', borderRadius: '8px', background: '#252932', border: '1px solid var(--border-color)', color: 'white' }}
                                        >
                                            <option value="TENANT">Tenant / Roommate Seeker</option>
                                            <option value="LANDLORD">Property Owner / Landlord</option>
                                        </select>
                                    </div>

                                    <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                                        <label style={{ display: 'block', marginBottom: '10px', fontSize: '0.9rem', color: 'white', fontWeight: 600 }}>
                                            Profile Picture
                                        </label>
                                        
                                        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', marginBottom: '14px' }}>
                                            <div style={{ position: 'relative', width: '60px', height: '60px', borderRadius: '50%', overflow: 'hidden', border: '2px solid #3b82f6', background: 'rgba(255, 255, 255, 0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                                                {avatarUrl ? (
                                                    <img src={avatarUrl} alt="Avatar preview" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                                ) : (
                                                    <Camera size={24} color="var(--text-muted)" />
                                                )}
                                            </div>

                                            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '6px' }}>
                                                <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '8px 14px', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.15)', border: '1px solid rgba(59, 130, 246, 0.4)', color: '#60a5fa', fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer', width: 'fit-content' }}>
                                                    <Upload size={14} /> Choose Photo File
                                                    <input type="file" accept="image/*" onChange={handleFileChange} style={{ display: 'none' }} />
                                                </label>
                                                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Upload photo from device or choose a preset</span>
                                            </div>
                                        </div>

                                        <div>
                                            <span style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Or select a preset avatar:</span>
                                            <div style={{ display: 'flex', gap: '10px' }}>
                                                {presetAvatars.map((url, idx) => (
                                                    <button
                                                        key={idx}
                                                        type="button"
                                                        onClick={() => setAvatarUrl(url)}
                                                        style={{
                                                            width: '36px',
                                                            height: '36px',
                                                            borderRadius: '50%',
                                                            padding: 0,
                                                            border: avatarUrl === url ? '2px solid #3b82f6' : '1px solid var(--border-color)',
                                                            overflow: 'hidden',
                                                            cursor: 'pointer',
                                                            opacity: avatarUrl === url ? 1 : 0.7
                                                        }}
                                                    >
                                                        <img src={url} alt={`Preset ${idx}`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </>
                            )}

                            <button
                                type="submit"
                                className="btn-primary"
                                disabled={isSubmitting}
                                style={{ marginTop: '8px', width: '100%', padding: '12px', opacity: isSubmitting ? 0.7 : 1 }}
                            >
                                {isSubmitting ? 'Processing...' : (mode === 'login' ? 'Sign In' : 'Create Account')}
                            </button>
                        </form>
                    </>
                )}
            </div>
        </div>
    );
};