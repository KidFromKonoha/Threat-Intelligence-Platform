import { DashboardLayout } from './types';

export const dashboardLayouts: Record<string, DashboardLayout> = {
  admin: {
    role: 'admin',
    sections: [
      {
        id: 'overview',
        title: 'Platform Overview',
        widgets: [
          { id: 'overview', width: 'md' },
          { id: 'feed-status', width: 'md' },
          { id: 'organization', width: 'md' }
        ]
      },
      {
        id: 'operations',
        title: 'Operations & Intelligence',
        widgets: [
          { id: 'threat-activity', width: 'lg' },
          { id: 'recent-intelligence', width: 'md' }
        ]
      },
      {
        id: 'actions_status',
        title: 'Quick Actions & System Status',
        widgets: [
          { id: 'quick-actions', width: 'xl' },
          { id: 'system-status', width: 'xl' }
        ]
      }
    ]
  },
  analyst: {
    role: 'analyst',
    sections: [
      {
        id: 'operations',
        title: 'Operations',
        widgets: [
          { id: 'threat-activity', width: 'lg' },
          { id: 'recent-intelligence', width: 'md' }
        ]
      },
      {
        id: 'actions',
        title: 'Quick Actions',
        widgets: [
          { id: 'quick-actions', width: 'full' }
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
