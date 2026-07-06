import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { ShieldAlert, Fingerprint, Bug, Skull, AlertOctagon, Activity, Network } from 'lucide-react';
import { Link } from 'react-router-dom';

interface EntityHeaderProps {
  type: string;
  value: string;
  severity?: string;
  confidence?: number;
  status?: string;
  description?: string | null;
  /** If provided, shows a "View Graph" button */
  graphEntityType?: string;
  entityId?: string;
}

export const EntityHeader: React.FC<EntityHeaderProps> = ({ type, value, severity, confidence, status, description, graphEntityType, entityId }) => {
  const renderIcon = () => {
    switch (type.toLowerCase()) {
      case 'indicator': return <Fingerprint className="w-8 h-8 text-muted-foreground" />;
      case 'malware': return <Bug className="w-8 h-8 text-muted-foreground" />;
      case 'threat actor': return <Skull className="w-8 h-8 text-muted-foreground" />;
      case 'campaign': return <ShieldAlert className="w-8 h-8 text-muted-foreground" />;
      case 'vulnerability': return <AlertOctagon className="w-8 h-8 text-muted-foreground" />;
      default: return <Activity className="w-8 h-8 text-muted-foreground" />;
    }
  };

  const showGraphLink = graphEntityType && entityId && !['vulnerability', 'report'].includes(graphEntityType);

  return (
    <Card className="mb-6">
      <CardContent className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-secondary rounded-lg">
            {renderIcon()}
          </div>
          <div className="flex flex-col">
            <h1 className="text-2xl font-bold tracking-tight">{value}</h1>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-sm text-muted-foreground uppercase tracking-wider font-semibold">{type}</span>
              {description && <span className="text-sm text-muted-foreground ml-2 line-clamp-1 border-l border-border pl-2">{description}</span>}
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {showGraphLink && (
            <Link
              to={`/threat-graph/${graphEntityType}/${entityId}`}
              className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-md bg-secondary hover:bg-secondary/80 text-foreground transition-colors border border-border"
            >
              <Network className="w-3.5 h-3.5" />
              View Graph
            </Link>
          )}
          {severity && (
            <div className="flex flex-col items-end">
              <span className="text-xs text-muted-foreground uppercase font-medium">Severity</span>
              <span className={`text-sm font-bold uppercase ${
                severity.toLowerCase() === 'critical' ? 'text-destructive' :
                severity.toLowerCase() === 'high' ? 'text-amber-500' :
                severity.toLowerCase() === 'medium' ? 'text-yellow-500' :
                'text-emerald-500'
              }`}>{severity}</span>
            </div>
          )}
          {confidence !== undefined && (
            <div className="flex flex-col items-end border-l border-border pl-3">
              <span className="text-xs text-muted-foreground uppercase font-medium">Confidence</span>
              <span className="text-sm font-bold">{confidence}%</span>
            </div>
          )}
          {status && (
            <div className="flex flex-col items-end border-l border-border pl-3">
              <span className="text-xs text-muted-foreground uppercase font-medium">Status</span>
              <span className="text-sm font-bold capitalize">{status}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

