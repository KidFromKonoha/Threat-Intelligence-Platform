import type { DashboardLayout } from './types';

export const dashboardLayouts: Record<string, DashboardLayout> = {
  admin: {
    role: 'admin',
    sections: [
      {
        id: 'platform_core',
        title: 'Platform Operations',
        widgets: [
          { id: 'overview', width: 'xl' },
          { id: 'feed-status', width: 'xl' },
          { id: 'quick-actions', width: 'full' }
        ]
      },

      {
        id: 'highlights',
        widgets: [
          { id: 'intelligence-highlights', width: 'full' }
        ]
      },
      {
        id: 'operations_triage',
        title: 'Triage & Investigations',
        widgets: [
          { id: 'automotive-alert', width: 'full' },
          { id: 'priority-queue', width: 'lg' },
          { id: 'investigation-health', width: 'md' },
          { id: 'investigation-summary', width: 'md' }
        ]
      },
      {
        id: 'intelligence_activity',
        title: 'Intelligence Activity',
        widgets: [
          { id: 'watchlist-activity', width: 'md' },
          { id: 'ioc-distribution', width: 'md' },
          { id: 'threat-activity', width: 'xl' },
          { id: 'high-severity', width: 'md' },
          { id: 'feed-contribution', width: 'md' }
        ]
      },
      {
        id: 'recent',
        title: 'Recent Intelligence',
        widgets: [
          { id: 'recent-intelligence', width: 'full' },
          { id: 'intelligence-snapshot', width: 'full' }
        ]
      }
    ]
  },
  analyst: {
    role: 'analyst',
    sections: [
      {
        id: 'highlights',
        widgets: [
          { id: 'intelligence-highlights', width: 'full' }
        ]
      },
      {
        id: 'operations_triage',
        widgets: [
          { id: 'automotive-alert', width: 'full' },
          { id: 'priority-queue', width: 'lg' },
          { id: 'investigation-health', width: 'md' }
        ]
      },
      {
        id: 'intelligence_activity',
        title: 'Intelligence Activity',
        widgets: [
          { id: 'watchlist-activity', width: 'md' },
          { id: 'ioc-distribution', width: 'md' },
          { id: 'threat-activity', width: 'xl' }
        ]
      },
      {
        id: 'recent',
        widgets: [
          { id: 'recent-intelligence', width: 'full' }
        ]
      }
    ]
  },
  executive: {
    role: 'executive',
    sections: [
      {
        id: 'overview',
        title: 'Executive Summary',
        widgets: [
          { id: 'overview', width: 'xl' },
          { id: 'organization', width: 'xl' },
          { id: 'threat-activity', width: 'full' }
        ]
      }
    ]
  }
};
