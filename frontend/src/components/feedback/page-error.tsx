import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface PageErrorProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const PageError: React.FC<PageErrorProps> = ({ 
  title = 'Something went wrong', 
  message = 'An error occurred while loading this content.',
  onRetry
}) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] w-full p-6 text-center">
      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-destructive/10 mb-4">
        <AlertTriangle className="w-6 h-6 text-destructive" />
      </div>
      <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-md mb-6">{message}</p>
      {onRetry && (
        <button 
          onClick={onRetry}
          className="px-4 py-2 text-sm font-medium text-primary-foreground bg-primary rounded-md hover:bg-primary/90 transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
};
