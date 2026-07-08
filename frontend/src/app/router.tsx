import { createBrowserRouter, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { AppLayout } from '../layouts/app-layout';
import { ProtectedRoute } from '../components/layout/protected-route';
import { LoginPage } from '../features/auth/pages/login-page';
import { Skeleton } from '../components/ui/skeleton';
import { EntitySkeleton } from '../features/entity-details/components/entity-skeleton';
import { FeedSkeleton } from '../features/feeds/components/feed-skeleton';
import { ReportSkeleton } from '../features/reports/components/report-skeleton';
import { WatchlistSkeleton } from '../features/watchlists/components/watchlist-skeleton';

// Route-level code splitting for better initial load performance
const DashboardPage = lazy(() => import('../features/dashboard/pages/dashboard-page').then(m => ({ default: m.DashboardPage })));
const SearchPage = lazy(() => import('../features/search/pages/search-page').then(m => ({ default: m.SearchPage })));
const InvestigationsPage = lazy(() => import('../features/investigations/pages/investigations-page').then(m => ({ default: m.InvestigationsPage })));
const InvestigationDetailPage = lazy(() => import('../features/investigations/pages/investigation-detail-page').then(m => ({ default: m.InvestigationDetailPage })));
const FeedsPage = lazy(() => import('../features/feeds/pages/feeds-page').then(m => ({ default: m.FeedsPage })));
const FeedDetailPage = lazy(() => import('../features/feeds/pages/feed-detail-page').then(m => ({ default: m.FeedDetailPage })));
const SettingsPage = lazy(() => import('../features/settings/pages/settings-page').then(m => ({ default: m.SettingsPage })));
const NotFoundPage = lazy(() => import('../features/errors/pages/not-found-page').then(m => ({ default: m.NotFoundPage })));

// Entity Detail Pages
const IndicatorPage = lazy(() => import('../features/entity-details/pages/indicator-page').then(m => ({ default: m.IndicatorPage })));
const ThreatActorPage = lazy(() => import('../features/entity-details/pages/threat-actor-page').then(m => ({ default: m.ThreatActorPage })));
const MalwarePage = lazy(() => import('../features/entity-details/pages/malware-page').then(m => ({ default: m.MalwarePage })));
const CampaignPage = lazy(() => import('../features/entity-details/pages/campaign-page').then(m => ({ default: m.CampaignPage })));
const VulnerabilityPage = lazy(() => import('../features/entity-details/pages/vulnerability-page').then(m => ({ default: m.VulnerabilityPage })));

// Graph
const GraphPage = lazy(() => import('../features/graph/pages/graph-page').then(m => ({ default: m.GraphPage })));

// Watchlists
const WatchlistsPage = lazy(() => import('../features/watchlists/pages/watchlists-page').then(m => ({ default: m.WatchlistsPage })));
const WatchlistDetailPage = lazy(() => import('../features/watchlists/pages/watchlist-detail-page').then(m => ({ default: m.WatchlistDetailPage })));

// Reports
const ReportsPage = lazy(() => import('../features/reports/pages/reports-page').then(m => ({ default: m.ReportsPage })));

const PageFallback = () => (
  <div className="flex-1 p-6 flex flex-col gap-6 w-full">
    <div className="flex items-center justify-between">
      <div className="space-y-2">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-64" />
      </div>
      <div className="flex gap-2">
        <Skeleton className="h-9 w-24" />
        <Skeleton className="h-9 w-32" />
      </div>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Skeleton className="h-32 w-full rounded-xl" />
      <Skeleton className="h-32 w-full rounded-xl" />
      <Skeleton className="h-32 w-full rounded-xl" />
    </div>
    <div className="flex-1">
      <Skeleton className="h-96 w-full rounded-xl" />
    </div>
  </div>
);

const EntityFallback = () => <div className="p-6 max-w-7xl mx-auto w-full"><EntitySkeleton /></div>;
const FeedFallback = () => <div className="flex-1 p-6 w-full"><FeedSkeleton /></div>;
const WatchlistFallback = () => <div className="flex-1 p-6 w-full"><WatchlistSkeleton /></div>;
const ReportFallback = () => <div className="flex-1 p-6 w-full"><ReportSkeleton /></div>;

const Wrap = ({ children, fallback }: { children: React.ReactNode, fallback?: React.ReactNode }) => (
  <Suspense fallback={fallback || <PageFallback />}>{children}</Suspense>
);

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      {
        element: <AppLayout />,
        children: [
          {
            index: true,
            element: <Navigate to="/dashboard" replace />,
          },
          {
            path: 'dashboard',
            element: <Wrap><DashboardPage /></Wrap>,
          },
          {
            path: 'search',
            element: <Wrap><SearchPage /></Wrap>,
          },
          {
            path: 'investigations',
            element: <Wrap><InvestigationsPage /></Wrap>,
          },
          {
            path: 'investigations/:id',
            element: <Wrap><InvestigationDetailPage /></Wrap>,
          },
          {
            path: 'watchlists',
            element: <Wrap fallback={<WatchlistFallback />}><WatchlistsPage /></Wrap>,
          },
          {
            path: 'watchlists/:id',
            element: <Wrap fallback={<WatchlistFallback />}><WatchlistDetailPage /></Wrap>,
          },
          {
            path: 'reports',
            element: <Wrap fallback={<ReportFallback />}><ReportsPage /></Wrap>,
          },
          {
            path: 'feeds',
            element: <Wrap fallback={<FeedFallback />}><FeedsPage /></Wrap>,
          },
          {
            path: 'feeds/:id',
            element: <Wrap><FeedDetailPage /></Wrap>,
          },
          {
            path: 'settings',
            element: <Wrap><SettingsPage /></Wrap>,
          },
          {
            path: 'threat-graph',
            element: <Wrap><GraphPage /></Wrap>,
          },
          {
            path: 'threat-graph/:entityType/:id',
            element: <Wrap><GraphPage /></Wrap>,
          },
          {
            path: 'entities/indicator/:id',
            element: <Wrap fallback={<EntityFallback />}><IndicatorPage /></Wrap>,
          },
          {
            path: 'entities/threat-actor/:id',
            element: <Wrap fallback={<EntityFallback />}><ThreatActorPage /></Wrap>,
          },
          {
            path: 'entities/malware/:id',
            element: <Wrap fallback={<EntityFallback />}><MalwarePage /></Wrap>,
          },
          {
            path: 'entities/campaign/:id',
            element: <Wrap fallback={<EntityFallback />}><CampaignPage /></Wrap>,
          },
          {
            path: 'entities/vulnerability/:id',
            element: <Wrap fallback={<EntityFallback />}><VulnerabilityPage /></Wrap>,
          },
          {
            path: '*',
            element: <Wrap><NotFoundPage /></Wrap>,
          },
        ],
      },
    ],
  },
]);
