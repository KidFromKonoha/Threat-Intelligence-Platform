export interface GraphNode {
  id: string;
  entity_type: string;
  label: string;
  metadata?: Record<string, unknown>;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
  metadata?: Record<string, unknown>;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  root_id: string;
  depth: number;
}

export type GraphEntityType =
  | 'indicator'
  | 'threat_actor'
  | 'malware'
  | 'campaign'
  | 'vulnerability'
  | 'investigation'
  | 'report';
