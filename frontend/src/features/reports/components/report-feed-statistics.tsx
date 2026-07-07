import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Rss, CheckCircle2, XCircle } from 'lucide-react';
import type { ReportFeedStatistics } from '../types/report';

interface Props {
  stats: ReportFeedStatistics;
}

export const ReportFeedStatisticsCard: React.FC<Props> = ({ stats }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Feed Integration Health</CardTitle>
      </CardHeader>
      <CardContent>
        {stats.feeds.length === 0 ? (
          <p className="text-sm text-muted-foreground italic">No feed data available.</p>
        ) : (
          <div className="border border-border rounded-md overflow-hidden">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-muted-foreground uppercase bg-secondary/50">
                <tr>
                  <th className="px-4 py-3 font-medium">Feed Name</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium text-right">Total Imports</th>
                  <th className="px-4 py-3 font-medium text-right">Failed Runs</th>
                  <th className="px-4 py-3 font-medium text-right">Avg Runtime (s)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {stats.feeds.map(feed => (
                  <tr key={feed.name} className="hover:bg-secondary/10 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Rss className="w-4 h-4 text-muted-foreground" />
                        <span className="font-medium">{feed.name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        {feed.status.toLowerCase() === 'active' || feed.status.toLowerCase() === 'healthy' ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-destructive" />
                        )}
                        <span className="capitalize">{feed.status}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right font-mono">{feed.total_imports.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right font-mono text-destructive">{feed.failed_runs.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right font-mono">{feed.average_runtime_seconds.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
