import React from 'react';
import { Outlet, ScrollRestoration } from 'react-router-dom';
import { Sidebar } from '../components/layout/sidebar';
import { TopNavigation } from '../components/layout/top-navigation';
import { ErrorBoundary } from '../components/feedback/error-boundary';

export const AppLayout: React.FC = () => {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0">
        <TopNavigation />
        <main className="flex-1 overflow-auto bg-background/50">
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
      <ScrollRestoration />
    </div>
  );
};
