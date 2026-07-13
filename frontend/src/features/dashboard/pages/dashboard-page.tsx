import React, { useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Plus, Search } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/use-auth';
import { DashboardGrid } from '../components/dashboard-grid';
import { registerDashboardWidgets, dashboardLayouts } from '../framework';
import { Role } from '../framework/types';

// Initialize the registry
registerDashboardWidgets();

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  
  // Default to 'analyst' if role is missing, or fallback to default layout
  const userRole = (user?.role?.toLowerCase() as Role) || 'analyst';
  
  const layout = useMemo(() => {
    return dashboardLayouts[userRole] || dashboardLayouts['analyst'];
  }, [userRole]);

  return (
    <div className="flex-1 p-6 overflow-y-auto bg-background/50">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Operational Intelligence</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Welcome back, {user?.username || 'Hunter'}. Here is your workspace for today.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link to="/search" className="flex items-center gap-2">
              <Search className="w-4 h-4" />
              Global Search
            </Link>
          </Button>
          <Button size="sm" asChild>
            <Link to="/investigations" className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              New Investigation
            </Link>
          </Button>
        </div>
      </div>

      <DashboardGrid layout={layout} />
    </div>
  );
};
