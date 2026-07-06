import React from 'react';
import { useInvestigationTimeline } from '../hooks/use-investigation';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Activity, Clock } from 'lucide-react';

interface Props {
  investigationId: string;
}

export const InvestigationTimeline: React.FC<Props> = ({ investigationId }) => {
  const { data, isLoading } = useInvestigationTimeline(investigationId);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="w-5 h-5" /> Activity Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="h-12 w-full bg-muted animate-pulse rounded"></div>
            <div className="h-12 w-full bg-muted animate-pulse rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="w-5 h-5" /> Activity Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground text-sm">
            No timeline events recorded.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Activity className="w-5 h-5" /> Activity Timeline
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative border-l border-border ml-3 space-y-6">
          {data.map((event, idx) => (
            <div key={event.id || idx} className="relative pl-6">
              <span className="absolute left-[-5px] top-1 w-2.5 h-2.5 rounded-full bg-primary ring-4 ring-background"></span>
              <div className="flex flex-col gap-1">
                <span className="text-sm font-semibold">{event.event_type.replace(/_/g, ' ')}</span>
                <span className="text-xs text-muted-foreground flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {new Date(event.timestamp).toLocaleString()}
                </span>
                <p className="text-sm text-foreground/80 mt-1">{event.description}</p>
                {event.details && Object.keys(event.details).length > 0 && (
                  <pre className="mt-2 text-[10px] bg-secondary p-2 rounded overflow-x-auto">
                    {JSON.stringify(event.details, null, 2)}
                  </pre>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
