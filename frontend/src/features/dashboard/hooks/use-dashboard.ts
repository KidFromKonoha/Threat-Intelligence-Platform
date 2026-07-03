import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../api/dashboard-api';

export const dashboardKeys = {
  all: ['dashboard'] as const,
  overview: () => [...dashboardKeys.all, 'overview'] as const,
  organization: () => [...dashboardKeys.all, 'organization'] as const,
  threatActivity: () => [...dashboardKeys.all, 'threatActivity'] as const,
  feedStatus: () => [...dashboardKeys.all, 'feedStatus'] as const,
  recentIntelligence: () => [...dashboardKeys.all, 'recentIntelligence'] as const,
};

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

export const useDashboardThreatActivity = () => {
  return useQuery({
    queryKey: dashboardKeys.threatActivity(),
    queryFn: dashboardApi.getThreatActivity,
  });
};

export const useDashboardFeedStatus = () => {
  return useQuery({
    queryKey: dashboardKeys.feedStatus(),
    queryFn: dashboardApi.getFeedStatus,
  });
};

export const useDashboardRecentIntelligence = () => {
  return useQuery({
    queryKey: dashboardKeys.recentIntelligence(),
    queryFn: dashboardApi.getRecentIntelligence,
  });
};
