import { apiClient } from '@/api/client';
import type {
  WatchlistResponse,
  WatchlistCreate,
  WatchlistUpdate,
  WatchlistMatchResponse,
} from '../types/watchlist';

export const watchlistApi = {
  list: async (): Promise<WatchlistResponse[]> => {
    const response = await apiClient.get('/watchlists');
    return response.data;
  },

  get: async (id: string): Promise<WatchlistResponse> => {
    const response = await apiClient.get(`/watchlists/${id}`);
    return response.data;
  },

  create: async (data: WatchlistCreate): Promise<WatchlistResponse> => {
    const response = await apiClient.post('/watchlists', data);
    return response.data;
  },

  update: async (id: string, data: WatchlistUpdate): Promise<WatchlistResponse> => {
    const response = await apiClient.put(`/watchlists/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/watchlists/${id}`);
  },

  evaluate: async (id: string): Promise<void> => {
    await apiClient.post(`/watchlists/${id}/evaluate`, undefined);
  },

  getMatches: async (): Promise<WatchlistMatchResponse[]> => {
    const response = await apiClient.get('/watchlists/matches');
    return response.data;
  },

  getMatch: async (matchId: string): Promise<WatchlistMatchResponse> => {
    const response = await apiClient.get(`/watchlists/matches/${matchId}`);
    return response.data;
  },
};
