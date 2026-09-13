import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1/',
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

export const fetchListings = async (params) => {
  const response = await api.get('listings/', { params });
  return response.data;
};

export const fetchRoommates = async () => {
  const response = await api.get('roommates/profiles/');
  return response.data;
};

export const searchListingsHybrid = async (queryPayload) => {
  const response = await axios.post('/api/v1/search/query', queryPayload);
  return response.data;
};

export default api;
