import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1, // Only retry once by default
      refetchOnWindowFocus: false, // Don't fetch on every tab switch
      refetchOnMount: true,
    },
  },
});
