import React, { useEffect, useState } from 'react';

const LEGEND_ITEMS = [
  { label: 'Indicator', colorDark: 'rgb(59, 130, 246)', colorLight: 'rgb(37, 99, 235)' },
  { label: 'Threat Actor', colorDark: 'rgb(239, 68, 68)', colorLight: 'rgb(185, 28, 28)' },
  { label: 'Malware', colorDark: 'rgb(249, 115, 22)', colorLight: 'rgb(194, 65, 12)' },
  { label: 'Campaign', colorDark: 'rgb(168, 85, 247)', colorLight: 'rgb(126, 34, 206)' },
  { label: 'Vulnerability', colorDark: 'rgb(234, 179, 8)', colorLight: 'rgb(161, 98, 7)' },
  { label: 'Investigation', colorDark: 'rgb(20, 184, 166)', colorLight: 'rgb(15, 118, 110)' },
  { label: 'Report', colorDark: 'rgb(100, 116, 139)', colorLight: 'rgb(71, 85, 105)' },
];

export const GraphLegend: React.FC = () => {
  const [isDark, setIsDark] = useState(() => document.documentElement.classList.contains('dark'));

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains('dark'));
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => observer.disconnect();
  }, []);

  return (
    <div
      style={{
        position: 'absolute',
        top: 16,
        right: 16,
        zIndex: 5,
        background: 'var(--card-bg, hsl(var(--card)))',
        border: '1px solid hsl(var(--border))',
        borderRadius: '8px',
        padding: '10px 14px',
        backdropFilter: 'blur(8px)',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <div style={{ fontSize: '10px', fontWeight: 700, color: 'hsl(var(--muted-foreground))', letterSpacing: '0.08em', marginBottom: '8px' }}>
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
                background: isDark ? item.colorDark : item.colorLight,
                flexShrink: 0,
              }}
            />
            <span style={{ fontSize: '11px', color: 'hsl(var(--foreground))' }}>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
