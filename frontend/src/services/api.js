import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1/',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('staymatch_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Access tokens are short-lived. When one is rejected, renew it once with the refresh token and retry the
// request; if that fails the session is over and the app is told to sign the user out.
export const SESSION_EXPIRED_EVENT = 'staymatch:session-expired';
const NO_REFRESH_PATHS = ['users/login/', 'users/register/', 'users/oauth/login/', 'users/token/refresh/', 'users/logout/'];
let refreshInFlight = null;

export const saveTokens = (data) => {
  if (data?.access) localStorage.setItem('staymatch_token', data.access);
  if (data?.refresh) localStorage.setItem('staymatch_refresh', data.refresh);
};

export const clearTokens = () => {
  localStorage.removeItem('staymatch_token');
  localStorage.removeItem('staymatch_refresh');
};

const renewAccessToken = () => {
  if (!refreshInFlight) {
    const refresh = localStorage.getItem('staymatch_refresh');
    // A bare axios call, so the failure handler below cannot re-enter itself.
    refreshInFlight = axios
      .post(`${api.defaults.baseURL}users/token/refresh/`, { refresh })
      .then((res) => {
        saveTokens(res.data);
        return res.data.access;
      })
      .finally(() => {
        refreshInFlight = null;
      });
  }
  return refreshInFlight;
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const status = error.response?.status;
    const skip = !original || original._retried || NO_REFRESH_PATHS.some((p) => original.url?.includes(p));
    if (status !== 401 || skip || !localStorage.getItem('staymatch_refresh')) {
      return Promise.reject(error);
    }
    original._retried = true;
    try {
      const access = await renewAccessToken();
      original.headers.Authorization = `Bearer ${access}`;
      return api(original);
    } catch (refreshError) {
      clearTokens();
      window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
      return Promise.reject(error);
    }
  }
);

export const logoutApi = async () => {
  const refresh = localStorage.getItem('staymatch_refresh');
  if (!refresh) return;
  try {
    await api.post('users/logout/', { refresh });
  } catch (e) {
    // Signing out locally still proceeds; the refresh token expires on its own.
  }
};

export const loginUserApi = async (username, password) => {
  const response = await api.post('users/login/', { email: username, username: username, password });
  return response.data;
};

export const registerUserApi = async (userData) => {
  const response = await api.post('users/register/', userData);
  return response.data;
};

export const oauthLoginApi = async (payload) => {
  const response = await api.post('users/oauth/login/', payload);
  return response.data;
};

export const fetchCurrentUser = async () => {
  const response = await api.get('users/me/');
  return response.data;
};

export const updateUserProfileApi = async (profileData) => {
  const response = await api.patch('users/me/', profileData);
  return response.data;
};


export const fetchListings = async (params) => {
  const response = await api.get('listings/', { params });
  return response.data;
};

export const createListingApi = async (listingData) => {
  const response = await api.post('listings/', listingData);
  return response.data;
};

export const fetchApplicationsApi = async () => {
  const response = await api.get('applications/');
  return response.data;
};

export const createApplicationApi = async (applicationData) => {
  const response = await api.post('applications/', applicationData);
  return response.data;
};

export const updateApplicationStatusApi = async (applicationId, status) => {
  const response = await api.patch(`applications/${applicationId}/`, { status });
  return response.data;
};

export const fetchRecommendationsApi = async (userId) => {
  const response = await api.get(`recommendations/listings/${userId}`);
  return response.data;
};

export const fetchRoommates = async () => {
  const response = await api.get('roommates/profiles/');
  return response.data;
};

export const searchListingsHybrid = async (queryPayload) => {
  const response = await api.post('search/query', queryPayload);
  return response.data;
};

export default api;

