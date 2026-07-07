import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, Shield, Rss, AlertCircle, Search, Target } from 'lucide-react';
import type { ReportPlatformOverview } from '../types/report';

interface Props {
  overview: ReportPlatformOverview;
}

export const ReportPlatformOverviewCard: React.FC<Props> = ({ overview }) => {
  const metrics = [
    {
      label: 'Total Indicators',
      value: overview.total_indicators,
      icon: Shield,
      color: 'text-blue-500',
    },
    {
      label: 'New Indicators',
      value: overview.new_indicators,
      icon: Target,
      color: 'text-indigo-500',
    },
    {
      label: 'Active Feeds',
      value: overview.active_feeds,
      icon: Rss,
      color: 'text-emerald-500',
    },
    {
      label: 'Feed Health',
      value: `${overview.feed_health_percentage.toFixed(1)}%`,
      icon: Activity,
      color: overview.feed_health_percentage > 90 ? 'text-emerald-500' : 'text-amber-500',
    },
    {
      label: 'Open Investigations',
      value: overview.open_investigations,
      icon: Search,
      color: 'text-amber-500',
    },
    {
      label: 'Watchlist Matches',
      value: overview.active_watchlist_matches,
      icon: AlertCircle,
      color: 'text-destructive',
    },
  ];

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="text-lg">Platform Overview</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {metrics.map((m, i) => (
            <div key={i} className="p-4 bg-secondary/30 rounded-lg border border-border/50 flex flex-col items-center justify-center text-center">
              <m.icon className={`w-5 h-5 mb-2 ${m.color}`} />
              <div className="text-2xl font-bold tracking-tight mb-1">{m.value}</div>
              <div className="text-xs text-muted-foreground font-medium uppercase tracking-wider">{m.label}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
