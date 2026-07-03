import React, { createContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';
import { tokenStorage } from '@/services/auth/token-storage';
import type { UserResponse } from '@/features/auth/types/auth';
import { authApi } from '@/features/auth/api/auth-api';
import { AUTH_EVENTS } from '@/services/auth/auth-events';
import { queryClient } from '@/app/query-client';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserResponse | null;
  login: (accessToken: string, refreshToken: string, user: UserResponse) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const performLogout = useCallback(() => {
    tokenStorage.clearTokens();
    setIsAuthenticated(false);
    setUser(null);
    queryClient.clear();
  }, []);

  useEffect(() => {
    // Listen for unauthorized events from the Axios interceptor
    const handleUnauthorized = () => {
      performLogout();
    };

    window.addEventListener(AUTH_EVENTS.UNAUTHORIZED, handleUnauthorized);
    return () => {
      window.removeEventListener(AUTH_EVENTS.UNAUTHORIZED, handleUnauthorized);
    };
  }, [performLogout]);

  useEffect(() => {
    const initAuth = async () => {
      const token = tokenStorage.getToken();
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const currentUser = await authApi.getCurrentUser();
        setUser(currentUser);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Failed to restore session:', error);
        performLogout();
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, [performLogout]);

  const login = useCallback((accessToken: string, refreshToken: string, loggedInUser: UserResponse) => {
    tokenStorage.setTokens(accessToken, refreshToken);
    setUser(loggedInUser);
    setIsAuthenticated(true);
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, user, login, logout: performLogout }}>
      {children}
    </AuthContext.Provider>
  );
};
