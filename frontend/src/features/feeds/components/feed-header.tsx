import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Database, RefreshCw, Activity } from 'lucide-react';
import { FeedStatusBadge } from './feed-status-badge';
import type { FeedResponse } from '../types/feed';
import { useUpdateFeed, useSyncFeed } from '../hooks/use-feed';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';

interface Props {
  feed: FeedResponse;
}

export const FeedHeader: React.FC<Props> = ({ feed }) => {
  const { mutate: updateFeed, isPending: isUpdating } = useUpdateFeed();
  const { mutate: syncFeed, isPending: isSyncing } = useSyncFeed();
  const [showConfirm, setShowConfirm] = React.useState(false);

  const handleToggle = () => {
    if (feed.enabled) {
      setShowConfirm(true);
    } else {
      updateFeed({ id: feed.id, data: { enabled: true } });
    }
  };

  const confirmDisable = () => {
    updateFeed({ id: feed.id, data: { enabled: false } });
  };

  return (
    <>
      <Card className="mb-6">
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-lg shrink-0 mt-1 ${!feed.enabled ? 'bg-secondary/30' : 'bg-secondary/50'}`}>
              <Database className={`w-8 h-8 ${!feed.enabled ? 'text-muted-foreground' : 'text-primary'}`} />
            </div>
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h1 className={`text-2xl font-bold tracking-tight ${!feed.enabled ? 'text-muted-foreground' : ''}`}>{feed.name}</h1>
                <FeedStatusBadge status={feed.status} enabled={feed.enabled} />
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
            <div className="relative group">
              <Button
                variant="default"
                className="w-full"
                onClick={() => syncFeed(feed.id)}
                disabled={!feed.enabled || isSyncing}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isSyncing ? 'animate-spin' : ''}`} />
                Sync Now
              </Button>
              {!feed.enabled && (
                <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block bg-popover text-popover-foreground text-[10px] px-2 py-1 rounded shadow-md border border-border whitespace-nowrap z-50">
                  Disabled feeds cannot run until re-enabled
                </span>
              )}
            </div>
            <Button
              variant={feed.enabled ? "outline" : "secondary"}
              className={`w-full ${feed.enabled ? 'border-destructive text-destructive hover:bg-destructive/10 hover:text-destructive' : ''}`}
              onClick={handleToggle}
              disabled={isUpdating}
            >
              {feed.enabled ? 'Disable Feed' : 'Enable Feed'}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>

    <ConfirmDialog
      isOpen={showConfirm}
      title="Disable Feed"
      description="Disable this feed? It will no longer be scheduled, but its history and imported indicators will remain."
      confirmText="Disable"
      onConfirm={confirmDisable}
      onCancel={() => setShowConfirm(false)}
      isDestructive={true}
    />
    </>
  );
};
