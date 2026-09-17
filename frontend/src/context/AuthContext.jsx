import React, { createContext, useState, useEffect } from 'react';
import { loginUserApi, registerUserApi, oauthLoginApi, fetchCurrentUser, createListingApi, fetchApplicationsApi, createApplicationApi, updateApplicationStatusApi, updateUserProfileApi } from '../services/api';
import { supabase } from '../lib/supabaseClient';

export const AuthContext = createContext();

const initialSentRequests = [];
const initialReceivedRequests = [];
const initialLandlordListings = [];

const getUserWithSavedPreferences = (userData) => {
  if (!userData) return userData;
  const userKey = userData.email || userData.username || userData.id;
  let savedPrefs = userData.preferences;

  if (!savedPrefs && userKey) {
    try {
      const storedStr = localStorage.getItem(`staymatch_profile_${userKey}`);
      if (storedStr) {
        savedPrefs = JSON.parse(storedStr);
      }
    } catch (e) {}
  }

  const hasCompleted = Boolean(
    savedPrefs || 
    userData.phone_number || 
    userData.bio || 
    (userData.preferences && Object.keys(userData.preferences).length > 0)
  );

  return {
    ...userData,
    preferences: savedPrefs || userData.preferences || null,
    is_profile_completed: hasCompleted
  };
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sentRequests, setSentRequests] = useState(initialSentRequests);
  const [receivedRequests, setReceivedRequests] = useState(initialReceivedRequests);
  const [landlordListings, setLandlordListings] = useState(initialLandlordListings);
  const [showOnboarding, setShowOnboarding] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const savedSent = localStorage.getItem('staymatch_sent_requests');
    const savedReceived = localStorage.getItem('staymatch_received_requests');
    const savedListings = localStorage.getItem('staymatch_landlord_listings');

    if (savedSent) {
      try { setSentRequests(JSON.parse(savedSent)); } catch (e) {}
    }
    if (savedReceived) {
      try { setReceivedRequests(JSON.parse(savedReceived)); } catch (e) {}
    }
    if (savedListings) {
      try { setLandlordListings(JSON.parse(savedListings)); } catch (e) {}
    }

    const handleSupabaseSession = async (session) => {
      if (!session?.user) return;
      const supaUser = session.user;
      const displayName = supaUser.user_metadata?.full_name || supaUser.user_metadata?.name || supaUser.email?.split('@')[0] || 'User';
      const avatarUrl = supaUser.user_metadata?.avatar_url || supaUser.user_metadata?.picture;

      try {
        const synced = await oauthLoginApi({
          email: supaUser.email,
          name: displayName,
          avatar_url: avatarUrl,
          provider: 'google_oidc',
          sub: supaUser.id
        });
        const rawData = { ...synced.user, name: displayName, avatar_url: synced.user?.avatar_url || avatarUrl };
        const userData = getUserWithSavedPreferences(rawData);
        localStorage.setItem('staymatch_token', synced.access);
        localStorage.setItem('staymatch_user', JSON.stringify(userData));
        if (isMounted) setUser(userData);
      } catch (err) {
        console.warn('Backend OAuth sync warning:', err);
        const fallbackUser = getUserWithSavedPreferences({
          id: supaUser.id,
          email: supaUser.email,
          username: supaUser.email?.split('@')[0],
          name: displayName,
          avatar_url: avatarUrl
        });
        localStorage.setItem('staymatch_user', JSON.stringify(fallbackUser));
        if (isMounted) setUser(fallbackUser);
      }
    };

    const initAuthSession = async () => {
      try {
        // 1. Check for active Supabase session (handles OAuth hash / PKCE redirect automatically)
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (session?.user) {
          await handleSupabaseSession(session);
        } else {
          // 2. Fallback to localStorage saved user if no active Supabase OAuth session
          const savedUser = localStorage.getItem('staymatch_user');
          const token = localStorage.getItem('staymatch_token');
          if (savedUser && token) {
            const parsedUser = JSON.parse(savedUser);
            const enrichedUser = getUserWithSavedPreferences(parsedUser);
            if (isMounted) setUser(enrichedUser);
          }
        }
      } catch (err) {
        console.error('Failed to initialize auth session:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    initAuthSession();

    // 3. Listen to Supabase auth events (SIGNED_IN, TOKEN_REFRESHED, SIGNED_OUT)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('Supabase Auth Event:', event, session?.user?.email);
      if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED' || event === 'USER_UPDATED') {
        if (session?.user) {
          await handleSupabaseSession(session);
        }
      } else if (event === 'SIGNED_OUT') {
        if (isMounted) {
          setUser(null);
          localStorage.removeItem('staymatch_token');
          localStorage.removeItem('staymatch_user');
        }
      }
    });

    return () => {
      isMounted = false;
      subscription?.unsubscribe();
    };
  }, []);

  const saveSent = (requests) => {
    setSentRequests(requests);
    localStorage.setItem('staymatch_sent_requests', JSON.stringify(requests));
  };

  const saveReceived = (requests) => {
    setReceivedRequests(requests);
    localStorage.setItem('staymatch_received_requests', JSON.stringify(requests));
  };

  const saveListings = (listings) => {
    setLandlordListings(listings);
    localStorage.setItem('staymatch_landlord_listings', JSON.stringify(listings));
  };

  const addNewListing = async (newListing) => {
    let created;
    try {
      created = await createListingApi(newListing);
    } catch (e) {
      created = {
        id: `prop-${Date.now()}`,
        status: "ACTIVE",
        applicants_count: 0,
        created_at: new Date().toISOString().split('T')[0],
        ...newListing
      };
    }
    const updated = [created, ...landlordListings];
    saveListings(updated);
    return created;
  };

  const login = async (username, password) => {
    const data = await loginUserApi(username, password);
    const token = data.access;
    localStorage.setItem('staymatch_token', token);

    let rawUserData = data.user;
    if (!rawUserData) {
      try {
        rawUserData = await fetchCurrentUser();
      } catch (e) {
        rawUserData = { username, name: username };
      }
    }

    const userData = getUserWithSavedPreferences(rawUserData);

    localStorage.setItem('staymatch_user', JSON.stringify(userData));
    setUser(userData);

    if (!userData.preferences && !userData.is_profile_completed) {
      setShowOnboarding(true);
    } else {
      setShowOnboarding(false);
    }
    return userData;
  };

  const register = async (userData) => {
    await registerUserApi(userData);
    const res = await login(userData.username, userData.password);
    const fullUser = getUserWithSavedPreferences({
      ...res,
      ...userData,
      name: userData.name || userData.username,
      avatar_url: userData.avatar_url || res.avatar_url,
      role: userData.role || res.role || 'TENANT'
    });
    localStorage.setItem('staymatch_user', JSON.stringify(fullUser));
    setUser(fullUser);

    if (!fullUser.preferences && !fullUser.is_profile_completed) {
      setShowOnboarding(true);
    }
    return fullUser;
  };

  const oauthLogin = async (payload) => {
    const data = await oauthLoginApi(payload);
    const userData = getUserWithSavedPreferences({
      ...data.user,
      name: payload.name || data.user?.name || data.user?.first_name || data.user?.username,
      email: payload.email || data.user?.email,
      avatar_url: payload.avatar_url || data.user?.avatar_url,
      role: data.user?.role || 'TENANT'
    });
    localStorage.setItem('staymatch_token', data.access);
    localStorage.setItem('staymatch_user', JSON.stringify(userData));
    setUser(userData);

    if (!userData.preferences && !userData.is_profile_completed) {
      setShowOnboarding(true);
    }
    return userData;
  };

  // Supabase Auth Methods
  const supabaseSignUp = async (email, password, metadata = {}) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: metadata }
    });
    if (error) throw error;
    return data;
  };

  const supabaseSignIn = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    });
    if (error) throw error;
    return data;
  };

  const supabaseGoogleLogin = async () => {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin
      }
    });
    if (error) throw error;
    return data;
  };

  const updatePreferences = async (preferences) => {
    if (user) {
      const updatedUser = { ...user, preferences, is_profile_completed: true };
      setUser(updatedUser);
      localStorage.setItem('staymatch_user', JSON.stringify(updatedUser));

      const userKey = user.email || user.username || user.id;
      if (userKey) {
        localStorage.setItem(`staymatch_profile_${userKey}`, JSON.stringify(preferences));
      }

      // Sync phone number and bio to backend user API if provided
      try {
        const phone = preferences.tenantPersonal?.phone || preferences.landlordPersonal?.phone;
        const bio = preferences.tenantPersonal?.cityState || preferences.landlordPersonal?.businessName;
        const updatePayload = {};
        if (phone) updatePayload.phone_number = phone;
        if (bio) updatePayload.bio = bio;
        if (Object.keys(updatePayload).length > 0) {
          await updateUserProfileApi(updatePayload);
        }
      } catch (e) {
        console.warn("Backend profile sync warning:", e);
      }
    }
    setShowOnboarding(false);
  };

  const addSentRequest = (newRequest) => {
    const updated = [newRequest, ...sentRequests];
    saveSent(updated);
  };

  const updateReceivedStatus = (requestId, newStatus) => {
    const updated = receivedRequests.map(r => r.id === requestId ? { ...r, status: newStatus } : r);
    saveReceived(updated);
  };

  const logout = async () => {
    try {
      await supabase.auth.signOut();
    } catch (e) {}
    localStorage.removeItem('staymatch_token');
    localStorage.removeItem('staymatch_user');
    localStorage.removeItem('staymatch_sent_requests');
    localStorage.removeItem('staymatch_received_requests');
    setUser(null);
    setSentRequests([]);
    setReceivedRequests([]);
    setShowOnboarding(false);
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: Boolean(user),
      login,
      register,
      oauthLogin,
      supabaseSignUp,
      supabaseSignIn,
      supabaseGoogleLogin,
      logout,
      loading,
      sentRequests,
      receivedRequests,
      landlordListings,
      addNewListing,
      addSentRequest,
      updateReceivedStatus,
      showOnboarding,
      setShowOnboarding,
      updatePreferences
    }}>
      {children}
    </AuthContext.Provider>
  );
};

