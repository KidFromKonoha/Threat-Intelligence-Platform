import { widgetRegistry } from './registry';
import { dashboardLayouts } from './layouts';

// Existing Widgets (Administrator)
import { OverviewCard } from '../components/overview-card';
import { FeedStatusCard } from '../components/feed-status-card';
import { OrganizationCard } from '../components/organization-card';

// Shared / Action Widgets
import { QuickActionsWidget } from '../widgets/quick-actions-widget';
import { SystemStatusWidget } from '../widgets/system-status-widget';

// Phase 2.3 Legacy / Threat Hunter
import { IntelligenceSnapshotWidget } from '../widgets/intelligence-snapshot-widget';
import { HighSeverityWidget } from '../widgets/high-severity-widget';
import { ThreatActivityWidget } from '../widgets/threat-activity-widget';
import { FeedContributionWidget } from '../widgets/feed-contribution-widget';
import { InvestigationSummaryWidget } from '../widgets/investigation-summary-widget';

// New Phase 2.4 Widgets (Analyst)
import { IntelligenceHighlightsWidget } from '../widgets/intelligence-highlights-widget';
import { PriorityQueueWidget } from '../widgets/priority-queue-widget';
import { InvestigationHealthWidget } from '../widgets/investigation-health-widget';
import { WatchlistActivityWidget } from '../widgets/watchlist-activity-widget';
import { RecentIntelligenceWidget } from '../widgets/recent-intelligence-widget';
import { IocDistributionWidget } from '../widgets/ioc-distribution-widget';
import { AutomotiveAlertWidget } from '../widgets/automotive-alert-widget';

// Phase 1 Redesign
import { GeospatialMapWidget } from '../widgets/geospatial-map-widget';
import { SupplyChainMatrixWidget } from '../widgets/supply-chain-matrix-widget';

export const registerDashboardWidgets = () => {
  // ── Existing Cards (Admin Focus) ────────────────────────────────────────────
  widgetRegistry.register({
    id: 'overview',
    title: 'Platform Overview',
    supportedRoles: ['admin', 'executive'],
    defaultWidth: 'md',
    priority: 100,
    component: OverviewCard,
  });

  widgetRegistry.register({
    id: 'feed-status',
    title: 'Feed Status',
    supportedRoles: ['admin'],
    defaultWidth: 'md',
    priority: 90,
    component: FeedStatusCard,
  });

  widgetRegistry.register({
    id: 'automotive-alert',
    title: 'Automotive Priority Alerts',
    supportedRoles: ['admin', 'analyst'],
    defaultWidth: 'lg',
    priority: 85,
    component: AutomotiveAlertWidget,
  });

  widgetRegistry.register({
    id: 'organization',
    title: 'Organization Risk',
    supportedRoles: ['admin', 'executive'],
    defaultWidth: 'md',
    priority: 80,
    component: OrganizationCard,
  });

  widgetRegistry.register({
    id: 'quick-actions',
    title: 'Quick Actions',
    supportedRoles: ['admin'],
    defaultWidth: 'xl',
    priority: 50,
    component: QuickActionsWidget,
  });

  widgetRegistry.register({
    id: 'system-status',
    title: 'System Status',
    supportedRoles: ['admin'],
    defaultWidth: 'xl',
    priority: 40,
    component: SystemStatusWidget,
  });

  // ── Phase 2.4 Widgets (Analyst Focus) ───────────────────────────────────────
  widgetRegistry.register({
    id: 'intelligence-highlights',
    title: 'Intelligence Highlights',
    supportedRoles: ['analyst', 'admin'],
    defaultWidth: 'full',
    priority: 200,
    component: IntelligenceHighlightsWidget,
  });

  widgetRegistry.register({
    id: 'priority-queue',
    title: 'Priority Queue',
    supportedRoles: ['analyst', 'admin'],
    defaultWidth: 'md',
    priority: 190,
    component: PriorityQueueWidget,
  });

  widgetRegistry.register({
    id: 'investigation-health',
    title: 'Investigation Health',
    supportedRoles: ['analyst', 'admin'],
    defaultWidth: 'md',
    priority: 180,
    component: InvestigationHealthWidget,
  });

  widgetRegistry.register({
    id: 'watchlist-activity',
    title: 'Watchlist Activity',
    supportedRoles: ['analyst', 'admin'],
    defaultWidth: 'md',
    priority: 170,
    component: WatchlistActivityWidget,
  });

  widgetRegistry.register({
    id: 'ioc-distribution',
    component: IocDistributionWidget,
    supportedRoles: ['analyst', 'admin']
  });

  // ── Phase 1 Redesign ────────────────────────────────────────────────────────
  widgetRegistry.register({
    id: 'geospatial-map',
    component: GeospatialMapWidget,
    supportedRoles: ['admin', 'analyst', 'executive']
  });

  widgetRegistry.register({
    id: 'supply-chain-matrix',
    component: SupplyChainMatrixWidget,
    supportedRoles: ['admin', 'executive']
  });

  widgetRegistry.register({
    id: 'recent-intelligence',
    title: 'Recent Intelligence',
    supportedRoles: ['analyst', 'admin'],
    defaultWidth: 'full',
    priority: 150,
    component: RecentIntelligenceWidget,
  });

  // ── Phase 2.3 Legacy ────────────────────────────────────────────────────────
  widgetRegistry.register({
    id: 'intelligence-snapshot',
    title: 'Intelligence Snapshot',
    supportedRoles: ['analyst', 'admin'],
    defaultWidth: 'full',
    priority: 140,
    component: IntelligenceSnapshotWidget,
  });

  widgetRegistry.register({
    id: 'high-severity',
    title: 'High Severity Intel',
    supportedRoles: ['analyst', 'admin'],
    defaultWidth: 'md',
    priority: 130,
    component: HighSeverityWidget,
  });

  widgetRegistry.register({
    id: 'threat-activity',
    title: 'Threat Activity',
    supportedRoles: ['analyst', 'admin'],
    defaultWidth: 'lg',
    priority: 110,
    component: ThreatActivityWidget,
  });

  widgetRegistry.register({
    id: 'feed-contribution',
    title: 'Feed Contribution',
    supportedRoles: ['analyst', 'admin'],
    defaultWidth: 'md',
    priority: 100,
    component: FeedContributionWidget,
  });

  widgetRegistry.register({
    id: 'investigation-summary',
    title: 'Investigation Summary',
    supportedRoles: ['analyst', 'admin'],
    defaultWidth: 'md',
    priority: 90,
    component: InvestigationSummaryWidget,
  });
};

export { widgetRegistry, dashboardLayouts };
export * from './types';
