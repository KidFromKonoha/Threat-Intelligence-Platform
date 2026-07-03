import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AppLayout } from '../layouts/app-layout';
import { ProtectedRoute } from '../components/layout/protected-route';
import { DashboardPage } from '../features/dashboard/pages/dashboard-page';
import { SearchPage } from '../features/search/pages/search-page';
import { InvestigationsPage } from '../features/investigations/pages/investigations-page';
import { WatchlistsPage } from '../features/watchlists/pages/watchlists-page';
import { ReportsPage } from '../features/reports/pages/reports-page';
import { FeedsPage } from '../features/feeds/pages/feeds-page';
import { SettingsPage } from '../features/settings/pages/settings-page';
import { LoginPage } from '../features/auth/pages/login-page';
import { NotFoundPage } from '../features/errors/pages/not-found-page';

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
            element: <DashboardPage />,
          },
          {
            path: 'search',
            element: <SearchPage />,
          },
          {
            path: 'investigations',
            element: <InvestigationsPage />,
          },
          {
            path: 'watchlists',
            element: <WatchlistsPage />,
          },
          {
            path: 'reports',
            element: <ReportsPage />,
          },
          {
            path: 'feeds',
            element: <FeedsPage />,
          },
          {
            path: 'settings',
            element: <SettingsPage />,
          },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);
