import { useDashboardWatchlistActivity } from '../hooks/use-dashboard';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { AlertCircle, Clock, Eye } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
// Removed ScrollArea import
import { formatDistanceToNow } from 'date-fns';

export function WatchlistActivityWidget() {
  const { data, isLoading, error, dataUpdatedAt } = useDashboardWatchlistActivity();

  if (isLoading) {
    return (
      <Card className="h-full min-h-[300px] max-h-[450px] flex flex-col">
        <CardHeader>
          <CardTitle>Watchlist Activity</CardTitle>
          <CardDescription>Hits detected today</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 flex-1">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="h-full min-h-[300px] max-h-[450px] flex flex-col border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            Error Loading Watchlists
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center">
          <p className="text-muted-foreground text-sm">Failed to load watchlist activity.</p>
        </CardContent>
      </Card>
    );
  }

  const activities = data?.activities || [];

  return (
    <Card className="h-full min-h-[300px] max-h-[450px] flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle>Watchlist Activity</CardTitle>
        <CardDescription>Top hits detected today</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 p-0 overflow-hidden">
        {activities.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center p-6 text-center">
            <Eye className="w-10 h-10 text-muted-foreground mb-4 opacity-50" />
            <p className="text-muted-foreground">No watchlist hits recorded today.</p>
          </div>
        ) : (
          <div className="h-full px-6 overflow-y-auto">
            <div className="space-y-3 pb-4">
              {activities.map((activity) => (
                <div key={activity.watchlist_id} className="flex items-center justify-between p-3 rounded-lg border bg-card text-card-foreground shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center">
                      <Eye className="w-4 h-4 text-blue-500" />
                    </div>
                    <p className="text-sm font-medium">{activity.watchlist_name}</p>
                  </div>
                  <div className="flex items-center gap-1.5 bg-secondary/50 px-2 py-1 rounded-md">
                    <span className="text-sm font-bold">{activity.hits_today}</span>
                    <span className="text-xs text-muted-foreground">hits</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter className="pt-4 pb-4 text-xs text-muted-foreground flex items-center gap-1 border-t mt-auto">
        <Clock className="w-3 h-3" />
        Last updated {dataUpdatedAt ? formatDistanceToNow(dataUpdatedAt, { addSuffix: true }) : 'never'}
      </CardFooter>
    </Card>
  );
}
