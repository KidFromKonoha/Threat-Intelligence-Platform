import { createBrowserRouter, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { AppLayout } from '../layouts/app-layout';
import { ProtectedRoute } from '../components/layout/protected-route';
import { LoginPage } from '../features/auth/pages/login-page';

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
  <div className="flex-1 flex items-center justify-center">
    <div className="flex flex-col items-center gap-3 text-muted-foreground">
      <div className="w-6 h-6 border-2 border-current border-t-transparent rounded-full animate-spin opacity-50" />
    </div>
  </div>
);

const Wrap = ({ children }: { children: React.ReactNode }) => (
  <Suspense fallback={<PageFallback />}>{children}</Suspense>
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
            element: <Wrap><WatchlistsPage /></Wrap>,
          },
          {
            path: 'watchlists/:id',
            element: <Wrap><WatchlistDetailPage /></Wrap>,
          },
          {
            path: 'reports',
            element: <Wrap><ReportsPage /></Wrap>,
          },
          {
            path: 'feeds',
            element: <Wrap><FeedsPage /></Wrap>,
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
            element: <Wrap><IndicatorPage /></Wrap>,
          },
          {
            path: 'entities/threat-actor/:id',
            element: <Wrap><ThreatActorPage /></Wrap>,
          },
          {
            path: 'entities/malware/:id',
            element: <Wrap><MalwarePage /></Wrap>,
          },
          {
            path: 'entities/campaign/:id',
            element: <Wrap><CampaignPage /></Wrap>,
          },
          {
            path: 'entities/vulnerability/:id',
            element: <Wrap><VulnerabilityPage /></Wrap>,
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
