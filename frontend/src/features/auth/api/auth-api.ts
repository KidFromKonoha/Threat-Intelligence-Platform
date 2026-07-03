import { apiClient } from '@/api/client';
import type { Token, UserResponse } from '@/features/auth/types/auth';

export const authApi = {
  // Login expects application/x-www-form-urlencoded based on OAuth2PasswordRequestForm
  login: async (username: string, password: string):Promise<Token> => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    
    const response = await apiClient.post<Token>('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<UserResponse> => {
    const response = await apiClient.get<UserResponse>('/auth/me');
    return response.data;
  }
};
