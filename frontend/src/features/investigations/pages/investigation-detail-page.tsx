import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useInvestigation, useInvestigationSummary, useDeleteInvestigation } from '../hooks/use-investigation';
import { InvestigationHeader } from '../components/investigation-header';
import { InvestigationTimeline } from '../components/investigation-timeline';
import { InvestigationEntities } from '../components/investigation-entities';
import { Button } from '@/components/ui/button';
import { Trash2, AlertCircle, ArrowLeft } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

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
      <div className="flex-1 flex flex-col h-full overflow-y-auto">
        <div className="px-6 py-3 border-b border-border flex-shrink-0 bg-card/30">
          <Skeleton className="h-4 w-36" />
        </div>
        <div className="p-6 space-y-4">
          <Skeleton className="h-28 w-full rounded-lg" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2">
              <Skeleton className="h-80 w-full rounded-lg" />
            </div>
            <Skeleton className="h-80 w-full rounded-lg" />
          </div>
        </div>
      </div>
    );
  }

  if (isInvError || !investigation) {
    return (
      <div className="flex-1 flex flex-col h-full overflow-y-auto">
        <div className="px-6 py-3 border-b border-border flex-shrink-0 bg-card/30">
          <Button variant="ghost" size="sm" className="-ml-2" onClick={() => navigate('/investigations')}>
            <ArrowLeft className="w-3.5 h-3.5 mr-1.5" /> Back
          </Button>
        </div>
        <div className="flex-1 flex items-center justify-center py-24 text-center p-6">
          <div>
            <div className="w-12 h-12 bg-destructive/10 rounded-full flex items-center justify-center mb-4 mx-auto">
              <AlertCircle className="w-6 h-6 text-destructive" />
            </div>
            <h2 className="text-base font-semibold mb-1">Investigation Not Found</h2>
            <p className="text-muted-foreground text-sm max-w-sm mb-6">
              The requested investigation could not be loaded.
            </p>
            <Button size="sm" onClick={() => navigate('/investigations')} variant="outline">
              Go to Investigations
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto">
      {/* Back nav */}
      <div className="px-6 py-3 border-b border-border flex-shrink-0 bg-card/30">
        <Button variant="ghost" size="sm" className="-ml-2 text-muted-foreground hover:text-foreground" onClick={() => navigate('/investigations')}>
          <ArrowLeft className="w-3.5 h-3.5 mr-1.5" />
          Investigations
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 p-6 space-y-4">
        <InvestigationHeader investigation={investigation} />

        <div className="flex justify-end">
          <Button variant="destructive" size="sm" onClick={handleDelete} disabled={isDeleting}>
            <Trash2 className="w-3.5 h-3.5 mr-1.5" />
            Delete Investigation
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 space-y-4">
            {summary && <InvestigationEntities summary={summary} />}
          </div>

          <div className="space-y-4">
            <InvestigationTimeline investigationId={investigation.id} />
          </div>
        </div>
      </div>
    </div>
  );
};
