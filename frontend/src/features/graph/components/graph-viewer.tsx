import React, { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  BackgroundVariant,
  type Node,
  type Edge,
  type Connection,
  type NodeMouseHandler,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useNavigate } from 'react-router-dom';
import type { GraphResponse } from '../types/graph';
import { ThreatNode } from './threat-node';
import { GraphLegend } from './graph-legend';

const nodeTypes = { threat: ThreatNode };

const entityRouteMap: Record<string, string> = {
  indicator: '/entities/indicator',
  threat_actor: '/entities/threat-actor',
  malware: '/entities/malware',
  campaign: '/entities/campaign',
  vulnerability: '/entities/vulnerability',
  investigation: '/investigations',
};

// Simple left-to-right dagre-style layout using layer assignment
function buildLayout(graphNodes: GraphResponse['nodes'], graphEdges: GraphResponse['edges'], rootId: string) {
  const adj: Record<string, string[]> = {};
  graphNodes.forEach(n => (adj[n.id] = []));
  graphEdges.forEach(e => {
    if (adj[e.source]) adj[e.source].push(e.target);
  });

  // BFS to assign depth levels
  const levels: Record<string, number> = { [rootId]: 0 };
  const queue = [rootId];
  while (queue.length) {
    const cur = queue.shift()!;
    for (const next of adj[cur] || []) {
      if (levels[next] === undefined) {
        levels[next] = levels[cur] + 1;
        queue.push(next);
      }
    }
  }

  // Nodes not reached from root get level 0
  graphNodes.forEach(n => {
    if (levels[n.id] === undefined) levels[n.id] = 0;
  });

  // Group by level
  const byLevel: Record<number, string[]> = {};
  graphNodes.forEach(n => {
    const l = levels[n.id];
    byLevel[l] = byLevel[l] || [];
    byLevel[l].push(n.id);
  });

  const nodeW = 200;
  const nodeH = 90;
  const hGap = 60;
  const vGap = 100;
  const positions: Record<string, { x: number; y: number }> = {};

  Object.entries(byLevel).forEach(([levelStr, nodeIds]) => {
    const level = Number(levelStr);
    const totalW = nodeIds.length * nodeW + (nodeIds.length - 1) * hGap;
    const startX = -totalW / 2;
    nodeIds.forEach((id, i) => {
      positions[id] = {
        x: startX + i * (nodeW + hGap),
        y: level * (nodeH + vGap),
      };
    });
  });

  return positions;
}

interface Props {
  graph: GraphResponse;
}

export const GraphViewer: React.FC<Props> = ({ graph }) => {
  const navigate = useNavigate();

  const positions = useMemo(
    () => buildLayout(graph.nodes, graph.edges, graph.root_id),
    [graph]
  );

  const initialNodes: Node[] = useMemo(
    () =>
      graph.nodes.map(gn => ({
        id: gn.id,
        type: 'threat',
        position: positions[gn.id] ?? { x: 0, y: 0 },
        data: {
          label: gn.label,
          entity_type: gn.entity_type,
          is_root: gn.id === graph.root_id,
          metadata: gn.metadata,
        },
      })),
    [graph, positions]
  );

  const initialEdges: Edge[] = useMemo(
    () =>
      graph.edges.map((ge, idx) => ({
        id: `${ge.source}-${ge.target}-${idx}`,
        source: ge.source,
        target: ge.target,
        label: ge.relationship,
        labelStyle: { fill: '#64748b', fontSize: 10 },
        labelBgStyle: { fill: 'rgba(15,23,42,0.7)' },
        labelBgPadding: [4, 2] as [number, number],
        style: { stroke: 'rgba(100,116,139,0.6)', strokeWidth: 1.5 },
        markerEnd: { type: MarkerType.ArrowClosed, color: 'rgba(100,116,139,0.6)' },
        animated: ge.source === graph.root_id || ge.target === graph.root_id,
      })),
    [graph]
  );

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges(eds => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick: NodeMouseHandler = useCallback(
    (_, node) => {
      const entityType = node.data.entity_type as string;
      const basePath = entityRouteMap[entityType];
      if (basePath) {
        navigate(`${basePath}/${node.id}`);
      }
    },
    [navigate]
  );

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes as any}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={2}
        style={{ background: 'hsl(var(--background, 222 47% 7%))' }}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="rgba(100,116,139,0.15)" gap={24} variant={BackgroundVariant.Dots} size={1.5} />
        <Controls
          style={{
            background: 'rgba(15,23,42,0.85)',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: '8px',
          }}
        />
        <MiniMap
          style={{
            background: 'rgba(15,23,42,0.85)',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: '8px',
          }}
          nodeColor={n => {
            const colors: Record<string, string> = {
              indicator: '#3b82f6',
              threat_actor: '#ef4444',
              malware: '#f97316',
              campaign: '#a855f7',
              vulnerability: '#eab308',
              investigation: '#14b8a6',
              report: '#64748b',
            };
            return colors[(n.data as { entity_type: string }).entity_type] ?? '#64748b';
          }}
          maskColor="rgba(15,23,42,0.6)"
        />
        <GraphLegend />
      </ReactFlow>
    </div>
  );
};
