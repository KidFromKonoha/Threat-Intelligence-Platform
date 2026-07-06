import { useQuery } from '@tanstack/react-query';
import { graphApi } from '../api/graph-api';
import type { GraphEntityType } from '../types/graph';

export const graphKeys = {
  all: ['graph'] as const,
  entity: (type: string, id: string, depth?: number) =>
    [...graphKeys.all, type, id, depth] as const,
};

export const useEntityGraph = (entityType: GraphEntityType, id: string, depth?: number) => {
  return useQuery({
    queryKey: graphKeys.entity(entityType, id, depth),
    queryFn: () => graphApi.getGraph(entityType, id, depth),
    enabled: !!entityType && !!id,
  });
};
