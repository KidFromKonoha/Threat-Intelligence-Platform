import { useDashboardIntelligenceHighlights } from '../hooks/use-dashboard';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { AlertCircle, TrendingUp, Info, Activity, ShieldAlert, Clock } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
// Removed Badge and ScrollArea imports
import { formatDistanceToNow } from 'date-fns';

export function IntelligenceHighlightsWidget() {
  const { data, isLoading, error, dataUpdatedAt } = useDashboardIntelligenceHighlights();

  if (isLoading) {
    return (
      <Card className="h-full min-h-[300px] max-h-[450px] flex flex-col">
        <CardHeader>
          <CardTitle>Intelligence Highlights</CardTitle>
          <CardDescription>Operational insights for the last 24 hours</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 flex-1">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
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
            Error Loading Highlights
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center">
          <p className="text-muted-foreground text-sm">Failed to load intelligence highlights.</p>
        </CardContent>
      </Card>
    );
  }

  const insights = data?.insights?.slice(0, 5) || [];

  const getIcon = (type: string, severity: string) => {
    if (type === 'spike') return <Activity className="w-5 h-5 text-destructive" />;
    if (type === 'watchlist_hit') return <ShieldAlert className="w-5 h-5 text-orange-500" />;
    if (type === 'investigation') return <AlertCircle className="w-5 h-5 text-yellow-500" />;
    return <Info className="w-5 h-5 text-blue-500" />;
  };

  return (
    <Card className="h-full min-h-[300px] max-h-[450px] flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle>Intelligence Highlights</CardTitle>
        <CardDescription>Operational insights for the last 24 hours</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 p-0 overflow-hidden">
        {insights.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center p-6 text-center">
            <Info className="w-10 h-10 text-muted-foreground mb-4 opacity-50" />
            <p className="text-muted-foreground">No significant operational highlights in the last 24 hours.</p>
          </div>
        ) : (
          <div className="h-full px-6 overflow-y-auto">
            <div className="space-y-4 pb-4">
              {insights.map((insight) => (
                <div key={insight.id} className="flex items-start gap-4 p-4 rounded-lg border bg-card text-card-foreground shadow-sm">
                  <div className="mt-1 flex-shrink-0">
                    {getIcon(insight.type, insight.severity)}
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium leading-none">{insight.title}</p>
                      {insight.trend === 'up' && <TrendingUp className="w-4 h-4 text-destructive" />}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {insight.description}
                    </p>
                    <div className="flex items-center gap-2 pt-2">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider ${insight.severity === 'critical' ? 'bg-destructive/10 text-destructive' : 'bg-secondary text-secondary-foreground'}`}>
                        {insight.severity}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {formatDistanceToNow(new Date(insight.timestamp), { addSuffix: true })}
                      </span>
                    </div>
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
