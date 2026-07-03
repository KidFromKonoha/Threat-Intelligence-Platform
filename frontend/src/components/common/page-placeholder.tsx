import React from 'react';

interface PagePlaceholderProps {
  title: string;
}

export const PagePlaceholder: React.FC<PagePlaceholderProps> = ({ title }) => {
  return (
    <div className="flex flex-col flex-1 p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">{title}</h1>
      </div>
      <div className="flex-1 rounded-lg border border-dashed border-border bg-card/50 flex items-center justify-center min-h-[400px]">
        <p className="text-sm text-muted-foreground">
          {title} implementation pending in a future phase.
        </p>
      </div>
    </div>
  );
};
