import React from 'react';
import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

interface EntityErrorProps {
  error: Error;
}

export const EntityError: React.FC<EntityErrorProps> = ({ error }) => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <div className="w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center mb-6">
        <AlertCircle className="w-8 h-8 text-destructive" />
      </div>
      <h2 className="text-2xl font-bold tracking-tight mb-2">Entity Not Found</h2>
      <p className="text-muted-foreground max-w-md mb-8">
        The requested entity could not be loaded. It may have been deleted, or you might not have permission to view it.
        <br />
        <span className="text-sm mt-2 block opacity-70">Details: {error.message}</span>
      </p>
      <Button onClick={() => navigate('/search')} variant="outline">
        Go to Search
      </Button>
    </div>
  );
};
