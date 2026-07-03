import axios from 'axios';
import { setupInterceptors } from './interceptors';

// VITE_API_BASE_URL is injected by vite
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL,
  timeout: 10000, // 10 second timeout per requirement
  headers: {
    'Content-Type': 'application/json',
  },
});

setupInterceptors(apiClient);

export default apiClient;
