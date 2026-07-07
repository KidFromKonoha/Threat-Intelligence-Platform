import React, { useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useFeed, useFeedRuns, useFeedStatus } from '../hooks/use-feed';
import { FeedHeader } from '../components/feed-header';
import { FeedStatistics } from '../components/feed-statistics';
import { FeedHistoryTable } from '../components/feed-history-table';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export const FeedDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: feed, isLoading: isFeedLoading, error: feedError } = useFeed(id!);
  const { data: runs, isLoading: isRunsLoading } = useFeedRuns(id!);
  const { data: statuses } = useFeedStatus();

  const statusDetail = useMemo(() => {
    return statuses?.find(s => s.id === id);
  }, [statuses, id]);

  if (isFeedLoading) {
    return (
      <div className="flex-1 flex flex-col h-full overflow-y-auto">
        <div className="px-6 py-4 border-b border-border flex items-center gap-3 bg-card/30 flex-shrink-0">
          <Skeleton className="h-4 w-4" />
          <Skeleton className="h-4 w-48" />
        </div>
        <div className="p-6 space-y-4">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (feedError || !feed) {
    return (
      <div className="flex-1 flex flex-col h-full overflow-y-auto">
        <div className="px-6 py-4 border-b border-border flex-shrink-0">
          <Button variant="ghost" size="sm" className="-ml-2" onClick={() => navigate('/feeds')}>
            <ArrowLeft className="w-3.5 h-3.5 mr-1.5" /> Back to Feeds
          </Button>
        </div>
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="p-8 text-center border border-dashed border-border rounded-lg bg-card/50">
            <p className="text-destructive text-sm font-medium mb-1">Failed to load feed</p>
            <p className="text-muted-foreground text-xs">The requested feed could not be found or loaded.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto">
      {/* Back navigation */}
      <div className="px-6 py-3 border-b border-border flex-shrink-0 bg-card/30">
        <Button variant="ghost" size="sm" className="-ml-2 text-muted-foreground hover:text-foreground" onClick={() => navigate('/feeds')}>
          <ArrowLeft className="w-3.5 h-3.5 mr-1.5" />
          Back to Feeds
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 space-y-4 animate-in fade-in duration-300">
        <FeedHeader feed={feed} />

        {statusDetail && (
          <FeedStatistics stats={statusDetail} />
        )}

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Run History</CardTitle>
          </CardHeader>
          <CardContent>
            <FeedHistoryTable runs={runs || []} isLoading={isRunsLoading} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
