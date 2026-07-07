import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

export const FeedSkeleton: React.FC = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
    {[1, 2, 3, 4, 5, 6].map(i => (
      <Card key={i}>
        <CardContent className="p-6">
          <div className="flex justify-between items-start mb-4">
            <div className="h-6 w-32 bg-muted rounded" />
            <div className="h-5 w-16 bg-muted rounded-full" />
          </div>
          <div className="h-4 w-full bg-muted rounded mb-2" />
          <div className="h-4 w-2/3 bg-muted rounded mb-6" />
          <div className="space-y-3">
            <div className="flex justify-between">
              <div className="h-3 w-20 bg-muted rounded" />
              <div className="h-3 w-16 bg-muted rounded" />
            </div>
            <div className="flex justify-between">
              <div className="h-3 w-24 bg-muted rounded" />
              <div className="h-3 w-20 bg-muted rounded" />
            </div>
          </div>
        </CardContent>
      </Card>
    ))}
  </div>
);
