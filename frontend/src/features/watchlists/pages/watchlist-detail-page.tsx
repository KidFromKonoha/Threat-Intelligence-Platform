import React from 'react';
import { useParams } from 'react-router-dom';
import { useWatchlist, useWatchlistMatches } from '../hooks/use-watchlist';
import { WatchlistHeader } from '../components/watchlist-header';
import { WatchlistEntityTable } from '../components/watchlist-entity-table';
import { WatchlistMatchesTable } from '../components/watchlist-matches-table';
import { WatchlistSkeleton } from '../components/watchlist-skeleton';

export const WatchlistDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data: watchlist, isLoading, error } = useWatchlist(id || '');
  const { data: allMatches, isLoading: matchesLoading } = useWatchlistMatches();

  if (isLoading) {
    return <div className="p-6 max-w-7xl mx-auto w-full"><WatchlistSkeleton /></div>;
  }

  if (error || !watchlist) {
    return (
      <div className="p-6 max-w-7xl mx-auto w-full text-center">
        <div className="text-destructive mb-2">Failed to load watchlist</div>
        <p className="text-muted-foreground text-sm">{error instanceof Error ? error.message : 'Unknown error'}</p>
      </div>
    );
  }

  const matches = allMatches?.filter(m => m.watchlist_id === watchlist.id) || [];

  return (
    <div className="p-6 max-w-7xl mx-auto w-full flex flex-col h-full overflow-y-auto">
      <WatchlistHeader watchlist={watchlist} />
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-6">
        <div className="col-span-1">
          <WatchlistEntityTable watchlist={watchlist} />
        </div>
        <div className="col-span-1">
          {matchesLoading ? (
            <div className="p-6 text-center text-muted-foreground">Loading matches...</div>
          ) : (
            <WatchlistMatchesTable matches={matches} />
          )}
        </div>
      </div>
    </div>
  );
};
