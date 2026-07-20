import React, { useEffect, useState } from 'react';
import { investigationApi } from '../api/investigation-api';
import { GraphViewer } from '@/features/graph/components/graph-viewer';
import { Skeleton } from '@/components/ui/skeleton';

interface Props {
  entityId: string;
  entityType: string;
}

export const RelationshipExplorer: React.FC<Props> = ({ entityId }) => {
  const [graph, setGraph] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [depth, setDepth] = useState(2);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    investigationApi.getGraph(entityId, depth).then(data => {
      if (isMounted) {
        setGraph(data);
        setLoading(false);
      }
    }).catch(console.error);
    return () => { isMounted = false; };
  }, [entityId, depth]);

  if (loading) return <Skeleton className="h-full w-full" />;
  if (!graph) return <div className="p-4">Failed to load graph</div>;

  return (
    <div className="h-full w-full relative">
      <div className="absolute top-4 right-4 z-10 flex items-center gap-2 bg-card p-2 rounded shadow-md border">
        <label className="text-sm font-medium">Depth:</label>
        <select 
          value={depth} 
          onChange={e => setDepth(Number(e.target.value))}
          className="bg-transparent border border-input rounded text-sm p-1"
        >
          <option value={1}>1 - Direct</option>
          <option value={2}>2 - Extended</option>
          <option value={3}>3 - Deep</option>
        </select>
      </div>
      <GraphViewer graph={graph} />
    </div>
  );
};
