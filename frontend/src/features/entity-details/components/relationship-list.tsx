import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { EntitySummary, IndicatorSummary } from '../types/entity';
import { Link } from 'react-router-dom';
import { Network, Fingerprint, Bug, Skull, ShieldAlert, AlertOctagon } from 'lucide-react';

interface RelationshipListProps {
  title: string;
  items: (EntitySummary | IndicatorSummary)[];
  type: 'indicator' | 'malware' | 'threat-actor' | 'campaign' | 'vulnerability' | 'report' | 'asset' | 'mitre_technique' | 'feed';
}

export const RelationshipList: React.FC<RelationshipListProps> = ({ title, items, type }) => {
  if (!items || items.length === 0) return null;

  const getIcon = () => {
    switch (type) {
      case 'indicator': return <Fingerprint className="w-4 h-4" />;
      case 'malware': return <Bug className="w-4 h-4" />;
      case 'threat-actor': return <Skull className="w-4 h-4" />;
      case 'campaign': return <ShieldAlert className="w-4 h-4" />;
      case 'vulnerability': return <AlertOctagon className="w-4 h-4" />;
      default: return <Network className="w-4 h-4" />;
    }
  };

  const getLink = (id: string) => {
    if (['indicator', 'malware', 'campaign', 'vulnerability'].includes(type)) {
      return `/entities/${type}/${id}`;
    }
    if (type === 'threat-actor') return `/entities/threat-actor/${id}`;
    return '#'; // Fallback for unimplemented types
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          {getIcon()}
          {title} <span className="text-muted-foreground text-sm font-normal ml-auto">{items.length}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-2">
          {items.map((item, idx) => {
            const isIndicator = 'value' in item;
            const primaryText = isIndicator ? (item as IndicatorSummary).value : (item as EntitySummary).name;
            const secondaryText = isIndicator ? (item as IndicatorSummary).type : (item as EntitySummary).description;
            
            return (
              <Link key={`${item.id}-${idx}`} to={getLink(item.id)} className="flex flex-col p-2 rounded-md hover:bg-muted transition-colors border border-transparent hover:border-border">
                <span className="text-sm font-medium truncate">{primaryText}</span>
                {secondaryText && <span className="text-xs text-muted-foreground truncate">{secondaryText}</span>}
              </Link>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
