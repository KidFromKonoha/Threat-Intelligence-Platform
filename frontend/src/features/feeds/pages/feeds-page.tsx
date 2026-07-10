import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFeeds } from '../hooks/use-feed';
import { FeedCard } from '../components/feed-card';
import { FeedSkeleton } from '../components/feed-skeleton';
import { FeedEmptyState } from '../components/feed-empty-state';


export const FeedsPage: React.FC = () => {
  const navigate = useNavigate();
  const { data: feeds, isLoading, error } = useFeeds();
  const [filter, setFilter] = useState<'all' | 'active' | 'paused'>('all');

  const filteredFeeds = React.useMemo(() => {
    if (!feeds) return [];
    if (filter === 'active') return feeds.filter(f => f.enabled);
    if (filter === 'paused') return feeds.filter(f => !f.enabled);
    return feeds;
  }, [feeds, filter]);

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto">
      {/* Page Header */}
      <div className="px-6 py-4 border-b border-border flex flex-col gap-6 md:flex-row md:items-center justify-between bg-card/30 flex-shrink-0">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-1">Intelligence Feeds</h1>
          <p className="text-muted-foreground text-sm">
            Manage your external threat intelligence sources and their synchronization schedules.
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <select 
            value={filter} 
            onChange={(e) => setFilter(e.target.value as 'all' | 'active' | 'paused')}
            className="h-9 px-3 py-1 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary min-w-[140px]"
          >
            <option value="all">All Feeds</option>
            <option value="active">Active Only</option>
            <option value="paused">Paused Only</option>
          </select>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-6">
        {isLoading ? (
          <FeedSkeleton />
        ) : error ? (
          <div className="p-8 text-center border border-dashed border-border rounded-lg bg-card/50">
            <p className="text-destructive text-sm font-medium mb-1">Failed to load feeds</p>
            <p className="text-muted-foreground text-xs">
              {error instanceof Error ? error.message : 'Unknown error occurred.'}
            </p>
          </div>
        ) : !filteredFeeds || filteredFeeds.length === 0 ? (
          <FeedEmptyState />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in duration-300">
            {filteredFeeds.map((feed) => (
              <FeedCard
                key={feed.id}
                feed={feed}
                onClick={() => navigate(`/feeds/${feed.id}`)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
