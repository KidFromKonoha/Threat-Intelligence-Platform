import axios from 'axios';

// VITE_API_BASE_URL is injected by vite
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const refreshClient = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Do NOT attach the response interceptor that handles 401 retries to this client.
// This client is strictly for token refresh operations to avoid infinite loops.
