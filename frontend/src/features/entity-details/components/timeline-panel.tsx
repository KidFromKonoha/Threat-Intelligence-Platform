import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { TimelineEvent } from '../types/entity';
import { Clock } from 'lucide-react';

interface TimelinePanelProps {
  events: TimelineEvent[];
}

export const TimelinePanel: React.FC<TimelinePanelProps> = ({ events }) => {
  if (!events || events.length === 0) return null;

  // Sort events by timestamp descending
  const sortedEvents = [...events].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-muted-foreground" />
          Timeline
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {sortedEvents.map((evt, idx) => (
            <div key={idx} className="flex gap-4">
              <div className="flex flex-col items-center">
                <div className="w-2 h-2 rounded-full bg-primary mt-1.5" />
                {idx !== sortedEvents.length - 1 && (
                  <div className="w-px h-full bg-border my-1" />
                )}
              </div>
              <div className="flex flex-col pb-4">
                <span className="text-sm font-semibold">{evt.event_type}</span>
                <span className="text-sm text-muted-foreground">{evt.description}</span>
                <span className="text-xs text-muted-foreground mt-1 opacity-70">
                  {new Date(evt.timestamp).toLocaleString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
