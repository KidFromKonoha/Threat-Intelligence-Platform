import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Database, RefreshCw } from 'lucide-react';
import { FeedStatusBadge } from './feed-status-badge';
import type { FeedResponse } from '../types/feed';
import { useSyncFeed, useUpdateFeed } from '../hooks/use-feed';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';
import { useAuth } from '@/hooks/use-auth';

interface Props {
  feed: FeedResponse;
  onClick: () => void;
}

export const FeedCard: React.FC<Props> = ({ feed, onClick }) => {
  const { mutate: syncFeed, isPending: isSyncing } = useSyncFeed();
  const { mutate: updateFeed, isPending: isUpdating } = useUpdateFeed();
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const [actionToConfirm, setActionToConfirm] = React.useState<'pause' | 'resume' | 'sync' | null>(null);

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (feed.enabled) {
      setActionToConfirm('pause');
    } else {
      setActionToConfirm('resume');
    }
  };

  const confirmPause = () => {
    updateFeed({ id: feed.id, data: { enabled: false } });
  };

  const confirmResume = () => {
    updateFeed({ id: feed.id, data: { enabled: true } });
  };

  const handleSync = (e: React.MouseEvent) => {
    e.stopPropagation();
    setActionToConfirm('sync');
  };

  const confirmSync = () => {
    syncFeed(feed.id);
  };

  return (
    <>
      <Card 
        className={`cursor-pointer transition-all hover:shadow-md ${
          !feed.enabled ? 'border-border/50 bg-card/50 grayscale-[0.3]' : 'hover:border-primary/50'
        }`}
        onClick={onClick}
      >
      <CardContent className="p-5">
        <div className="flex justify-between items-start mb-3">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-md ${!feed.enabled ? 'bg-secondary/30' : 'bg-secondary/50'}`}>
              <Database className={`w-5 h-5 ${!feed.enabled ? 'text-muted-foreground' : 'text-primary'}`} />
            </div>
            <div>
              <h3 className={`font-semibold text-base leading-none mb-1.5 ${!feed.enabled ? 'text-muted-foreground' : ''}`}>{feed.name}</h3>
              <div className="flex items-center gap-2">
                <FeedStatusBadge status={feed.status} enabled={feed.enabled} />
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
          {isAdmin ? (
            <Button
              variant={feed.enabled ? "outline" : "secondary"}
              size="sm"
              onClick={handleToggle}
              disabled={isUpdating}
              className={`w-24 ${feed.enabled ? 'border-destructive text-destructive hover:bg-destructive/10 hover:text-destructive' : ''}`}
            >
              {feed.enabled ? 'Pause' : 'Resume'}
            </Button>
          ) : (
            <div className="w-24"></div>
          )}

          <div className="relative group flex flex-col items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSync}
              disabled={!feed.enabled || isSyncing}
              className={feed.enabled ? "text-primary hover:text-primary hover:bg-primary/10" : ""}
            >
              {isSyncing ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              Sync Now
            </Button>
            {!feed.enabled && (
              <span className="absolute bottom-full mb-2 hidden group-hover:block bg-popover text-popover-foreground text-[10px] px-2 py-1 rounded shadow-md border border-border whitespace-nowrap z-50">
                Paused feeds cannot run until resumed
              </span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>

    <ConfirmDialog
      isOpen={actionToConfirm === 'pause'}
      title="Pause Feed"
      description="Pause this feed? It will no longer be scheduled, but its history and imported indicators will remain."
      confirmText="Pause"
      onConfirm={confirmPause}
      onCancel={() => setActionToConfirm(null)}
      isDestructive={true}
    />
    <ConfirmDialog
      isOpen={actionToConfirm === 'resume'}
      title="Resume Feed"
      description="Resume this feed? It will start running according to its schedule."
      confirmText="Resume"
      onConfirm={confirmResume}
      onCancel={() => setActionToConfirm(null)}
    />
    <ConfirmDialog
      isOpen={actionToConfirm === 'sync'}
      title="Run Feed Now"
      description="Are you sure you want to run this feed manually? This may take some time depending on the size of the feed."
      confirmText="Run Now"
      onConfirm={confirmSync}
      onCancel={() => setActionToConfirm(null)}
    />
    </>
  );
};
