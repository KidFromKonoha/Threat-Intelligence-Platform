import React from 'react';
import { OverviewCard } from '../components/overview-card';
import { FeedStatusCard } from '../components/feed-status-card';
import { OrganizationCard } from '../components/organization-card';
import { ThreatActivityCard } from '../components/threat-activity-card';
import { RecentIntelligenceCard } from '../components/recent-intelligence-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Search, Server, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  return (
    <div className="flex-1 p-6 overflow-y-auto">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Dashboard</h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Operational workspace and platform overview
          </p>
        </div>
        <div className="flex items-center rounded-md border border-border overflow-hidden divide-x divide-border">
          <Button variant="ghost" size="sm" className="rounded-none border-0 text-muted-foreground hover:text-foreground hover:bg-secondary px-3 h-8" asChild>
            <Link to="/search" className="flex items-center">
              <Search className="w-3.5 h-3.5 mr-1.5" />
              Search
            </Link>
          </Button>
          <Button size="sm" className="rounded-none border-0 px-3 h-8" asChild>
            <Link to="/investigations" className="flex items-center">
              <Plus className="w-3.5 h-3.5 mr-1.5" />
              New Investigation
            </Link>
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-4">
        {/* Top Row — key metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <OverviewCard />
          <FeedStatusCard />
          <OrganizationCard />
        </div>

        {/* Middle Row — activity + recent intel */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <ThreatActivityCard />
          </div>
          <div>
            <RecentIntelligenceCard />
          </div>
        </div>

        {/* Bottom Row — quick actions + system status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pb-2">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-2">
              <Button variant="outline" size="sm" className="justify-start" asChild>
                <Link to="/search">
                  <Search className="w-3.5 h-3.5 mr-2" /> Search Indicators
                </Link>
              </Button>
              <Button variant="outline" size="sm" className="justify-start" asChild>
                <Link to="/watchlists">
                  <ShieldCheck className="w-3.5 h-3.5 mr-2" /> View Watchlists
                </Link>
              </Button>
              <Button variant="outline" size="sm" className="justify-start" asChild>
                <Link to="/investigations">
                  <Plus className="w-3.5 h-3.5 mr-2" /> New Investigation
                </Link>
              </Button>
              <Button variant="outline" size="sm" className="justify-start" asChild>
                <Link to="/feeds">
                  <Server className="w-3.5 h-3.5 mr-2" /> Manage Feeds
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col space-y-3">
                {[
                  { label: 'Core API Database', status: 'Operational' },
                  { label: 'Redis Cache Worker', status: 'Operational' },
                  { label: 'Background Job Queue', status: 'Operational' },
                ].map(({ label, status }) => (
                  <div key={label} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Server className="w-3.5 h-3.5 text-muted-foreground" />
                      <span className="text-sm">{label}</span>
                    </div>
                    <span className="text-xs font-medium text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-sm">
                      {status}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
