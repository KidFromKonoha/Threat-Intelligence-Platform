import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useDashboardOverview } from '../hooks/use-dashboard';
import { Shield, Target, Activity, AlertTriangle } from 'lucide-react';

export const OverviewCard: React.FC = () => {
  const { data, isLoading, isError } = useDashboardOverview();

  if (isLoading) {
    return <Card className="h-full flex items-center justify-center min-h-[160px]"><span className="text-muted-foreground text-sm">Loading Overview...</span></Card>;
  }

  if (isError || !data) {
    return <Card className="h-full flex items-center justify-center min-h-[160px]"><span className="text-destructive text-sm">Failed to load overview</span></Card>;
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Platform Overview</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-4">
        <div className="flex flex-col">
          <div className="flex items-center text-muted-foreground mb-1">
            <Target className="w-4 h-4 mr-2" />
            <span className="text-xs font-medium uppercase">Total Indicators</span>
          </div>
          <span className="text-2xl font-semibold">{data.total_indicators.toLocaleString()}</span>
          <span className="text-xs text-muted-foreground mt-1">
            <span className="text-emerald-500 font-medium">+{data.new_indicators_24h}</span> in last 24h
          </span>
        </div>
        
        <div className="flex flex-col">
          <div className="flex items-center text-muted-foreground mb-1">
            <Activity className="w-4 h-4 mr-2" />
            <span className="text-xs font-medium uppercase">Active Feeds</span>
          </div>
          <span className="text-2xl font-semibold">{data.active_feeds}</span>
          <span className="text-xs text-muted-foreground mt-1">
            <span className={data.feed_health.health_percentage < 90 ? 'text-destructive font-medium' : 'text-emerald-500 font-medium'}>
              {data.feed_health.health_percentage.toFixed(1)}%
            </span> health
          </span>
        </div>

        <div className="flex flex-col mt-2">
          <div className="flex items-center text-muted-foreground mb-1">
            <Shield className="w-4 h-4 mr-2" />
            <span className="text-xs font-medium uppercase">Open Investigations</span>
          </div>
          <span className="text-2xl font-semibold">{data.open_investigations}</span>
        </div>
        
        <div className="flex flex-col mt-2">
          <div className="flex items-center text-muted-foreground mb-1">
            <AlertTriangle className="w-4 h-4 mr-2" />
            <span className="text-xs font-medium uppercase">Feed Errors</span>
          </div>
          <span className="text-2xl font-semibold">{data.feed_health.error_feeds}</span>
        </div>
      </CardContent>
    </Card>
  );
};
