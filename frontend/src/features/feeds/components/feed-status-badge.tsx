import React from 'react';
import type { FeedStatus } from '../types/feed';

interface Props {
  status: FeedStatus | string;
}

export const FeedStatusBadge: React.FC<Props> = ({ status }) => {
  const isHealthy = status.toLowerCase() === 'active' || status.toLowerCase() === 'healthy';
  const isError = status.toLowerCase() === 'error';

  return (
    <span
      className={`px-2 py-0.5 rounded-full text-xs font-semibold tracking-wide uppercase border ${
        isHealthy
          ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
          : isError
          ? 'bg-destructive/10 text-destructive border-destructive/20'
          : 'bg-muted text-muted-foreground border-border'
      }`}
    >
      {status}
    </span>
  );
};
