import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, Clock, CheckCircle2, XCircle } from 'lucide-react';
import type { FeedStatusDetail } from '../types/feed';

interface Props {
  stats: FeedStatusDetail;
}

export const FeedStatistics: React.FC<Props> = ({ stats }) => {
  const metrics = [
    {
      label: 'Total Runs',
      value: stats.total_runs.toLocaleString(),
      icon: Activity,
      color: 'text-blue-500',
    },
    {
      label: 'Failed Runs',
      value: stats.failed_runs.toLocaleString(),
      icon: XCircle,
      color: 'text-destructive',
    },
    {
      label: 'Avg Duration',
      value: stats.average_run_duration ? `${stats.average_run_duration.toFixed(2)}s` : '-',
      icon: Clock,
      color: 'text-amber-500',
    },
    {
      label: 'Records Imported',
      value: stats.records_imported.toLocaleString(),
      icon: CheckCircle2,
      color: 'text-emerald-500',
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Feed Health Statistics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map((m, i) => (
            <div key={i} className="p-4 bg-secondary/30 rounded-lg border border-border flex flex-col items-center text-center">
              <m.icon className={`w-5 h-5 mb-2 ${m.color}`} />
              <div className="text-xl font-bold tracking-tight mb-1">{m.value}</div>
              <div className="text-xs text-muted-foreground font-medium uppercase tracking-wider">{m.label}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
