import React from 'react';
import { ArrowLeft, Clock, Shield, Network } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useNavigate, Link } from 'react-router-dom';
import type { InvestigationResponse } from '../types/investigation';

interface Props {
  investigation: InvestigationResponse;
}

export const InvestigationHeader: React.FC<Props> = ({ investigation }) => {
  const navigate = useNavigate();

  return (
    <div className="bg-card border-b border-border w-full">
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex items-start gap-4 mb-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/investigations')} className="mt-1">
            <ArrowLeft className="w-5 h-5" />
          </Button>
          
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <Shield className={`w-6 h-6 ${investigation.priority === 'critical' ? 'text-destructive' : investigation.priority === 'high' ? 'text-amber-500' : 'text-emerald-500'}`} />
                <h1 className="text-2xl font-bold tracking-tight">{investigation.title}</h1>
                <span className={`text-xs uppercase font-bold px-2.5 py-1 rounded-full tracking-wider ml-2 ${
                  investigation.status === 'open' ? 'bg-primary/20 text-primary' : 
                  investigation.status === 'in_progress' ? 'bg-amber-500/20 text-amber-500' : 
                  'bg-muted text-muted-foreground'
                }`}>
                  {investigation.status.replace('_', ' ')}
                </span>
                <span className="text-xs uppercase font-bold text-muted-foreground tracking-wider bg-secondary px-2.5 py-1 rounded-sm ml-1">
                  {investigation.priority}
                </span>
              </div>
              
              <Link
                to={`/threat-graph/investigation/${investigation.id}`}
                className="flex items-center gap-2 text-sm font-medium px-4 py-2 rounded-md bg-secondary hover:bg-secondary/80 text-foreground transition-colors border border-border"
              >
                <Network className="w-4 h-4" />
                View Graph
              </Link>
            </div>
            
            {investigation.description && (
              <p className="text-muted-foreground text-sm max-w-3xl ml-11">
                {investigation.description}
              </p>
            )}
            
            <div className="flex items-center gap-6 mt-4 ml-11 text-xs text-muted-foreground">
              <div className="flex items-center gap-1.5">
                <Clock className="w-4 h-4" />
                <span>Created {new Date(investigation.created_at).toLocaleString()}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Clock className="w-4 h-4" />
                <span>Updated {new Date(investigation.updated_at).toLocaleString()}</span>
              </div>
              {investigation.owner && (
                <div className="flex items-center gap-1.5 ml-auto bg-secondary/50 px-2 py-1 rounded-md">
                  <span className="font-semibold">Owner:</span>
                  <span>{investigation.owner}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
