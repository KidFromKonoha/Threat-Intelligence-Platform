import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { tokenStorage } from '../../services/auth/token-storage';

export const setupInterceptors = (client: typeof axios) => {
  // Request Interceptor
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = tokenStorage.getToken();
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error: AxiosError) => {
      return Promise.reject(error);
    }
  );

  // Response Interceptor
  client.interceptors.response.use(
    (response) => {
      return response;
    },
    async (error: AxiosError) => {
      // Placeholder for future refresh token logic
      // if (error.response?.status === 401) {
      //    // handle refresh
      // }
      return Promise.reject(error);
    }
  );
};
