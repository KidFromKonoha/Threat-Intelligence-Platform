import { useQuery } from '@tanstack/react-query';
import { entityApi } from '../api/entity-api';

export const entityKeys = {
  all: ['entity'] as const,
  indicator: (id: string) => [...entityKeys.all, 'indicator', id] as const,
  threatActor: (id: string) => [...entityKeys.all, 'threatActor', id] as const,
  malware: (id: string) => [...entityKeys.all, 'malware', id] as const,
  campaign: (id: string) => [...entityKeys.all, 'campaign', id] as const,
  vulnerability: (id: string) => [...entityKeys.all, 'vulnerability', id] as const,
};

export const useIndicator = (id: string) => {
  return useQuery({
    queryKey: entityKeys.indicator(id),
    queryFn: () => entityApi.getIndicator(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
  });
};

export const useThreatActor = (id: string) => {
  return useQuery({
    queryKey: entityKeys.threatActor(id),
    queryFn: () => entityApi.getThreatActor(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
  });
};

export const useMalware = (id: string) => {
  return useQuery({
    queryKey: entityKeys.malware(id),
    queryFn: () => entityApi.getMalware(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
  });
};

export const useCampaign = (id: string) => {
  return useQuery({
    queryKey: entityKeys.campaign(id),
    queryFn: () => entityApi.getCampaign(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
  });
};

export const useVulnerability = (id: string) => {
  return useQuery({
    queryKey: entityKeys.vulnerability(id),
    queryFn: () => entityApi.getVulnerability(id),
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
  });
};
