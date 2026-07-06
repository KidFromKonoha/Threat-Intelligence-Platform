import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { investigationApi } from '../api/investigation-api';
import type { InvestigationCreate, InvestigationUpdate } from '../types/investigation';

export const investigationKeys = {
  all: ['investigations'] as const,
  lists: () => [...investigationKeys.all, 'list'] as const,
  list: (filters: string) => [...investigationKeys.lists(), { filters }] as const,
  details: () => [...investigationKeys.all, 'detail'] as const,
  detail: (id: string) => [...investigationKeys.details(), id] as const,
  summaries: () => [...investigationKeys.all, 'summary'] as const,
  summary: (id: string) => [...investigationKeys.summaries(), id] as const,
  timelines: () => [...investigationKeys.all, 'timeline'] as const,
  timeline: (id: string) => [...investigationKeys.timelines(), id] as const,
};

export const useInvestigations = () => {
  return useQuery({
    queryKey: investigationKeys.lists(),
    queryFn: () => investigationApi.getInvestigations(),
  });
};

export const useInvestigation = (id: string) => {
  return useQuery({
    queryKey: investigationKeys.detail(id),
    queryFn: () => investigationApi.getInvestigation(id),
    enabled: !!id,
  });
};

export const useInvestigationSummary = (id: string) => {
  return useQuery({
    queryKey: investigationKeys.summary(id),
    queryFn: () => investigationApi.getInvestigationSummary(id),
    enabled: !!id,
  });
};

export const useInvestigationTimeline = (id: string) => {
  return useQuery({
    queryKey: investigationKeys.timeline(id),
    queryFn: () => investigationApi.getInvestigationTimeline(id),
    enabled: !!id,
  });
};

export const useCreateInvestigation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (payload: InvestigationCreate) => investigationApi.createInvestigation(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: investigationKeys.lists() });
    },
  });
};

export const useUpdateInvestigation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: InvestigationUpdate }) => investigationApi.updateInvestigation(id, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: investigationKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: investigationKeys.lists() });
    },
  });
};

export const useDeleteInvestigation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => investigationApi.deleteInvestigation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: investigationKeys.lists() });
    },
  });
};

export const useLinkIndicator = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ investigationId, indicatorId }: { investigationId: string, indicatorId: string }) => investigationApi.linkIndicator(investigationId, indicatorId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: investigationKeys.summary(variables.investigationId) });
    },
  });
};

export const useUnlinkIndicator = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ investigationId, indicatorId }: { investigationId: string, indicatorId: string }) => investigationApi.unlinkIndicator(investigationId, indicatorId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: investigationKeys.summary(variables.investigationId) });
    },
  });
};
