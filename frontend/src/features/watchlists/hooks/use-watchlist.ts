import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { watchlistApi } from '../api/watchlist-api';
import type { WatchlistCreate, WatchlistUpdate } from '../types/watchlist';

export const WATCHLIST_KEYS = {
  all: ['watchlists'] as const,
  lists: () => [...WATCHLIST_KEYS.all, 'list'] as const,
  detail: (id: string) => [...WATCHLIST_KEYS.all, 'detail', id] as const,
  matches: () => [...WATCHLIST_KEYS.all, 'matches'] as const,
  match: (id: string) => [...WATCHLIST_KEYS.matches(), id] as const,
};

export function useWatchlists() {
  return useQuery({
    queryKey: WATCHLIST_KEYS.lists(),
    queryFn: watchlistApi.list,
  });
}

export function useWatchlist(id: string) {
  return useQuery({
    queryKey: WATCHLIST_KEYS.detail(id),
    queryFn: () => watchlistApi.get(id),
    enabled: !!id,
  });
}

export function useCreateWatchlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: WatchlistCreate) => watchlistApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: WATCHLIST_KEYS.lists() });
    },
  });
}

export function useUpdateWatchlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: WatchlistUpdate }) =>
      watchlistApi.update(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: WATCHLIST_KEYS.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: WATCHLIST_KEYS.lists() });
    },
  });
}

export function useDeleteWatchlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => watchlistApi.delete(id),
    onSuccess: (_, deletedId) => {
      queryClient.invalidateQueries({ queryKey: WATCHLIST_KEYS.lists() });
      queryClient.removeQueries({ queryKey: WATCHLIST_KEYS.detail(deletedId) });
    },
  });
}

export function useWatchlistMatches() {
  return useQuery({
    queryKey: WATCHLIST_KEYS.matches(),
    queryFn: watchlistApi.getMatches,
  });
}
