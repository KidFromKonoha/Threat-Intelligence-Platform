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

/**
 * Dual-theme colors:
 * dark  — semi-transparent tint on near-black background  → light text
 * light — solid pastel fill on white background           → dark text
 * We read the class on <html> at render time to pick the right set.
 */
const entityColorsDark: Record<string, { bg: string; border: string; text: string; abbrevBg: string }> = {
  indicator:   { bg: 'rgba(59,130,246,0.15)',  border: 'rgb(59,130,246)',   text: '#93c5fd', abbrevBg: 'rgba(59,130,246,0.2)' },
  threat_actor:{ bg: 'rgba(239,68,68,0.15)',   border: 'rgb(239,68,68)',    text: '#fca5a5', abbrevBg: 'rgba(239,68,68,0.2)' },
  malware:     { bg: 'rgba(249,115,22,0.15)',  border: 'rgb(249,115,22)',   text: '#fdba74', abbrevBg: 'rgba(249,115,22,0.2)' },
  campaign:    { bg: 'rgba(168,85,247,0.15)',  border: 'rgb(168,85,247)',   text: '#d8b4fe', abbrevBg: 'rgba(168,85,247,0.2)' },
  vulnerability:{ bg: 'rgba(234,179,8,0.15)', border: 'rgb(234,179,8)',    text: '#fde047', abbrevBg: 'rgba(234,179,8,0.2)' },
  investigation:{ bg: 'rgba(20,184,166,0.15)',border: 'rgb(20,184,166)',   text: '#5eead4', abbrevBg: 'rgba(20,184,166,0.2)' },
  report:      { bg: 'rgba(100,116,139,0.15)', border: 'rgb(100,116,139)', text: '#94a3b8', abbrevBg: 'rgba(100,116,139,0.2)' },
};

const entityColorsLight: Record<string, { bg: string; border: string; text: string; abbrevBg: string }> = {
  indicator:   { bg: '#dbeafe', border: 'rgb(37,99,235)',   text: '#1e40af', abbrevBg: '#bfdbfe' },
  threat_actor:{ bg: '#fee2e2', border: 'rgb(185,28,28)',   text: '#991b1b', abbrevBg: '#fecaca' },
  malware:     { bg: '#ffedd5', border: 'rgb(194,65,12)',   text: '#9a3412', abbrevBg: '#fed7aa' },
  campaign:    { bg: '#f3e8ff', border: 'rgb(126,34,206)',  text: '#6b21a8', abbrevBg: '#e9d5ff' },
  vulnerability:{ bg: '#fef9c3',border: 'rgb(161,98,7)',   text: '#854d0e', abbrevBg: '#fef08a' },
  investigation:{ bg: '#ccfbf1',border: 'rgb(15,118,110)', text: '#134e4a', abbrevBg: '#99f6e4' },
  report:      { bg: '#f1f5f9', border: 'rgb(71,85,105)',   text: '#334155', abbrevBg: '#e2e8f0' },
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

function isDarkMode() {
  return document.documentElement.classList.contains('dark');
}

export const ThreatNode: React.FC<NodeProps<ThreatNodeType>> = memo(({ data, selected }) => {
  const entityType = data.entity_type || 'unknown';
  const dark = isDarkMode();
  const palette = dark ? entityColorsDark : entityColorsLight;
  const colors = palette[entityType] ?? (dark
    ? { bg: 'rgba(100,116,139,0.15)', border: 'rgb(100,116,139)', text: '#94a3b8', abbrevBg: 'rgba(100,116,139,0.2)' }
    : { bg: '#f1f5f9', border: 'rgb(71,85,105)', text: '#334155', abbrevBg: '#e2e8f0' });
  const abbrev = entityAbbrev[entityType] ?? entityType.slice(0, 3).toUpperCase();
  const labelColor = dark ? '#f1f5f9' : '#0f172a';
  const rootBadgeColor = dark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.08)';
  const rootTextColor = dark ? '#fff' : '#334155';

  return (
    <div
      style={{
        background: colors.bg,
        border: `1.5px solid ${selected ? colors.border : colors.border}`,
        outline: selected ? `2px solid ${colors.border}` : 'none',
        outlineOffset: '2px',
        borderRadius: '8px',
        padding: '10px 14px',
        minWidth: '140px',
        maxWidth: '200px',
        boxShadow: dark
          ? (selected ? `0 4px 16px rgba(0,0,0,0.5)` : '0 2px 8px rgba(0,0,0,0.3)')
          : (selected ? `0 4px 12px rgba(0,0,0,0.15)` : '0 1px 4px rgba(0,0,0,0.10)'),
        cursor: 'pointer',
        transition: 'box-shadow 0.15s ease, outline 0.1s ease',
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
            background: colors.abbrevBg,
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
              color: rootTextColor,
              background: rootBadgeColor,
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
          color: labelColor,
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
