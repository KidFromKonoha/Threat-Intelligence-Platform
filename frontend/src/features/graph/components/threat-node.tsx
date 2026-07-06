import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps, Node } from '@xyflow/react';

export interface ThreatNodeData extends Record<string, unknown> {
  label: string;
  entity_type: string;
  is_root?: boolean;
  metadata?: Record<string, unknown>;
}

export type ThreatNodeType = Node<ThreatNodeData, 'threat'>;

const entityColors: Record<string, { bg: string; border: string; text: string }> = {
  indicator: { bg: 'rgba(59, 130, 246, 0.15)', border: 'rgb(59, 130, 246)', text: '#93c5fd' },
  threat_actor: { bg: 'rgba(239, 68, 68, 0.15)', border: 'rgb(239, 68, 68)', text: '#fca5a5' },
  malware: { bg: 'rgba(249, 115, 22, 0.15)', border: 'rgb(249, 115, 22)', text: '#fdba74' },
  campaign: { bg: 'rgba(168, 85, 247, 0.15)', border: 'rgb(168, 85, 247)', text: '#d8b4fe' },
  vulnerability: { bg: 'rgba(234, 179, 8, 0.15)', border: 'rgb(234, 179, 8)', text: '#fde047' },
  investigation: { bg: 'rgba(20, 184, 166, 0.15)', border: 'rgb(20, 184, 166)', text: '#5eead4' },
  report: { bg: 'rgba(100, 116, 139, 0.15)', border: 'rgb(100, 116, 139)', text: '#94a3b8' },
};

const entityAbbrev: Record<string, string> = {
  indicator: 'IOC',
  threat_actor: 'TA',
  malware: 'MAL',
  campaign: 'CAM',
  vulnerability: 'CVE',
  investigation: 'INV',
  report: 'RPT',
};

export const ThreatNode: React.FC<NodeProps<ThreatNodeType>> = memo(({ data, selected }) => {
  const entityType = data.entity_type || 'unknown';
  const colors = entityColors[entityType] ?? { bg: 'rgba(100,116,139,0.15)', border: 'rgb(100,116,139)', text: '#94a3b8' };
  const abbrev = entityAbbrev[entityType] ?? entityType.slice(0, 3).toUpperCase();

  return (
    <div
      style={{
        background: colors.bg,
        border: `1.5px solid ${selected ? '#fff' : colors.border}`,
        borderRadius: '8px',
        padding: '10px 14px',
        minWidth: '140px',
        maxWidth: '200px',
        boxShadow: selected
          ? `0 0 0 2px ${colors.border}, 0 4px 16px rgba(0,0,0,0.4)`
          : '0 2px 8px rgba(0,0,0,0.3)',
        cursor: 'pointer',
        transition: 'box-shadow 0.15s ease',
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: colors.border, border: 'none', width: 8, height: 8 }} />

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
        <span
          style={{
            fontSize: '9px',
            fontWeight: 700,
            letterSpacing: '0.08em',
            color: colors.text,
            background: `${colors.border}22`,
            padding: '2px 5px',
            borderRadius: '3px',
            flexShrink: 0,
          }}
        >
          {abbrev}
        </span>
        {data.is_root && (
          <span
            style={{
              fontSize: '8px',
              fontWeight: 700,
              color: '#fff',
              background: 'rgba(255,255,255,0.15)',
              padding: '1px 4px',
              borderRadius: '3px',
            }}
          >
            ROOT
          </span>
        )}
      </div>

      <div
        style={{
          fontSize: '12px',
          fontWeight: 500,
          color: '#f1f5f9',
          lineHeight: 1.3,
          wordBreak: 'break-all',
          maxWidth: '170px',
          overflow: 'hidden',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
        }}
        title={data.label}
      >
        {data.label}
      </div>

      <Handle type="source" position={Position.Bottom} style={{ background: colors.border, border: 'none', width: 8, height: 8 }} />
    </div>
  );
});

ThreatNode.displayName = 'ThreatNode';
