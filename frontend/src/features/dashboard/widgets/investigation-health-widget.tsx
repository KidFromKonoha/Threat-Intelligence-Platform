import { useDashboardInvestigationHealth } from '../hooks/use-dashboard';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { AlertCircle, Clock, Briefcase, AlertTriangle, FileWarning, CheckCircle2 } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDistanceToNow } from 'date-fns';

export function InvestigationHealthWidget() {
  const { data, isLoading, error, dataUpdatedAt } = useDashboardInvestigationHealth();

  if (isLoading) {
    return (
      <Card className="h-full min-h-[250px] max-h-[450px] flex flex-col">
        <CardHeader>
          <CardTitle>Investigation Health</CardTitle>
          <CardDescription>Current operational workload</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 flex-1">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="h-full min-h-[250px] max-h-[450px] flex flex-col border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            Error Loading Health
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center">
          <p className="text-muted-foreground text-sm">Failed to load investigation health metrics.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full min-h-[250px] max-h-[450px] flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle>Investigation Health</CardTitle>
        <CardDescription>Current operational workload</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 p-6 pt-0">
        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col p-4 bg-muted/50 rounded-lg border">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Briefcase className="w-4 h-4" />
              <span className="text-sm font-medium">Open</span>
            </div>
            <span className="text-3xl font-bold">{data?.open || 0}</span>
          </div>
          
          <div className="flex flex-col p-4 bg-red-500/10 rounded-lg border border-red-500/20">
            <div className="flex items-center gap-2 text-red-600 dark:text-red-400 mb-2">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm font-medium">High Priority</span>
            </div>
            <span className="text-3xl font-bold text-red-600 dark:text-red-400">{data?.high_priority || 0}</span>
          </div>
          
          <div className="flex flex-col p-4 bg-orange-500/10 rounded-lg border border-orange-500/20">
            <div className="flex items-center gap-2 text-orange-600 dark:text-orange-400 mb-2">
              <FileWarning className="w-4 h-4" />
              <span className="text-sm font-medium">Overdue (7d+)</span>
            </div>
            <span className="text-3xl font-bold text-orange-600 dark:text-orange-400">{data?.overdue || 0}</span>
          </div>
          
          <div className="flex flex-col p-4 bg-green-500/10 rounded-lg border border-green-500/20">
            <div className="flex items-center gap-2 text-green-600 dark:text-green-400 mb-2">
              <CheckCircle2 className="w-4 h-4" />
              <span className="text-sm font-medium">Updated Today</span>
            </div>
            <span className="text-3xl font-bold text-green-600 dark:text-green-400">{data?.updated_today || 0}</span>
          </div>
        </div>
      </CardContent>
      <CardFooter className="pt-4 pb-4 text-xs text-muted-foreground flex items-center gap-1 border-t mt-auto">
        <Clock className="w-3 h-3" />
        Last updated {dataUpdatedAt ? formatDistanceToNow(dataUpdatedAt, { addSuffix: true }) : 'never'}
      </CardFooter>
    </Card>
  );
}
