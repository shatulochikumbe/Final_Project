import axios from 'axios';

const API_BASE_URL = 'http://localhost:3000/api'; // Change for production

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const apiService = {
  // User management
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  completeOnboarding: (userId, profileData) => 
    api.post(`/onboarding/${userId}`, profileData),

  // Meal planning
  getMealPlan: (userId) => api.get(`/meal-plan/${userId}`),
  generateMealPlan: (userId, preferences) => 
    api.post(`/meal-plan/generate/${userId}`, preferences),

  // Progress tracking
  logProgress: (userId, progressData) => 
    api.post(`/progress/${userId}`, progressData),
  getProgress: (userId) => api.get(`/progress/${userId}`),

  // Vendor services
  getNearbyVendors: (location) => 
    api.get('/vendors/nearby', { params: location }),
  getVendorProducts: (vendorId) => 
    api.get(`/vendors/${vendorId}/products`),
};

export default apiService;