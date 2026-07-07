import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { feedApi } from '../api/feed-api';
import type { FeedUpdate } from '../types/feed';

export const FEED_KEYS = {
  all: ['feeds'] as const,
  lists: () => [...FEED_KEYS.all, 'list'] as const,
  detail: (id: string) => [...FEED_KEYS.all, 'detail', id] as const,
  status: () => [...FEED_KEYS.all, 'status'] as const,
  runs: (id: string) => [...FEED_KEYS.all, 'runs', id] as const,
};

export function useFeeds() {
  return useQuery({
    queryKey: FEED_KEYS.lists(),
    queryFn: feedApi.list,
  });
}

export function useFeed(id: string) {
  return useQuery({
    queryKey: FEED_KEYS.detail(id),
    queryFn: () => feedApi.get(id),
    enabled: !!id,
  });
}

export function useFeedStatus() {
  return useQuery({
    queryKey: FEED_KEYS.status(),
    queryFn: feedApi.getStatus,
    refetchInterval: 30000, // refresh every 30s for live monitoring
  });
}

export function useFeedRuns(id: string) {
  return useQuery({
    queryKey: FEED_KEYS.runs(id),
    queryFn: () => feedApi.getRuns(id),
    enabled: !!id,
    refetchInterval: 15000, // refresh faster for recent runs
  });
}

export function useUpdateFeed() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: FeedUpdate }) => 
      feedApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: FEED_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: FEED_KEYS.detail(id) });
      queryClient.invalidateQueries({ queryKey: FEED_KEYS.status() });
    },
  });
}

export function useSyncFeed() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => feedApi.sync(id),
    onSuccess: (_, id) => {
      // Fire-and-forget invalidation to instantly show new run without blocking UI state
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: FEED_KEYS.runs(id) }).catch(() => {});
        queryClient.invalidateQueries({ queryKey: FEED_KEYS.status() }).catch(() => {});
      }, 0);
    },
  });
}
