import { apiClient } from '@/api/client';
import type {
  DashboardOverviewResponse,
  DashboardOrganizationResponse,
  DashboardThreatActivityResponse,
  DashboardFeedStatusResponse,
  DashboardRecentIntelligenceResponse,
  DashboardIntelligenceSnapshotResponse,
  DashboardHighSeverityIntelligenceResponse,
  DashboardIocDistributionResponse,
  DashboardFeedContributionResponse,
  DashboardInvestigationSummaryResponse,
  
  // Phase 2.4 types
  DashboardIntelligenceHighlightsResponse,
  DashboardPriorityQueueResponse,
  DashboardInvestigationHealthResponse,
  DashboardWatchlistActivityResponse,
  DashboardGeospatialResponse,
  DashboardSupplyChainResponse,
} from '../types/dashboard';

export const dashboardApi = {
  // ── General Operations ────────────────────────────────────────────────────────

  getOverview: async (): Promise<DashboardOverviewResponse> => {
    const response = await apiClient.get('/dashboard/overview');
    return response.data;
  },

  getOrganization: async (): Promise<DashboardOrganizationResponse> => {
    const response = await apiClient.get('/dashboard/organization');
    return response.data;
  },

  getFeedStatus: async (): Promise<DashboardFeedStatusResponse> => {
    const response = await apiClient.get('/dashboard/feed-status');
    return response.data;
  },

  getFeedContribution: async (): Promise<DashboardFeedContributionResponse> => {
    const response = await apiClient.get('/dashboard/feed-contribution');
    return response.data;
  },

  getThreatActivity: async (days: number = 30): Promise<DashboardThreatActivityResponse> => {
    const response = await apiClient.get(`/dashboard/threat-activity?days=${days}`);
    return response.data;
  },

  // ── Operations ───────────────────────────────────────────────────────────────

  getPriorityQueue: async (): Promise<DashboardPriorityQueueResponse> => {
    const response = await apiClient.get('/dashboard/operations/priority-queue');
    return response.data;
  },

  getInvestigationHealth: async (): Promise<DashboardInvestigationHealthResponse> => {
    const response = await apiClient.get('/dashboard/operations/health');
    return response.data;
  },

  getPriorityAlerts: async (limit: number = 5, minScore: number = 50): Promise<DashboardRecentIntelligenceResponse> => {
    const response = await apiClient.get(`/dashboard/alerts/priority?limit=${limit}&min_score=${minScore}`);
    return response.data;
  },

  // ── Intelligence ─────────────────────────────────────────────────────────────

  getIntelligenceHighlights: async (): Promise<DashboardIntelligenceHighlightsResponse> => {
    const response = await apiClient.get('/dashboard/intelligence/highlights');
    return response.data;
  },

  getWatchlistActivity: async (): Promise<DashboardWatchlistActivityResponse> => {
    const response = await apiClient.get('/dashboard/intelligence/watchlist-activity');
    return response.data;
  },

  getRecentIntelligence: async (
    skip: number = 0,
    limit: number = 10,
    sortBy: string = 'created_at',
    order: string = 'desc',
    typeFilter?: string
  ): Promise<DashboardRecentIntelligenceResponse> => {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
      sort_by: sortBy,
      order: order,
    });
    if (typeFilter) {
      params.append('type_filter', typeFilter);
    }
    const response = await apiClient.get(`/dashboard/intelligence/recent?${params.toString()}`);
    return response.data;
  },

  getIocDistribution: async (): Promise<DashboardIocDistributionResponse> => {
    const response = await apiClient.get('/dashboard/intelligence/ioc-distribution');
    return response.data;
  },

  // ── Deprecated/Legacy ────────────────────────────────────────────────────────
  
  getIntelligenceSnapshot: async (): Promise<DashboardIntelligenceSnapshotResponse> => {
    const response = await apiClient.get('/dashboard/intelligence-snapshot');
    return response.data;
  },

  getHighSeverityIntelligence: async (): Promise<DashboardHighSeverityIntelligenceResponse> => {
    const response = await apiClient.get('/dashboard/high-severity');
    return response.data;
  },

  getInvestigationSummary: async (): Promise<DashboardInvestigationSummaryResponse> => {
    const response = await apiClient.get('/dashboard/investigation-summary');
    return response.data;
  },

  getGeospatialThreats: async (days: number = 7): Promise<DashboardGeospatialResponse> => {
    const response = await apiClient.get('/dashboard/geospatial', { params: { days } });
    return response.data;
  },

  getSupplyChainMatrix: async (days: number = 30): Promise<DashboardSupplyChainResponse> => {
    const response = await apiClient.get('/dashboard/supply-chain', { params: { days } });
    return response.data;
  }
};
