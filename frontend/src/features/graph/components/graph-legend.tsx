import React from 'react';

const LEGEND_ITEMS = [
  { label: 'Indicator', color: 'rgb(59, 130, 246)' },
  { label: 'Threat Actor', color: 'rgb(239, 68, 68)' },
  { label: 'Malware', color: 'rgb(249, 115, 22)' },
  { label: 'Campaign', color: 'rgb(168, 85, 247)' },
  { label: 'Vulnerability', color: 'rgb(234, 179, 8)' },
  { label: 'Investigation', color: 'rgb(20, 184, 166)' },
  { label: 'Report', color: 'rgb(100, 116, 139)' },
];

export const GraphLegend: React.FC = () => (
  <div
    style={{
      position: 'absolute',
      bottom: 56,
      left: 16,
      zIndex: 5,
      background: 'rgba(15, 23, 42, 0.85)',
      border: '1px solid rgba(255,255,255,0.08)',
      borderRadius: '8px',
      padding: '10px 14px',
      backdropFilter: 'blur(8px)',
    }}
  >
    <div style={{ fontSize: '10px', fontWeight: 700, color: '#64748b', letterSpacing: '0.08em', marginBottom: '8px' }}>
      ENTITY TYPES
    </div>
    <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
      {LEGEND_ITEMS.map(item => (
        <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
          <span
            style={{
              width: 10,
              height: 10,
              borderRadius: '2px',
              background: item.color,
              flexShrink: 0,
            }}
          />
          <span style={{ fontSize: '11px', color: '#cbd5e1' }}>{item.label}</span>
        </div>
      ))}
    </div>
  </div>
);
