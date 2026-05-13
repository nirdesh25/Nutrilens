import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (data: { name: string; email: string; password: string; age?: number }) =>
    api.post('/api/auth/register', data),
  
  login: (data: { email: string; password: string }) =>
    api.post('/api/auth/login', data),
};

// Scan API
export const scanAPI = {
  predictFreshness: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/scan/predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  getHistory: () => api.get('/api/scan/history'),
  
  getWasteDecision: (scanId: number) =>
    api.get(`/api/scan/waste-decision/${scanId}`),
};

// Grocery API
export const groceryAPI = {
  getAll: () => api.get('/api/groceries'),
  
  create: (data: {
    food_name: string;
    category?: string;
    quantity?: number;
    freshness_status?: string;
  }) => api.post('/api/groceries', data),
  
  update: (id: number, data: any) => api.put(`/api/groceries/${id}`, data),
  
  delete: (id: number) => api.delete(`/api/groceries/${id}`),
};

// Health API
export const healthAPI = {
  getProfile: () => api.get('/api/health/profile'),
  
  createProfile: (data: {
    diabetes?: boolean;
    high_bp?: boolean;
    cholesterol?: boolean;
    surgery_recovery?: boolean;
    weight_loss?: boolean;
  }) => api.post('/api/health/profile', data),
  
  updateProfile: (data: any) => api.put('/api/health/profile', data),
  
  getRecommendations: () => api.get('/api/health/recommendations'),
};

// Waste API
export const wasteAPI = {
  logAction: (data: { food_name: string; action: string; co2_saved: number }) =>
    api.post('/api/waste/log', data),
  
  getLogs: () => api.get('/api/waste/logs'),
  
  getAnalytics: () => api.get('/api/waste/analytics'),
};

// Sensor API (Smart Freshness Box)
export const sensorAPI = {
  getCurrent: () => api.get('/api/sensor/current'),
  
  getHistory: (hours: number = 24) =>
    api.get(`/api/sensor/history?hours=${hours}`),
  
  getStatus: () => api.get('/api/sensor/status'),
  
  analyzeMilkQuality: (data: {
    ph: number;
    temperature: number;
    taste: number;
    odor: number;
    fat: number;
    turbidity: number;
    color: number;
  }) => api.post('/api/sensor/milk-quality', data),
};

// pH Analysis API
export const phAPI = {
  analyze: (file: File, foodType: string = 'default') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('food_type', foodType);
    return api.post('/api/ph/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  getFoodTypes: () => api.get('/api/ph/food-types'),
};

// User API
export const userAPI = {
  getProfile: () => api.get('/api/user/profile'),
  
  updateProfile: (data: { age?: number }) => api.put('/api/user/profile', data),

  getStats: () => api.get('/api/user/stats'),
};

