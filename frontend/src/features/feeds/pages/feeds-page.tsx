import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useFeeds } from '../hooks/use-feed';
import { FeedCard } from '../components/feed-card';
import { FeedSkeleton } from '../components/feed-skeleton';
import { FeedEmptyState } from '../components/feed-empty-state';
import { Database } from 'lucide-react';

export const FeedsPage: React.FC = () => {
  const navigate = useNavigate();
  const { data: feeds, isLoading, error } = useFeeds();

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto">
      {/* Page Header */}
      <div className="px-6 py-4 border-b border-border flex items-center gap-3 bg-card/30 flex-shrink-0">
        <Database className="w-4 h-4 text-muted-foreground" />
        <div>
          <h1 className="text-base font-semibold tracking-tight">Feed Management</h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Monitor and manage intelligence feed integrations
          </p>
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
        ) : !feeds || feeds.length === 0 ? (
          <FeedEmptyState />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 animate-in fade-in duration-300">
            {feeds.map((feed) => (
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
