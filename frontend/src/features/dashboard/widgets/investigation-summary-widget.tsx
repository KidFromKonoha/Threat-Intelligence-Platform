import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useDashboardInvestigationSummary } from '../hooks/use-dashboard';
import { Briefcase, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

export const InvestigationSummaryWidget: React.FC = () => {
  const { data, isLoading, isError } = useDashboardInvestigationSummary();

  if (isLoading) {
    return <Card className="h-full p-6"><Skeleton className="h-32 w-full" /></Card>;
  }

  if (isError || !data) {
    return <Card className="h-full p-6"><span className="text-destructive text-sm">Failed to load investigation summary</span></Card>;
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3 flex flex-row items-center justify-between space-y-0">
        <CardTitle>Investigations</CardTitle>
        <Button variant="link" size="sm" asChild className="h-auto p-0 text-xs">
          <Link to="/investigations">View All</Link>
        </Button>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-4">
        <div className="flex flex-col p-3 rounded-lg bg-secondary/50">
          <div className="flex items-center gap-2 text-muted-foreground mb-2">
            <Briefcase className="w-4 h-4" />
            <span className="text-xs font-medium uppercase">Open</span>
          </div>
          <span className="text-2xl font-bold">{data.open}</span>
        </div>
        <div className="flex flex-col p-3 rounded-lg bg-destructive/10 text-destructive">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-xs font-medium uppercase">High Priority</span>
          </div>
          <span className="text-2xl font-bold">{data.high_priority}</span>
        </div>
        <div className="flex flex-col p-3 rounded-lg bg-secondary/50">
          <div className="flex items-center gap-2 text-muted-foreground mb-2">
            <Clock className="w-4 h-4" />
            <span className="text-xs font-medium uppercase">Updated (7d)</span>
          </div>
          <span className="text-2xl font-bold">{data.recently_updated}</span>
        </div>
        <div className="flex flex-col p-3 rounded-lg bg-secondary/50">
          <div className="flex items-center gap-2 text-muted-foreground mb-2">
            <CheckCircle2 className="w-4 h-4" />
            <span className="text-xs font-medium uppercase">Closed</span>
          </div>
          <span className="text-2xl font-bold">{data.closed}</span>
        </div>
      </CardContent>
    </Card>
  );
};
