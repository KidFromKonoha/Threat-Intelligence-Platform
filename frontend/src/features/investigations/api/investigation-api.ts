import apiClient from '@/api/client';
import type { 
  InvestigationResponse, 
  InvestigationCreate, 
  InvestigationUpdate, 
  InvestigationSummaryResponse,
  InvestigationTimelineEvent
} from '../types/investigation';

export const investigationApi = {
  getInvestigations: async (): Promise<InvestigationResponse[]> => {
    const { data } = await apiClient.get('/investigations');
    return data;
  },

  getInvestigation: async (id: string): Promise<InvestigationResponse> => {
    const { data } = await apiClient.get(`/investigations/${id}`);
    return data;
  },

  createInvestigation: async (payload: InvestigationCreate): Promise<InvestigationResponse> => {
    const { data } = await apiClient.post('/investigations', payload);
    return data;
  },

  updateInvestigation: async (id: string, payload: InvestigationUpdate): Promise<InvestigationResponse> => {
    const { data } = await apiClient.put(`/investigations/${id}`, payload);
    return data;
  },

  deleteInvestigation: async (id: string): Promise<void> => {
    await apiClient.delete(`/investigations/${id}`);
  },

  getInvestigationSummary: async (id: string): Promise<InvestigationSummaryResponse> => {
    const { data } = await apiClient.get(`/investigations/${id}/summary`);
    return data;
  },

  getInvestigationTimeline: async (id: string): Promise<InvestigationTimelineEvent[]> => {
    const { data } = await apiClient.get(`/investigations/${id}/timeline`);
    return data;
  },

  linkIndicator: async (investigationId: string, indicatorId: string): Promise<void> => {
    await apiClient.post(`/investigations/${investigationId}/indicators/${indicatorId}`);
  },

  unlinkIndicator: async (investigationId: string, indicatorId: string): Promise<void> => {
    await apiClient.delete(`/investigations/${investigationId}/indicators/${indicatorId}`);
  }
};
