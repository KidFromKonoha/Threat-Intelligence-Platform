import React from 'react';
import { EntityEvent } from '../api/investigation-api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { format } from 'date-fns';
import { ScrollArea } from '@/components/ui/scroll-area';

interface Props {
  timeline: EntityEvent[];
}

export const TimelinePanel: React.FC<Props> = ({ timeline }) => {
  return (
    <Card className="flex flex-col flex-1 h-[400px]">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          Investigation Timeline
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-0">
        <ScrollArea className="h-[320px] px-6">
          <div className="space-y-4 pb-4">
            {timeline.length === 0 ? (
              <p className="text-sm text-muted-foreground">No events recorded.</p>
            ) : (
              <div className="relative border-l ml-3 space-y-6 mt-2">
                {timeline.map((event, idx) => (
                  <div key={event.id || idx} className="relative pl-6">
                    <div className="absolute w-3 h-3 bg-primary rounded-full -left-[6.5px] top-1.5" />
                    <div className="flex flex-col gap-1">
                      <span className="text-sm font-semibold">{event.event_type}</span>
                      <span className="text-xs text-muted-foreground">
                        {format(new Date(event.created_at), 'MMM d, yyyy HH:mm:ss')}
                      </span>
                      {event.payload && Object.keys(event.payload).length > 0 && (
                        <pre className="text-xs bg-muted p-2 rounded mt-1 overflow-x-auto">
                          {JSON.stringify(event.payload, null, 2)}
                        </pre>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};
