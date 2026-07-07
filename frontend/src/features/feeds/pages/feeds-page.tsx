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
    <div className="p-6 max-w-7xl mx-auto w-full h-full flex flex-col overflow-hidden">
      <div className="flex items-center justify-between mb-8 flex-shrink-0">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="p-2 bg-primary/10 rounded-md">
              <Database className="w-6 h-6 text-primary" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight">Feed Management</h1>
          </div>
          <p className="text-muted-foreground text-sm ml-11">
            Monitor and manage intelligence feeds integration.
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto pb-6">
        {isLoading ? (
          <FeedSkeleton />
        ) : error ? (
          <div className="p-12 text-center border border-dashed border-border rounded-lg bg-card/50 text-destructive">
            Failed to load feeds. {error instanceof Error ? error.message : 'Unknown error occurred.'}
          </div>
        ) : !feeds || feeds.length === 0 ? (
          <FeedEmptyState />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
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
