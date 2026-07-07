import React from 'react';
import { Database } from 'lucide-react';

export const FeedEmptyState: React.FC = () => (
  <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-border rounded-lg bg-card/50">
    <div className="p-4 bg-secondary/50 rounded-full mb-4">
      <Database className="w-8 h-8 text-muted-foreground" />
    </div>
    <h3 className="text-lg font-semibold tracking-tight mb-2">No Feeds Available</h3>
    <p className="text-sm text-muted-foreground max-w-md mx-auto">
      There are currently no feeds configured or available. Ensure the backend feed integration services are running.
    </p>
  </div>
);
