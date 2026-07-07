import React from 'react';
import { Binoculars } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Props {
  onCreateClick?: () => void;
}

export const WatchlistEmptyState: React.FC<Props> = ({ onCreateClick }) => (
  <div className="flex-1 flex flex-col items-center justify-center p-12 text-center border border-dashed border-border rounded-lg bg-card/50">
    <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-4">
      <Binoculars className="w-8 h-8 text-muted-foreground" />
    </div>
    <h2 className="text-xl font-semibold tracking-tight mb-2">No Watchlists Found</h2>
    <p className="text-muted-foreground max-w-sm mb-6">
      Watchlists help you monitor specific entities and automatically track new activity.
    </p>
    {onCreateClick && (
      <Button onClick={onCreateClick}>Create Watchlist</Button>
    )}
  </div>
);
