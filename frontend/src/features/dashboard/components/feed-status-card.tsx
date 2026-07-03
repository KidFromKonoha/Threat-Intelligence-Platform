import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useDashboardFeedStatus } from '../hooks/use-dashboard';
import { Clock } from 'lucide-react';

export const FeedStatusCard: React.FC = () => {
  const { data, isLoading, isError } = useDashboardFeedStatus();

  if (isLoading) {
    return <Card className="h-full flex items-center justify-center min-h-[160px]"><span className="text-muted-foreground text-sm">Loading Feeds...</span></Card>;
  }

  if (isError || !data) {
    return <Card className="h-full flex items-center justify-center min-h-[160px]"><span className="text-destructive text-sm">Failed to load feed status</span></Card>;
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle>Feed Health</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto pr-2 -mr-2">
        <div className="space-y-4">
          {data.feeds.slice(0, 4).map((feed) => (
            <div key={feed.id} className="flex items-center justify-between border-b border-border pb-3 last:border-0 last:pb-0">
              <div className="flex flex-col max-w-[60%]">
                <span className="text-sm font-medium truncate">{feed.name}</span>
                <span className="text-xs text-muted-foreground flex items-center mt-0.5">
                  <Clock className="w-3 h-3 mr-1" />
                  {feed.last_success ? new Date(feed.last_success).toLocaleTimeString() : 'Never'}
                </span>
              </div>
              <div className="flex flex-col items-end flex-shrink-0 ml-2">
                {feed.status === 'active' ? (
                  <span className="flex items-center text-xs font-semibold text-emerald-500 whitespace-nowrap">
                    <span className="mr-1.5 text-lg leading-none">&bull;</span> Active
                  </span>
                ) : feed.status === 'error' ? (
                  <span className="flex items-center text-xs font-semibold text-destructive whitespace-nowrap">
                    <span className="mr-1.5 text-lg leading-none">&bull;</span> Error
                  </span>
                ) : (
                  <span className="flex items-center text-xs font-semibold text-muted-foreground whitespace-nowrap">
                    <span className="mr-1.5 text-lg leading-none">&bull;</span> Disabled
                  </span>
                )}
                <span className="text-xs text-muted-foreground mt-0.5 whitespace-nowrap">
                  {feed.records_imported.toLocaleString()} records
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
