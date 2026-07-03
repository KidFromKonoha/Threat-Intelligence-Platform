import React from 'react';
import { EmptyState } from '../../../components/feedback/empty-state';
import { useNavigate } from 'react-router-dom';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();
  
  return (
    <div className="min-h-[70vh] flex items-center justify-center">
      <EmptyState 
        title="Page Not Found"
        description="The page you are looking for does not exist or has been moved."
        action={
          <button 
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-md hover:bg-primary/90 transition-colors"
          >
            Go to Dashboard
          </button>
        }
      />
    </div>
  );
};
