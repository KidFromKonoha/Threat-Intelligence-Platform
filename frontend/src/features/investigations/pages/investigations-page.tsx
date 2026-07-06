import React, { useState } from 'react';
import { useInvestigations } from '../hooks/use-investigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Search, Shield, Clock, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { InvestigationCreateModal } from '../components/investigation-create-modal';

export const InvestigationsPage: React.FC = () => {
  const { data, isLoading, isError, error } = useInvestigations();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  return (
    <div className="flex-1 flex flex-col bg-background text-foreground h-full overflow-y-auto">
      <div className="w-full max-w-7xl mx-auto px-6 pt-10 pb-6 flex flex-col gap-6">
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">Investigations</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Manage and track ongoing threat investigations.
            </p>
          </div>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Investigation
          </Button>
        </div>

        {isError && (
          <div className="p-4 border border-destructive/50 bg-destructive/10 text-destructive rounded-lg flex items-start gap-3">
            <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
            <div className="flex flex-col">
              <span className="font-semibold text-sm">Error Loading Investigations</span>
              <span className="text-sm mt-1 opacity-90">
                {error instanceof Error ? error.message : 'An unknown error occurred.'}
              </span>
            </div>
          </div>
        )}

        {isLoading ? (
          <div className="space-y-4">
            <div className="h-24 w-full bg-muted animate-pulse rounded-lg"></div>
            <div className="h-24 w-full bg-muted animate-pulse rounded-lg"></div>
            <div className="h-24 w-full bg-muted animate-pulse rounded-lg"></div>
          </div>
        ) : data && data.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center border border-dashed rounded-lg bg-muted/10">
            <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-4">
              <Search className="w-6 h-6 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No active investigations</h3>
            <p className="text-sm text-muted-foreground mb-4">Start a new investigation to track related threat intelligence.</p>
            <Button onClick={() => setIsCreateModalOpen(true)}>
              <Plus className="w-4 h-4 mr-2" /> Create Investigation
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data?.map(inv => (
              <Link to={`/investigations/${inv.id}`} key={inv.id} className="block group">
                <Card className="h-full overflow-hidden hover:bg-muted/50 transition-colors border-border group-hover:border-primary/50">
                  <CardContent className="p-5 flex flex-col h-full">
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center gap-2">
                        <Shield className={`w-5 h-5 ${inv.priority === 'critical' ? 'text-destructive' : inv.priority === 'high' ? 'text-amber-500' : 'text-emerald-500'}`} />
                        <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full tracking-wider ${
                          inv.status === 'open' ? 'bg-primary/20 text-primary' : 
                          inv.status === 'in_progress' ? 'bg-amber-500/20 text-amber-500' : 
                          'bg-muted text-muted-foreground'
                        }`}>
                          {inv.status.replace('_', ' ')}
                        </span>
                      </div>
                      <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider bg-secondary px-2 py-0.5 rounded-sm">
                        {inv.priority}
                      </span>
                    </div>
                    
                    <h3 className="text-lg font-semibold mb-2 line-clamp-2">{inv.title}</h3>
                    
                    {inv.description && (
                      <p className="text-sm text-muted-foreground line-clamp-2 mb-4 flex-1">
                        {inv.description}
                      </p>
                    )}
                    
                    <div className="flex items-center gap-4 mt-auto pt-4 border-t border-border text-xs text-muted-foreground">
                      <div className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{new Date(inv.created_at).toLocaleDateString()}</span>
                      </div>
                      {inv.owner && (
                        <div className="flex items-center gap-1.5 ml-auto">
                          <span className="w-4 h-4 rounded-full bg-secondary flex items-center justify-center text-[9px] font-bold">
                            {inv.owner.substring(0, 2).toUpperCase()}
                          </span>
                          <span className="truncate max-w-[80px]">{inv.owner}</span>
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
