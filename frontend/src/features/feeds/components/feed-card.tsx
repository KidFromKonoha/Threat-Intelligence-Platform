import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Database, RefreshCw } from 'lucide-react';
import { FeedStatusBadge } from './feed-status-badge';
import type { FeedResponse } from '../types/feed';
import { useSyncFeed, useUpdateFeed } from '../hooks/use-feed';

interface Props {
  feed: FeedResponse;
  onClick: () => void;
}

export const FeedCard: React.FC<Props> = ({ feed, onClick }) => {
  const { mutate: syncFeed, isPending: isSyncing } = useSyncFeed();
  const { mutate: updateFeed, isPending: isUpdating } = useUpdateFeed();

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    updateFeed({ id: feed.id, data: { enabled: !feed.enabled } });
  };

  const handleSync = (e: React.MouseEvent) => {
    e.stopPropagation();
    syncFeed(feed.id);
  };

  return (
    <Card 
      className="cursor-pointer hover:border-primary/50 transition-all hover:shadow-md"
      onClick={onClick}
    >
      <CardContent className="p-5">
        <div className="flex justify-between items-start mb-3">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-secondary/50 rounded-md">
              <Database className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-base leading-none mb-1.5">{feed.name}</h3>
              <div className="flex items-center gap-2">
                <FeedStatusBadge status={feed.status} />
                <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                  {feed.type.replace('_', ' ')}
                </span>
              </div>
            </div>
          </div>
        </div>

        <p className="text-sm text-muted-foreground mb-4 line-clamp-2 min-h-[40px]">
          {feed.description || 'No description provided.'}
        </p>

        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
          <div className="bg-secondary/30 p-2 rounded">
            <div className="text-xs text-muted-foreground mb-1">Records</div>
            <div className="font-mono font-medium">{feed.records_imported.toLocaleString()}</div>
          </div>
          <div className="bg-secondary/30 p-2 rounded">
            <div className="text-xs text-muted-foreground mb-1">Last Sync</div>
            <div className="font-mono font-medium text-[11px] truncate" title={feed.last_success ? new Date(feed.last_success).toLocaleString() : 'Never'}>
              {feed.last_success ? new Date(feed.last_success).toLocaleString() : 'Never'}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-border">
          <Button
            variant={feed.enabled ? "outline" : "secondary"}
            size="sm"
            onClick={handleToggle}
            disabled={isUpdating}
            className={`w-24 ${feed.enabled ? 'border-destructive text-destructive hover:bg-destructive/10 hover:text-destructive' : ''}`}
          >
            {feed.enabled ? 'Disable' : 'Enable'}
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleSync}
            disabled={!feed.enabled || isSyncing}
            className="text-primary hover:text-primary hover:bg-primary/10"
          >
            {isSyncing ? (
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4 mr-2" />
            )}
            Sync Now
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
