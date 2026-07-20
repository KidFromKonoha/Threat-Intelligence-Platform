import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useDashboardHighSeverityIntelligence } from '../hooks/use-dashboard';
import { Link } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const HighSeverityWidget: React.FC = () => {
  const { data, isLoading, isError } = useDashboardHighSeverityIntelligence();

  if (isLoading) {
    return <Card className="h-full p-6"><Skeleton className="h-32 w-full" /></Card>;
  }

  if (isError || !data) {
    return <Card className="h-full p-6"><span className="text-destructive text-sm">Failed to load</span></Card>;
  }

  return (
    <Card className="h-full flex flex-col border-destructive/20 shadow-sm">
      <CardHeader className="pb-3 flex flex-row items-center justify-between space-y-0">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-destructive" />
          <CardTitle className="text-sm font-medium text-destructive uppercase tracking-wide">High Severity Intel</CardTitle>
        </div>
        <Button variant="link" size="sm" asChild className="h-auto p-0 text-xs">
          <Link to="/search?severity=high,critical">View All</Link>
        </Button>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto">
        <div className="space-y-3">
          {data.indicators.length === 0 ? (
             <div className="text-sm text-muted-foreground py-4 text-center">No high severity intelligence recently.</div>
          ) : (
            data.indicators.slice(0, 5).map((indicator) => (
              <div key={indicator.id} className="flex flex-col gap-1 border-b border-border/50 pb-2 last:border-0 last:pb-0">
                <Link to={`/entities/indicator/${indicator.id}`} className="text-sm font-medium hover:underline truncate">
                  {indicator.value}
                </Link>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="uppercase">{indicator.type}</span>
                  <span className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-destructive" />
                    {indicator.severity}
                  </span>
                  <span>{indicator.confidence}% Conf</span>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};
