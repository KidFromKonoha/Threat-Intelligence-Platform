import React from 'react';
import { Card, CardContent } from '@/components/ui/card';

export const EntitySkeleton: React.FC = () => {
  return (
    <div className="flex flex-col gap-6 w-full animate-pulse">
      <Card>
        <CardContent className="p-6 flex items-center justify-between">
          <div className="flex gap-4 items-center">
            <div className="w-14 h-14 bg-muted rounded-lg" />
            <div className="flex flex-col gap-2">
              <div className="h-6 w-64 bg-muted rounded" />
              <div className="h-4 w-32 bg-muted rounded" />
            </div>
          </div>
          <div className="flex gap-4">
            <div className="h-10 w-20 bg-muted rounded" />
            <div className="h-10 w-20 bg-muted rounded" />
          </div>
        </CardContent>
      </Card>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          <div className="h-64 w-full bg-muted rounded-lg" />
          <div className="h-40 w-full bg-muted rounded-lg" />
        </div>
        <div className="col-span-1 space-y-6">
          <div className="h-40 w-full bg-muted rounded-lg" />
          <div className="h-40 w-full bg-muted rounded-lg" />
        </div>
      </div>
    </div>
  );
};
