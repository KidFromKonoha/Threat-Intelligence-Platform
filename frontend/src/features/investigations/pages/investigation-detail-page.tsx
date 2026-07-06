import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useInvestigation, useInvestigationSummary, useDeleteInvestigation } from '../hooks/use-investigation';
import { InvestigationHeader } from '../components/investigation-header';
import { InvestigationTimeline } from '../components/investigation-timeline';
import { InvestigationEntities } from '../components/investigation-entities';
import { Button } from '@/components/ui/button';
import { Trash2, AlertCircle } from 'lucide-react';

export const InvestigationDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const investigationId = id as string;
  const navigate = useNavigate();
  
  const { data: investigation, isLoading: isInvLoading, isError: isInvError } = useInvestigation(investigationId);
  const { data: summary, isLoading: isSumLoading } = useInvestigationSummary(investigationId);
  const { mutateAsync: deleteInvestigation, isPending: isDeleting } = useDeleteInvestigation();

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this investigation?')) {
      try {
        await deleteInvestigation(investigationId);
        navigate('/investigations');
      } catch (err) {
        console.error('Failed to delete', err);
      }
    }
  };

  if (isInvLoading || isSumLoading) {
    return (
      <div className="flex-1 p-6 space-y-6">
        <div className="h-32 bg-muted animate-pulse rounded-lg w-full"></div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-96 bg-muted animate-pulse rounded-lg"></div>
          <div className="h-96 bg-muted animate-pulse rounded-lg"></div>
        </div>
      </div>
    );
  }

  if (isInvError || !investigation) {
    return (
      <div className="flex-1 flex items-center justify-center py-24 text-center">
        <div className="w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center mb-6">
          <AlertCircle className="w-8 h-8 text-destructive" />
        </div>
        <h2 className="text-2xl font-bold tracking-tight mb-2">Investigation Not Found</h2>
        <p className="text-muted-foreground max-w-md mb-8">
          The requested investigation could not be loaded.
        </p>
        <Button onClick={() => navigate('/investigations')} variant="outline">
          Go to Investigations
        </Button>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-background text-foreground h-full overflow-y-auto">
      <InvestigationHeader investigation={investigation} />
      
      <div className="w-full max-w-7xl mx-auto px-6 py-6">
        <div className="flex justify-end gap-3 mb-6">
          <Button variant="destructive" size="sm" onClick={handleDelete} disabled={isDeleting}>
            <Trash2 className="w-4 h-4 mr-2" />
            Delete
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {summary && <InvestigationEntities summary={summary} />}
          </div>
          
          <div className="space-y-6">
            <InvestigationTimeline investigationId={investigation.id} />
          </div>
        </div>
      </div>
    </div>
  );
};
