import { useDashboardPriorityQueue } from '../hooks/use-dashboard';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Briefcase, Eye, Target, AlertCircle, Clock } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
// Removed Badge and ScrollArea imports
import { Button } from '@/components/ui/button';
import { formatDistanceToNow } from 'date-fns';

export function PriorityQueueWidget() {
  const { data, isLoading, error, dataUpdatedAt } = useDashboardPriorityQueue();

  if (isLoading) {
    return (
      <Card className="h-full min-h-[300px] max-h-[450px] flex flex-col">
        <CardHeader>
          <CardTitle>Priority Queue</CardTitle>
          <CardDescription>Items requiring immediate action</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 flex-1">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
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
            Error Loading Priority Queue
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center">
          <p className="text-muted-foreground text-sm">Failed to load priority queue items.</p>
        </CardContent>
      </Card>
    );
  }

  const items = data?.items?.slice(0, 10) || [];

  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'briefcase': return <Briefcase className="w-5 h-5 text-blue-500" />;
      case 'eye': return <Eye className="w-5 h-5 text-orange-500" />;
      case 'target': return <Target className="w-5 h-5 text-destructive" />;
      default: return <AlertCircle className="w-5 h-5 text-muted-foreground" />;
    }
  };

  return (
    <Card className="h-full min-h-[300px] max-h-[450px] flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle>Priority Queue</CardTitle>
        <CardDescription>Items requiring immediate action</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 p-0 overflow-hidden">
        {items.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center p-6 text-center">
            <div className="w-12 h-12 rounded-full bg-green-100/10 flex items-center justify-center mb-4">
               <Briefcase className="w-6 h-6 text-green-500" />
            </div>
            <p className="font-medium">Inbox Zero</p>
            <p className="text-muted-foreground text-sm mt-1">No priority items require your immediate attention.</p>
          </div>
        ) : (
          <div className="h-full px-6 overflow-y-auto">
            <div className="space-y-4 pb-4">
              {items.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-3 rounded-lg border bg-card text-card-foreground shadow-sm hover:bg-accent/50 transition-colors">
                  <div className="flex items-start gap-4">
                    <div className="mt-1 flex-shrink-0">
                      {getIcon(item.icon)}
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm font-medium leading-none">{item.title}</p>
                      <p className="text-xs text-muted-foreground">{item.subtitle}</p>
                      <div className="flex items-center gap-2 pt-1">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider ${item.priority === 'critical' ? 'bg-destructive/10 text-destructive' : 'bg-primary/10 text-primary'}`}>
                          {item.priority}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(item.timestamp), { addSuffix: true })}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <Button variant="outline" size="sm">{item.action}</Button>
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
