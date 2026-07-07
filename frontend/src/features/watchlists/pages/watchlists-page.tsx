import React, { useState } from 'react';
import { Plus, LayoutGrid, List as ListIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useWatchlists, useWatchlistMatches } from '../hooks/use-watchlist';
import { WatchlistCard } from '../components/watchlist-card';
import { WatchlistEmptyState } from '../components/watchlist-empty-state';
import { WatchlistSkeleton } from '../components/watchlist-skeleton';
import { WatchlistCreateModal } from '../components/watchlist-create-modal';

export const WatchlistsPage: React.FC = () => {
  const { data: watchlists, isLoading, error } = useWatchlists();
  const { data: matches } = useWatchlistMatches();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col h-full overflow-y-auto">
        <div className="px-6 py-4 border-b border-border bg-card/30 flex-shrink-0">
          <div className="h-5 w-32 bg-muted animate-pulse rounded" />
        </div>
        <div className="p-6">
          <WatchlistSkeleton />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="text-center">
          <div className="text-destructive mb-1 font-medium text-sm">Failed to load watchlists</div>
          <p className="text-muted-foreground text-xs">{error instanceof Error ? error.message : 'Unknown error'}</p>
        </div>
      </div>
    );
  }

  const hasWatchlists = watchlists && watchlists.length > 0;

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto">
      {/* Page Header */}
      <div className="px-6 py-4 border-b border-border flex items-center justify-between bg-card/30 flex-shrink-0">
        <div>
          <h1 className="text-base font-semibold tracking-tight">Watchlists</h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Monitor specific intelligence entities for automated matching
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center p-0.5 bg-secondary rounded-md border border-border">
            <button
              onClick={() => setViewMode('grid')}
              aria-label="Grid view"
              className={`p-1.5 rounded-sm transition-colors ${viewMode === 'grid' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
            >
              <LayoutGrid className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              aria-label="List view"
              className={`p-1.5 rounded-sm transition-colors ${viewMode === 'list' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
            >
              <ListIcon className="w-3.5 h-3.5" />
            </button>
          </div>
          <Button size="sm" onClick={() => setIsCreateModalOpen(true)}>
            <Plus className="w-3.5 h-3.5 mr-1.5" />
            New Watchlist
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 overflow-y-auto">
        {!hasWatchlists ? (
          <WatchlistEmptyState onCreateClick={() => setIsCreateModalOpen(true)} />
        ) : (
          <div className={viewMode === 'grid'
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
            : "flex flex-col gap-3"
          }>
            {watchlists.map(watchlist => {
              const matchCount = matches?.filter(m => m.watchlist_id === watchlist.id).length || 0;
              return (
                <WatchlistCard
                  key={watchlist.id}
                  watchlist={watchlist}
                  matchCount={matchCount}
                />
              );
            })}
          </div>
        )}
      </div>

      {isCreateModalOpen && (
        <WatchlistCreateModal onClose={() => setIsCreateModalOpen(false)} />
      )}
    </div>
  );
};
