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

