import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useDashboardOverview } from '../hooks/use-dashboard';
import { Shield, Target, Activity, AlertTriangle } from 'lucide-react';

export const OverviewCard: React.FC = () => {
  const { data, isLoading, isError } = useDashboardOverview();

  if (isLoading) {
    return (
      <Card className="h-full min-h-[160px] p-6">
        <div className="space-y-4">
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-8 w-1/3" />
          <Skeleton className="h-4 w-2/3" />
          <Skeleton className="h-8 w-1/3" />
        </div>
      </Card>
    );
  }

  if (isError || !data) {
    return <Card className="h-full flex items-center justify-center min-h-[160px]"><span className="text-destructive text-sm">Failed to load overview</span></Card>;
  }

  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">Platform Overview</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-x-6 gap-y-4">
        <div className="flex flex-col">
          <div className="flex items-center text-muted-foreground mb-1">
            <Target className="w-3.5 h-3.5 mr-1.5" />
            <span className="text-xs font-medium uppercase tracking-wide">Indicators</span>
          </div>
          <span className="text-2xl font-semibold tabular-nums">{data.total_indicators.toLocaleString()}</span>
          <span className="text-xs text-muted-foreground mt-0.5">
            <span className="text-emerald-500 font-medium">+{data.new_indicators_24h}</span> last 24h
          </span>
        </div>

        <div className="flex flex-col">
          <div className="flex items-center text-muted-foreground mb-1">
            <Activity className="w-3.5 h-3.5 mr-1.5" />
            <span className="text-xs font-medium uppercase tracking-wide">Active Feeds</span>
          </div>
          <span className="text-2xl font-semibold tabular-nums">{data.active_feeds}</span>
          <span className="text-xs text-muted-foreground mt-0.5">
            <span className={data.feed_health.health_percentage < 90 ? 'text-destructive font-medium' : 'text-emerald-500 font-medium'}>
              {data.feed_health.health_percentage.toFixed(0)}%
            </span> health
          </span>
        </div>

        <div className="flex flex-col">
          <div className="flex items-center text-muted-foreground mb-1">
            <Shield className="w-3.5 h-3.5 mr-1.5" />
            <span className="text-xs font-medium uppercase tracking-wide">Investigations</span>
          </div>
          <span className="text-2xl font-semibold tabular-nums">{data.open_investigations}</span>
          <span className="text-xs text-muted-foreground mt-0.5">Open</span>
        </div>

        <div className="flex flex-col">
          <div className="flex items-center text-muted-foreground mb-1">
            <AlertTriangle className="w-3.5 h-3.5 mr-1.5" />
            <span className="text-xs font-medium uppercase tracking-wide">Feed Errors</span>
          </div>
          <span className={`text-2xl font-semibold tabular-nums ${data.feed_health.error_feeds > 0 ? 'text-destructive' : ''}`}>
            {data.feed_health.error_feeds}
          </span>
          <span className="text-xs text-muted-foreground mt-0.5">Failing</span>
        </div>
      </CardContent>
    </Card>
  );
};
