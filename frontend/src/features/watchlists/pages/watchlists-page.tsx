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
    return <div className="p-6 max-w-7xl mx-auto w-full"><WatchlistSkeleton /></div>;
  }

  if (error) {
    return (
      <div className="p-6 max-w-7xl mx-auto w-full text-center">
        <div className="text-destructive mb-2">Failed to load watchlists</div>
        <p className="text-muted-foreground text-sm">{error instanceof Error ? error.message : 'Unknown error'}</p>
      </div>
    );
  }

  const hasWatchlists = watchlists && watchlists.length > 0;

  return (
    <div className="p-6 max-w-7xl mx-auto w-full h-full flex flex-col overflow-hidden">
      <div className="flex items-center justify-between mb-6 flex-shrink-0">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Watchlists</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Monitor specific intelligence entities for automated matching.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center p-1 bg-secondary rounded-md border border-border">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded-sm transition-colors ${viewMode === 'grid' ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-1.5 rounded-sm transition-colors ${viewMode === 'list' ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
            >
              <ListIcon className="w-4 h-4" />
            </button>
          </div>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Watchlist
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto pb-6">
        {!hasWatchlists ? (
          <WatchlistEmptyState onCreateClick={() => setIsCreateModalOpen(true)} />
        ) : (
          <div className={viewMode === 'grid' 
            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
            : "flex flex-col gap-4"
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
