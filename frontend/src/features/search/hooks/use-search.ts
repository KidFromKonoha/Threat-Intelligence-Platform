import { useQuery } from '@tanstack/react-query';
import { searchApi } from '../api/search-api';
import type { SearchParams } from '../types/search';

export const searchKeys = {
  all: ['search'] as const,
  query: (params: SearchParams) => [...searchKeys.all, params] as const,
};

export const useGlobalSearch = (params: SearchParams, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: searchKeys.query(params),
    queryFn: () => searchApi.search(params),
    enabled: options?.enabled !== false && params.q.trim().length > 0,
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 1,
  });
};
