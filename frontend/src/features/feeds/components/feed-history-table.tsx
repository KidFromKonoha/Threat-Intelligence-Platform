import React from 'react';
import type { FeedRunResponse } from '../types/feed';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';

interface Props {
  runs: FeedRunResponse[];
  isLoading: boolean;
}

export const FeedHistoryTable: React.FC<Props> = ({ runs, isLoading }) => {
  if (isLoading) {
    return <div className="p-8 text-center text-muted-foreground animate-pulse">Loading history...</div>;
  }

  if (!runs || runs.length === 0) {
    return <div className="p-8 text-center text-muted-foreground italic">No sync history available.</div>;
  }

  return (
    <div className="border border-border/60 rounded-xl overflow-hidden bg-card/50 shadow-sm">
      <table className="w-full text-sm text-left">
        <thead className="text-[11px] text-muted-foreground uppercase tracking-wider bg-black/5 dark:bg-white/[0.02] border-b border-border/60">
          <tr>
            <th className="px-4 py-3 font-medium">Status</th>
            <th className="px-4 py-3 font-medium">Start Time</th>
            <th className="px-4 py-3 font-medium text-right">Duration (s)</th>
            <th className="px-4 py-3 font-medium text-right">Received</th>
            <th className="px-4 py-3 font-medium text-right">Added</th>
            <th className="px-4 py-3 font-medium text-right">Updated</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border/40">
          {runs.map(run => (
            <tr key={run.id} className="hover:bg-black/5 dark:hover:bg-white/[0.02] transition-colors">
              <td className="px-4 py-3">
                <div className="flex items-center gap-1.5">
                  {run.status === 'success' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  ) : run.status === 'failed' ? (
                    <XCircle className="w-4 h-4 text-destructive" />
                  ) : (
                    <Loader2 className="w-4 h-4 text-amber-500 animate-spin" />
                  )}
                  <span className="capitalize">{run.status}</span>
                </div>
              </td>
              <td className="px-4 py-3 font-mono text-xs">
                {new Date(run.start_time).toLocaleString()}
              </td>
              <td className="px-4 py-3 text-right font-mono">
                {run.duration !== null ? run.duration.toFixed(2) : '-'}
              </td>
              <td className="px-4 py-3 text-right font-mono">{run.records_received.toLocaleString()}</td>
              <td className="px-4 py-3 text-right font-mono text-emerald-500">+{run.records_added.toLocaleString()}</td>
              <td className="px-4 py-3 text-right font-mono text-blue-500">{run.records_updated.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
