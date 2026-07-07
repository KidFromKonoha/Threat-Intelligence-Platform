import React, { useState } from 'react';
import { useInvestigations } from '../hooks/use-investigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Search, Shield, Clock, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Skeleton } from '@/components/ui/skeleton';
import { InvestigationCreateModal } from '../components/investigation-create-modal';

export const InvestigationsPage: React.FC = () => {
  const { data, isLoading, isError, error } = useInvestigations();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto">
      {/* Page Header */}
      <div className="px-6 py-4 border-b border-border flex items-center justify-between bg-card/30 flex-shrink-0">
        <div>
          <h1 className="text-base font-semibold tracking-tight">Investigations</h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Manage and track ongoing threat investigations
          </p>
        </div>
        <Button size="sm" onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="w-3.5 h-3.5 mr-1.5" />
          New Investigation
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 p-6">
        {isError && (
          <div className="mb-4 p-3 border border-destructive/50 bg-destructive/10 text-destructive rounded-md flex items-center gap-3">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span className="text-sm">
              {error instanceof Error ? error.message : 'Failed to load investigations.'}
            </span>
          </div>
        )}

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="rounded-lg border border-border p-4 space-y-3">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-3 w-2/3" />
              </div>
            ))}
          </div>
        ) : data && data.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center mb-4">
              <Search className="w-5 h-5 text-muted-foreground" />
            </div>
            <h3 className="text-sm font-semibold mb-1">No active investigations</h3>
            <p className="text-xs text-muted-foreground mb-4 max-w-xs">
              Start a new investigation to track related threat intelligence.
            </p>
            <Button size="sm" onClick={() => setIsCreateModalOpen(true)}>
              <Plus className="w-3.5 h-3.5 mr-1.5" /> Create Investigation
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {data?.map(inv => (
              <Link to={`/investigations/${inv.id}`} key={inv.id} className="block group">
                <Card className="h-full overflow-hidden hover:bg-muted/30 transition-colors border-border group-hover:border-primary/40">
                  <CardContent className="p-4 flex flex-col h-full">
                    <div className="flex justify-between items-start mb-2.5">
                      <div className="flex items-center gap-2">
                        <Shield className={`w-4 h-4 flex-shrink-0 ${
                          inv.priority === 'critical' ? 'text-destructive' :
                          inv.priority === 'high' ? 'text-amber-500' :
                          'text-emerald-500'
                        }`} />
                        <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded-sm tracking-wide ${
                          inv.status === 'open' ? 'bg-primary/15 text-primary' :
                          inv.status === 'in_progress' ? 'bg-amber-500/15 text-amber-500' :
                          'bg-muted text-muted-foreground'
                        }`}>
                          {inv.status.replace('_', ' ')}
                        </span>
                      </div>
                      <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wide bg-secondary px-1.5 py-0.5 rounded-sm">
                        {inv.priority}
                      </span>
                    </div>

                    <h3 className="text-sm font-semibold mb-1.5 line-clamp-2 leading-snug">{inv.title}</h3>

                    {inv.description && (
                      <p className="text-xs text-muted-foreground line-clamp-2 mb-3 flex-1">
                        {inv.description}
                      </p>
                    )}

                    <div className="flex items-center gap-3 mt-auto pt-3 border-t border-border text-[11px] text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        <span>{new Date(inv.created_at).toLocaleDateString()}</span>
                      </div>
                      {inv.owner && (
                        <div className="flex items-center gap-1 ml-auto">
                          <span className="w-4 h-4 rounded-full bg-secondary flex items-center justify-center text-[9px] font-bold">
                            {inv.owner.substring(0, 2).toUpperCase()}
                          </span>
                          <span className="truncate max-w-[70px]">{inv.owner}</span>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>

      <InvestigationCreateModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
};
