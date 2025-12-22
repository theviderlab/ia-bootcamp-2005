import axios from 'axios';
import { API_BASE_URL } from '@constants/api';

/**
 * Base API Client
 * Configured axios instance with default settings
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Log requests in debug mode
    if (import.meta.env.VITE_ENABLE_DEBUG_MODE === 'true') {
      console.log('[API Request]', config.method.toUpperCase(), config.url, config.data);
    }
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Log responses in debug mode
    if (import.meta.env.VITE_ENABLE_DEBUG_MODE === 'true') {
      console.log('[API Response]', response.status, response.data);
    }
    return response;
  },
  (error) => {
    // Handle errors
    if (error.response) {
      // Server responded with error status
      console.error('[API Response Error]', error.response.status, error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('[API No Response]', error.request);
    } else {
      // Error setting up request
      console.error('[API Setup Error]', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
