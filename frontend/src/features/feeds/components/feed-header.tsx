import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Database, RefreshCw, Activity } from 'lucide-react';
import { FeedStatusBadge } from './feed-status-badge';
import type { FeedResponse } from '../types/feed';
import { useUpdateFeed, useSyncFeed } from '../hooks/use-feed';

interface Props {
  feed: FeedResponse;
}

export const FeedHeader: React.FC<Props> = ({ feed }) => {
  const { mutate: updateFeed, isPending: isUpdating } = useUpdateFeed();
  const { mutate: syncFeed, isPending: isSyncing } = useSyncFeed();

  return (
    <Card className="mb-6">
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-secondary/50 rounded-lg shrink-0 mt-1">
              <Database className="w-8 h-8 text-primary" />
            </div>
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-bold tracking-tight">{feed.name}</h1>
                <FeedStatusBadge status={feed.status} />
              </div>
              <p className="text-muted-foreground text-sm max-w-2xl mb-4">
                {feed.description || 'No description provided.'}
              </p>
              
              <div className="flex items-center gap-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4" />
                  <span className="font-medium uppercase">{feed.type.replace('_', ' ')}</span>
                </div>
                <div>Priority: <span className="font-mono text-foreground">{feed.priority}</span></div>
                <div>Schedule: <span className="font-mono text-foreground">{feed.schedule || 'Manual'}</span></div>
              </div>
            </div>
          </div>
          
          <div className="flex flex-col gap-2 min-w-[140px]">
            <Button
              variant="default"
              className="w-full"
              onClick={() => syncFeed(feed.id)}
              disabled={!feed.enabled || isSyncing}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isSyncing ? 'animate-spin' : ''}`} />
              Sync Now
            </Button>
            <Button
              variant={feed.enabled ? "outline" : "secondary"}
              className={`w-full ${feed.enabled ? 'border-destructive text-destructive hover:bg-destructive/10 hover:text-destructive' : ''}`}
              onClick={() => updateFeed({ id: feed.id, data: { enabled: !feed.enabled } })}
              disabled={isUpdating}
            >
              {feed.enabled ? 'Disable Feed' : 'Enable Feed'}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
