import { createClient } from '@supabase/supabase-js';

// Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY (the project's public "anon" key) in frontend/.env.
// Nothing is baked into the source: without them, Google sign-in is switched off and the rest of the app
// (email and password accounts) keeps working.
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey);

const notConfigured = async () => ({
  data: null,
  error: new Error('Sign-in with Supabase is not configured. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.'),
});

// Same shape as the parts of supabase.auth the app uses, so callers need no special cases.
const disabledClient = {
  auth: {
    getSession: async () => ({ data: { session: null }, error: null }),
    onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }),
    signInWithOAuth: notConfigured,
    signInWithPassword: notConfigured,
    signUp: notConfigured,
    signOut: async () => ({ error: null }),
  },
};

export const supabase = supabaseConfigured
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    })
  : disabledClient;

export default supabase;
