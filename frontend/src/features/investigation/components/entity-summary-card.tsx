import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';

interface Props {
  title: string;
  type: string;
  riskScore?: number | null;
  tags?: string[];
  attributes: Record<string, any>;
}

export const EntitySummaryCard: React.FC<Props> = ({ title, type, riskScore, tags, attributes }) => {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-xl break-all">{title}</CardTitle>
            <div className="text-sm font-medium text-muted-foreground mt-1 uppercase tracking-wider">{type}</div>
          </div>
          {riskScore !== undefined && riskScore !== null && (
            <div className={`text-2xl font-bold px-3 py-1 rounded-md ${
              riskScore > 75 ? 'bg-red-500/20 text-red-500' :
              riskScore > 40 ? 'bg-orange-500/20 text-orange-500' :
              'bg-blue-500/20 text-blue-500'
            }`}>
              {riskScore}
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {tags && tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4 mt-2">
            {tags.map(t => (
              <Badge key={t} variant="secondary">{t}</Badge>
            ))}
          </div>
        )}
        <div className="grid grid-cols-2 gap-y-2 text-sm mt-4">
          {Object.entries(attributes).map(([key, val]) => {
            if (val === null || val === undefined || typeof val === 'object' || key === 'id' || key === 'value' || key === 'name' || key === 'type') return null;
            let displayVal = String(val);
            if (key.endsWith('_at') || key.endsWith('_seen')) {
              try { displayVal = format(new Date(val), 'yyyy-MM-dd HH:mm'); } catch (e) {}
            }
            return (
              <React.Fragment key={key}>
                <div className="text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</div>
                <div className="font-medium text-right truncate" title={displayVal}>{displayVal}</div>
              </React.Fragment>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
