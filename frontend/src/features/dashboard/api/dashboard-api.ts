import { apiClient } from '@/api/client';
import type {
  DashboardOverviewResponse,
  DashboardOrganizationResponse,
  DashboardThreatActivityResponse,
  DashboardFeedStatusResponse,
  DashboardRecentIntelligenceResponse,
} from '../types/dashboard';

export const dashboardApi = {
  getOverview: async (): Promise<DashboardOverviewResponse> => {
    const response = await apiClient.get('/dashboard/overview');
    return response.data;
  },

  getOrganization: async (): Promise<DashboardOrganizationResponse> => {
    const response = await apiClient.get('/dashboard/organization');
    return response.data;
  },

  getThreatActivity: async (): Promise<DashboardThreatActivityResponse> => {
    const response = await apiClient.get('/dashboard/threat-activity');
    return response.data;
  },

  getFeedStatus: async (): Promise<DashboardFeedStatusResponse> => {
    const response = await apiClient.get('/dashboard/feed-status');
    return response.data;
  },

  getRecentIntelligence: async (): Promise<DashboardRecentIntelligenceResponse> => {
    const response = await apiClient.get('/dashboard/recent-intelligence');
    return response.data;
  },
};
