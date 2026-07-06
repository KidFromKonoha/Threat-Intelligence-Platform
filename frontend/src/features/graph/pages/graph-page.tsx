import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useEntityGraph } from '../hooks/use-graph';
import { GraphViewer } from '../components/graph-viewer';
import { Button } from '@/components/ui/button';
import { ArrowLeft, AlertCircle, Network } from 'lucide-react';
import type { GraphEntityType } from '../types/graph';

const VALID_ENTITY_TYPES = new Set<GraphEntityType>([
  'indicator',
  'threat_actor',
  'malware',
  'campaign',
  'investigation',
]);

export const GraphPage: React.FC = () => {
  const { entityType, id } = useParams<{ entityType: string; id: string }>();
  const navigate = useNavigate();

  const resolvedType = entityType as GraphEntityType;
  const isValidType = VALID_ENTITY_TYPES.has(resolvedType);

  const { data: graph, isLoading, isError, error } = useEntityGraph(
    resolvedType,
    id ?? '',
    2
  );

  if (!id || !entityType || !isValidType) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-4 text-center p-12">
        <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center">
          <Network className="w-8 h-8 text-muted-foreground" />
        </div>
        <h2 className="text-xl font-semibold">Select an Entity</h2>
        <p className="text-sm text-muted-foreground max-w-sm">
          Navigate to an entity from Search or Investigations and open its graph to explore relationships.
        </p>
        {entityType && !isValidType && (
          <p className="text-xs text-destructive mt-1">
            Entity type <code className="font-mono">{entityType}</code> is not supported for graph visualization.
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-3 border-b border-border bg-card flex-shrink-0">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate(-1)}
          aria-label="Go back"
        >
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">
            Threat Graph
          </span>
          <span className="text-xs text-muted-foreground">—</span>
          <span className="text-xs font-mono text-muted-foreground uppercase tracking-wider">
            {entityType}
          </span>
          <span className="text-xs text-muted-foreground">/</span>
          <span className="text-xs font-mono text-primary truncate max-w-[200px]">{id}</span>
        </div>
        {graph && (
          <div className="ml-auto flex items-center gap-4 text-xs text-muted-foreground">
            <span>{graph.nodes.length} nodes</span>
            <span>{graph.edges.length} edges</span>
            <span>depth {graph.depth}</span>
          </div>
        )}
      </div>

      {/* Graph Canvas */}
      <div className="flex-1 relative">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-10">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              <span className="text-sm text-muted-foreground">Building graph…</span>
            </div>
          </div>
        )}

        {isError && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex flex-col items-center gap-3 text-center max-w-md">
              <div className="w-12 h-12 bg-destructive/10 rounded-full flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-destructive" />
              </div>
              <h3 className="font-semibold">Graph Unavailable</h3>
              <p className="text-sm text-muted-foreground">
                {error instanceof Error ? error.message : 'Failed to load graph data.'}
              </p>
              <Button variant="outline" size="sm" onClick={() => navigate(-1)}>
                Go Back
              </Button>
            </div>
          </div>
        )}

        {!isLoading && !isError && graph && graph.nodes.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex flex-col items-center gap-3 text-center max-w-md">
              <div className="w-12 h-12 bg-muted rounded-full flex items-center justify-center">
                <Network className="w-6 h-6 text-muted-foreground" />
              </div>
              <h3 className="font-semibold">Empty Graph</h3>
              <p className="text-sm text-muted-foreground">
                No relationships found for this entity.
              </p>
            </div>
          </div>
        )}

        {!isLoading && !isError && graph && graph.nodes.length > 0 && (
          <GraphViewer graph={graph} />
        )}
      </div>
    </div>
  );
};
