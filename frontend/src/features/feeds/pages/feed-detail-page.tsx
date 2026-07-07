import React, { useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useFeed, useFeedRuns, useFeedStatus } from '../hooks/use-feed';
import { FeedHeader } from '../components/feed-header';
import { FeedStatistics } from '../components/feed-statistics';
import { FeedHistoryTable } from '../components/feed-history-table';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

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
    return <div className="p-12 text-center text-muted-foreground animate-pulse">Loading feed details...</div>;
  }

  if (feedError || !feed) {
    return (
      <div className="p-6">
        <Button variant="ghost" className="mb-4" onClick={() => navigate('/feeds')}>
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Feeds
        </Button>
        <div className="p-12 text-center border border-dashed border-border rounded-lg bg-card/50 text-destructive">
          Failed to load feed detail.
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto w-full h-full flex flex-col overflow-hidden">
      <div className="mb-4 flex-shrink-0">
        <Button variant="ghost" onClick={() => navigate('/feeds')} className="-ml-2 text-muted-foreground hover:text-foreground">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Feeds
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto pb-6 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <FeedHeader feed={feed} />
        
        {statusDetail && (
          <FeedStatistics stats={statusDetail} />
        )}

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Run History</CardTitle>
          </CardHeader>
          <CardContent>
            <FeedHistoryTable runs={runs || []} isLoading={isRunsLoading} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
