import { apiClient } from '@/api/client';
import type { 
  IndicatorFullDetailResponse, 
  ThreatActorDetailResponse, 
  MalwareDetailResponse, 
  CampaignDetailResponse, 
  VulnerabilityDetailResponse 
} from '../types/entity';

export const entityApi = {
  getIndicator: async (id: string): Promise<IndicatorFullDetailResponse> => {
    const response = await apiClient.get(`/indicators/${id}`);
    return response.data;
  },

  getThreatActor: async (id: string): Promise<ThreatActorDetailResponse> => {
    const response = await apiClient.get(`/threat-actors/${id}`);
    return response.data;
  },

  getMalware: async (id: string): Promise<MalwareDetailResponse> => {
    const response = await apiClient.get(`/malware/${id}`);
    return response.data;
  },

  getCampaign: async (id: string): Promise<CampaignDetailResponse> => {
    const response = await apiClient.get(`/campaigns/${id}`);
    return response.data;
  },

  getVulnerability: async (id: string): Promise<VulnerabilityDetailResponse> => {
    const response = await apiClient.get(`/vulnerabilities/${id}`);
    return response.data;
  },
};
