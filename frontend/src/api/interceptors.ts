import type { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { tokenStorage } from '@/services/auth/token-storage';
import { dispatchUnauthorized } from '@/services/auth/auth-events';
import { refreshClient } from './refresh-client';

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

export const setupInterceptors = (client: AxiosInstance) => {
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
      const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

      // Prevent infinite loops or intercepting non-401 errors
      if (error.response?.status !== 401 || !originalRequest || originalRequest._retry) {
        return Promise.reject(error);
      }

      // If it's the refresh endpoint itself failing, logout immediately
      if (originalRequest.url?.endsWith('/auth/refresh')) {
        tokenStorage.clearTokens();
        dispatchUnauthorized();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Queue this request and wait for the refresh to complete
        return new Promise<string>(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return client(originalRequest);
          })
          .catch((err: unknown) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = tokenStorage.getRefreshToken();
      if (!refreshToken) {
        isRefreshing = false;
        tokenStorage.clearTokens();
        dispatchUnauthorized();
        return Promise.reject(error);
      }

      try {
        // Use the dedicated refreshClient to bypass interceptors
        const response = await refreshClient.post('/auth/refresh', { refresh_token: refreshToken });
        const { access_token, refresh_token: new_refresh_token } = response.data;
        
        tokenStorage.setTokens(access_token, new_refresh_token);
        
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }
        
        processQueue(null, access_token);
        return client(originalRequest);
      } catch (refreshError: unknown) {
        processQueue(refreshError, null);
        tokenStorage.clearTokens();
        dispatchUnauthorized();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
  );
};
