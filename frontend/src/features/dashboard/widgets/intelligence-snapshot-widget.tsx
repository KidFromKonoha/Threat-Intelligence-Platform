import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useDashboardIntelligenceSnapshot } from '../hooks/use-dashboard';
import { Target, Users, Bug, Crosshair, FileText, Briefcase, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const TrendIndicator: React.FC<{ trend: 'up' | 'down' | 'flat' }> = ({ trend }) => {
  if (trend === 'up') return <TrendingUp className="w-3 h-3 text-destructive" />;
  if (trend === 'down') return <TrendingDown className="w-3 h-3 text-emerald-500" />;
  return <Minus className="w-3 h-3 text-muted-foreground" />;
};

const MetricItem: React.FC<{ label: string, value: number, trend: 'up' | 'down' | 'flat', icon: React.ReactNode }> = ({ label, value, trend, icon }) => (
  <div className="flex items-center gap-4 p-4 rounded-lg bg-card border border-border/50 shadow-sm">
    <div className="p-3 bg-primary/10 rounded-full text-primary">
      {icon}
    </div>
    <div className="flex flex-col">
      <span className="text-sm font-medium text-muted-foreground">{label}</span>
      <div className="flex items-center gap-2">
        <span className="text-2xl font-bold tabular-nums">{value.toLocaleString()}</span>
        <TrendIndicator trend={trend} />
      </div>
    </div>
  </div>
);

export const IntelligenceSnapshotWidget: React.FC = () => {
  const { data, isLoading, isError } = useDashboardIntelligenceSnapshot();

  if (isLoading) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle>Intelligence Snapshot (24h)</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-24 w-full rounded-lg" />
          ))}
        </CardContent>
      </Card>
    );
  }

  if (isError || !data) {
    return <Card className="h-full flex items-center justify-center p-6"><span className="text-destructive text-sm">Failed to load snapshot</span></Card>;
  }

  return (
    <Card className="h-full border-none shadow-none bg-transparent">
      <CardHeader className="px-0 pt-0 pb-4">
        <CardTitle className="text-lg font-semibold">Intelligence Snapshot (24h)</CardTitle>
      </CardHeader>
      <CardContent className="px-0 grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        <MetricItem label="New Indicators" value={data.new_indicators.count} trend={data.new_indicators.trend} icon={<Target className="w-5 h-5" />} />
        <MetricItem label="New Threat Actors" value={data.new_threat_actors.count} trend={data.new_threat_actors.trend} icon={<Users className="w-5 h-5" />} />
        <MetricItem label="New Malware" value={data.new_malware.count} trend={data.new_malware.trend} icon={<Bug className="w-5 h-5" />} />
        <MetricItem label="New Campaigns" value={data.new_campaigns.count} trend={data.new_campaigns.trend} icon={<Crosshair className="w-5 h-5" />} />
        <MetricItem label="New Reports" value={data.new_reports.count} trend={data.new_reports.trend} icon={<FileText className="w-5 h-5" />} />
        <MetricItem label="Open Investigations" value={data.open_investigations.count} trend={data.open_investigations.trend} icon={<Briefcase className="w-5 h-5" />} />
      </CardContent>
    </Card>
  );
};
