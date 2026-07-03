import React from 'react';
import { OverviewCard } from '../components/overview-card';
import { FeedStatusCard } from '../components/feed-status-card';
import { OrganizationCard } from '../components/organization-card';
import { ThreatActivityCard } from '../components/threat-activity-card';
import { RecentIntelligenceCard } from '../components/recent-intelligence-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Search, Server, ShieldCheck } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  return (
    <div className="flex-1 p-6 overflow-y-auto bg-background text-foreground">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Operational workspace and platform overview.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Search className="w-4 h-4 mr-2" />
            Global Search
          </Button>
          <Button size="sm">
            <Plus className="w-4 h-4 mr-2" />
            New Investigation
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-6 max-w-7xl">
        {/* Top Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <OverviewCard />
          <FeedStatusCard />
          <OrganizationCard />
        </div>

        {/* Middle Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <ThreatActivityCard />
          </div>
          <div className="md:col-span-1">
            <RecentIntelligenceCard />
          </div>
        </div>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-6">
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4">
              <Button variant="outline" className="justify-start">
                <Plus className="w-4 h-4 mr-2" /> Add Indicator
              </Button>
              <Button variant="outline" className="justify-start">
                <Search className="w-4 h-4 mr-2" /> View Watchlists
              </Button>
              <Button variant="outline" className="justify-start">
                <ShieldCheck className="w-4 h-4 mr-2" /> Trigger Enrichment
              </Button>
              <Button variant="outline" className="justify-start">
                <Server className="w-4 h-4 mr-2" /> Manage Feeds
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Server className="w-4 h-4 mr-2 text-muted-foreground" />
                    <span className="text-sm font-medium">Core API Database</span>
                  </div>
                  <span className="text-xs font-medium text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded-sm">Operational</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Server className="w-4 h-4 mr-2 text-muted-foreground" />
                    <span className="text-sm font-medium">Redis Cache Worker</span>
                  </div>
                  <span className="text-xs font-medium text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded-sm">Operational</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Server className="w-4 h-4 mr-2 text-muted-foreground" />
                    <span className="text-sm font-medium">Background Job Queue</span>
                  </div>
                  <span className="text-xs font-medium text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded-sm">Operational</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
