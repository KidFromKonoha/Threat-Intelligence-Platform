import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../api/dashboard-api';

export const dashboardKeys = {
  all: ['dashboard'] as const,
  overview: () => [...dashboardKeys.all, 'overview'] as const,
  organization: () => [...dashboardKeys.all, 'organization'] as const,
  feedStatus: () => [...dashboardKeys.all, 'feedStatus'] as const,
  feedContribution: () => [...dashboardKeys.all, 'feedContribution'] as const,
  threatActivity: (days: number) => [...dashboardKeys.all, 'threatActivity', days] as const,
  
  priorityQueue: () => [...dashboardKeys.all, 'priorityQueue'] as const,
  priorityAlerts: () => [...dashboardKeys.all, 'priorityAlerts'] as const,
  investigationHealth: () => [...dashboardKeys.all, 'investigationHealth'] as const,
  intelligenceHighlights: () => [...dashboardKeys.all, 'intelligenceHighlights'] as const,
  watchlistActivity: () => [...dashboardKeys.all, 'watchlistActivity'] as const,
  recentIntelligence: (skip: number, limit: number, sortBy: string, order: string, typeFilter?: string) => 
    [...dashboardKeys.all, 'recentIntelligence', skip, limit, sortBy, order, typeFilter] as const,
  iocDistribution: () => [...dashboardKeys.all, 'iocDistribution'] as const,
  geospatial: (days: number) => [...dashboardKeys.all, 'geospatial', days] as const,
  supplyChain: (days: number) => [...dashboardKeys.all, 'supplyChain', days] as const,
  
  // Legacy
  intelligenceSnapshot: () => [...dashboardKeys.all, 'intelligenceSnapshot'] as const,
  highSeverity: () => [...dashboardKeys.all, 'highSeverity'] as const,
  investigationSummary: () => [...dashboardKeys.all, 'investigationSummary'] as const,
};

// ── General Operations ────────────────────────────────────────────────────────

export const useDashboardOverview = () => {
  return useQuery({
    queryKey: dashboardKeys.overview(),
    queryFn: dashboardApi.getOverview,
  });
};

export const useDashboardOrganization = () => {
  return useQuery({
    queryKey: dashboardKeys.organization(),
    queryFn: dashboardApi.getOrganization,
  });
};

export const useDashboardFeedStatus = () => {
  return useQuery({
    queryKey: dashboardKeys.feedStatus(),
    queryFn: dashboardApi.getFeedStatus,
  });
};

export const useDashboardFeedContribution = () => {
  return useQuery({
    queryKey: dashboardKeys.feedContribution(),
    queryFn: dashboardApi.getFeedContribution,
  });
};

export const useDashboardThreatActivity = (days: number = 30) => {
  return useQuery({
    queryKey: dashboardKeys.threatActivity(days),
    queryFn: () => dashboardApi.getThreatActivity(days),
  });
};

// ── Operations ───────────────────────────────────────────────────────────────

export const useDashboardPriorityQueue = () => {
  return useQuery({
    queryKey: dashboardKeys.priorityQueue(),
    queryFn: dashboardApi.getPriorityQueue,
  });
};

export const useDashboardPriorityAlerts = (limit: number = 5, minScore: number = 50) => {
  return useQuery({
    queryKey: [...dashboardKeys.priorityAlerts(), limit, minScore],
    queryFn: () => dashboardApi.getPriorityAlerts(limit, minScore),
  });
};

export const useDashboardInvestigationHealth = () => {
  return useQuery({
    queryKey: dashboardKeys.investigationHealth(),
    queryFn: dashboardApi.getInvestigationHealth,
  });
};

// ── Intelligence ─────────────────────────────────────────────────────────────

export const useDashboardIntelligenceHighlights = () => {
  return useQuery({
    queryKey: dashboardKeys.intelligenceHighlights(),
    queryFn: dashboardApi.getIntelligenceHighlights,
  });
};

export const useDashboardWatchlistActivity = () => {
  return useQuery({
    queryKey: dashboardKeys.watchlistActivity(),
    queryFn: dashboardApi.getWatchlistActivity,
  });
};

export const useDashboardRecentIntelligence = (
  skip: number = 0,
  limit: number = 10,
  sortBy: string = 'created_at',
  order: string = 'desc',
  typeFilter?: string
) => {
  return useQuery({
    queryKey: dashboardKeys.recentIntelligence(skip, limit, sortBy, order, typeFilter),
    queryFn: () => dashboardApi.getRecentIntelligence(skip, limit, sortBy, order, typeFilter),
  });
};

export const useDashboardIocDistribution = () => {
  return useQuery({
    queryKey: dashboardKeys.iocDistribution(),
    queryFn: dashboardApi.getIocDistribution,
  });
};

// ── Deprecated/Legacy ────────────────────────────────────────────────────────

export const useDashboardIntelligenceSnapshot = () => {
  return useQuery({
    queryKey: dashboardKeys.intelligenceSnapshot(),
    queryFn: dashboardApi.getIntelligenceSnapshot,
  });
};

export const useDashboardHighSeverityIntelligence = () => {
  return useQuery({
    queryKey: dashboardKeys.highSeverity(),
    queryFn: dashboardApi.getHighSeverityIntelligence,
  });
};

export const useDashboardInvestigationSummary = () => {
  return useQuery({
    queryKey: dashboardKeys.investigationSummary(),
    queryFn: dashboardApi.getInvestigationSummary,
  });
};

export const useDashboardGeospatial = (days: number = 7) => {
  return useQuery({
    queryKey: dashboardKeys.geospatial(days),
    queryFn: () => dashboardApi.getGeospatialThreats(days),
  });
};

export const useDashboardSupplyChain = (days: number = 30) => {
  return useQuery({
    queryKey: dashboardKeys.supplyChain(days),
    queryFn: () => dashboardApi.getSupplyChainMatrix(days),
  });
};
