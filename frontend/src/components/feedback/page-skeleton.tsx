import React from 'react';

export const PageSkeleton: React.FC = () => {
  return (
    <div className="w-full space-y-4 animate-pulse p-6">
      <div className="h-8 bg-muted rounded w-1/4"></div>
      <div className="space-y-3">
        <div className="h-24 bg-muted rounded"></div>
        <div className="h-24 bg-muted rounded"></div>
        <div className="h-24 bg-muted rounded"></div>
      </div>
    </div>
  );
};
