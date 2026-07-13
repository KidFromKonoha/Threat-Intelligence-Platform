import { widgetRegistry } from './registry';
import { dashboardLayouts } from './layouts';

// Import existing cards/components
import { OverviewCard } from '../components/overview-card';
import { FeedStatusCard } from '../components/feed-status-card';
import { OrganizationCard } from '../components/organization-card';
import { ThreatActivityCard } from '../components/threat-activity-card';
import { RecentIntelligenceCard } from '../components/recent-intelligence-card';

// Import new widgets
import { QuickActionsWidget } from '../widgets/quick-actions-widget';
import { SystemStatusWidget } from '../widgets/system-status-widget';

export const registerDashboardWidgets = () => {
  widgetRegistry.register({
    id: 'overview',
    title: 'Platform Overview',
    description: 'High level metrics of the platform',
    supportedRoles: ['admin', 'executive', 'analyst'],
    defaultWidth: 'md',
    priority: 100,
    component: OverviewCard,
  });

  widgetRegistry.register({
    id: 'feed-status',
    title: 'Feed Status',
    description: 'Status of intelligence feeds',
    supportedRoles: ['admin'],
    defaultWidth: 'md',
    priority: 90,
    component: FeedStatusCard,
  });

  widgetRegistry.register({
    id: 'organization',
    title: 'Organization Risk',
    description: 'Risk metrics for the organization',
    supportedRoles: ['admin', 'executive'],
    defaultWidth: 'md',
    priority: 80,
    component: OrganizationCard,
  });

  widgetRegistry.register({
    id: 'threat-activity',
    title: 'Threat Activity',
    description: 'Timeline of threat activities',
    supportedRoles: ['admin', 'executive', 'analyst'],
    defaultWidth: 'lg',
    priority: 70,
    component: ThreatActivityCard,
  });

  widgetRegistry.register({
    id: 'recent-intelligence',
    title: 'Recent Intelligence',
    description: 'Recently imported indicators and reports',
    supportedRoles: ['admin', 'analyst'],
    defaultWidth: 'md',
    priority: 60,
    component: RecentIntelligenceCard,
  });

  widgetRegistry.register({
    id: 'quick-actions',
    title: 'Quick Actions',
    description: 'Shortcuts to common tasks',
    supportedRoles: ['admin', 'analyst'],
    defaultWidth: 'xl',
    priority: 50,
    component: QuickActionsWidget,
  });

  widgetRegistry.register({
    id: 'system-status',
    title: 'System Status',
    description: 'Health of platform services',
    supportedRoles: ['admin'],
    defaultWidth: 'xl',
    priority: 40,
    component: SystemStatusWidget,
  });
};

export { widgetRegistry, dashboardLayouts };
export * from './types';
