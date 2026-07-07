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
  const [isDark, setIsDark] = React.useState(() => document.documentElement.classList.contains('dark'));

  React.useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains('dark'));
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

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
        labelStyle: { fill: 'hsl(var(--muted-foreground))', fontSize: 10 },
        labelBgStyle: { fill: 'hsl(var(--background))' },
        labelBgPadding: [4, 2] as [number, number],
        style: { stroke: 'hsl(var(--muted-foreground))', strokeWidth: 1.5, opacity: 0.6 },
        markerEnd: { type: MarkerType.ArrowClosed, color: 'hsl(var(--muted-foreground))' },
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
        style={{ background: 'hsl(var(--background))' }}
        proOptions={{ hideAttribution: true }}
      >
        <Background color={isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'} gap={24} variant={BackgroundVariant.Dots} size={1.5} />
        <Controls
          className="graph-controls-custom"
          style={{
            background: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          }}
        />
        <MiniMap
          style={{
            background: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          }}
          nodeColor={n => {
            const colorsDark: Record<string, string> = {
              indicator: '#3b82f6',
              threat_actor: '#ef4444',
              malware: '#f97316',
              campaign: '#a855f7',
              vulnerability: '#eab308',
              investigation: '#14b8a6',
              report: '#64748b',
            };
            const colorsLight: Record<string, string> = {
              indicator: '#2563eb',
              threat_actor: '#b91c1c',
              malware: '#c2410c',
              campaign: '#7e22ce',
              vulnerability: '#a16207',
              investigation: '#0f766e',
              report: '#475569',
            };
            const palette = isDark ? colorsDark : colorsLight;
            return palette[(n.data as { entity_type: string }).entity_type] ?? (isDark ? '#64748b' : '#94a3b8');
          }}
          maskColor={isDark ? "rgba(15,23,42,0.6)" : "rgba(255,255,255,0.6)"}
        />
        <GraphLegend />
      </ReactFlow>
    </div>
  );
};
