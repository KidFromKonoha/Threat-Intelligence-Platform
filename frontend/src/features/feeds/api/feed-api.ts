import { apiClient } from '@/api/client';
import type {
  FeedResponse,
  FeedUpdate,
  FeedRunResponse,
  FeedStatusDetail,
} from '../types/feed';

export const feedApi = {
  list: async (): Promise<FeedResponse[]> => {
    const response = await apiClient.get('/feeds');
    return response.data;
  },

  get: async (id: string): Promise<FeedResponse> => {
    const response = await apiClient.get(`/feeds/${id}`);
    return response.data;
  },

  create: async (data: Omit<FeedResponse, 'id' | 'created_at' | 'updated_at' | 'status' | 'records_imported'>): Promise<FeedResponse> => {
    const response = await apiClient.post('/feeds', data);
    return response.data;
  },

  update: async (id: string, data: FeedUpdate): Promise<FeedResponse> => {
    const response = await apiClient.put(`/feeds/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/feeds/${id}`);
  },

  sync: async (id: string): Promise<FeedRunResponse> => {
    const response = await apiClient.post(`/feeds/${id}/run`, undefined);
    return response.data;
  },

  getRuns: async (id: string): Promise<FeedRunResponse[]> => {
    const response = await apiClient.get(`/feeds/${id}/runs`);
    return response.data;
  },

  getStatus: async (): Promise<FeedStatusDetail[]> => {
    const response = await apiClient.get('/feeds/status');
    return response.data;
  },
};
