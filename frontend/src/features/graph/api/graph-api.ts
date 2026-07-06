import apiClient from '@/api/client';
import type { GraphResponse, GraphEntityType } from '../types/graph';

const entityTypeToPath: Partial<Record<GraphEntityType, string>> = {
  indicator: 'indicator',
  threat_actor: 'threat-actor',
  malware: 'malware',
  campaign: 'campaign',
  investigation: 'investigation',
};

export const graphApi = {
  getGraph: async (entityType: GraphEntityType, id: string, depth?: number): Promise<GraphResponse> => {
    const path = entityTypeToPath[entityType];
    if (!path) throw new Error(`Unsupported entity type for graph: ${entityType}`);
    const params = depth !== undefined ? { depth } : {};
    const { data } = await apiClient.get(`/graph/${path}/${id}`, { params });
    return data;
  },

  getIndicatorGraph: async (id: string, depth?: number): Promise<GraphResponse> => {
    const { data } = await apiClient.get(`/graph/indicator/${id}`, { params: depth ? { depth } : {} });
    return data;
  },

  getThreatActorGraph: async (id: string, depth?: number): Promise<GraphResponse> => {
    const { data } = await apiClient.get(`/graph/threat-actor/${id}`, { params: depth ? { depth } : {} });
    return data;
  },

  getMalwareGraph: async (id: string, depth?: number): Promise<GraphResponse> => {
    const { data } = await apiClient.get(`/graph/malware/${id}`, { params: depth ? { depth } : {} });
    return data;
  },

  getCampaignGraph: async (id: string, depth?: number): Promise<GraphResponse> => {
    const { data } = await apiClient.get(`/graph/campaign/${id}`, { params: depth ? { depth } : {} });
    return data;
  },

  getInvestigationGraph: async (id: string, depth?: number): Promise<GraphResponse> => {
    const { data } = await apiClient.get(`/graph/investigation/${id}`, { params: depth ? { depth } : {} });
    return data;
  },
};
