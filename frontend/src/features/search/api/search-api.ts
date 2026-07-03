import { apiClient } from '@/api/client';
import type { GlobalSearchResult, SearchParams } from '../types/search';

export const searchApi = {
  search: async (params: SearchParams): Promise<GlobalSearchResult> => {
    const response = await apiClient.get('/search', { params });
    return response.data;
  },
};
