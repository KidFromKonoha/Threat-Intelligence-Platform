import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { EnrichmentData } from '../types/entity';
import { Database } from 'lucide-react';

interface EnrichmentPanelProps {
  enrichments: EnrichmentData[];
}

export const EnrichmentPanel: React.FC<EnrichmentPanelProps> = ({ enrichments }) => {
  if (!enrichments || enrichments.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Database className="w-5 h-5 text-muted-foreground" />
          Third-Party Enrichment
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {enrichments.map((enr, idx) => (
            <div key={idx} className="flex flex-col border border-border rounded-md overflow-hidden">
              <div className="bg-muted px-4 py-2 flex items-center justify-between border-b border-border">
                <span className="font-semibold text-sm">{enr.provider}</span>
                <div className="flex items-center gap-3">
                  <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                    enr.status === 'completed' ? 'bg-emerald-500/20 text-emerald-500' :
                    enr.status === 'failed' ? 'bg-destructive/20 text-destructive' :
                    'bg-secondary text-muted-foreground'
                  }`}>
                    {enr.status}
                  </span>
                  <span className="text-xs text-muted-foreground">{new Date(enr.timestamp).toLocaleString()}</span>
                </div>
              </div>
              <div className="p-4 bg-background">
                {enr.data ? (
                  <pre className="text-xs text-muted-foreground whitespace-pre-wrap font-mono max-h-40 overflow-y-auto">
                    {JSON.stringify(enr.data, null, 2)}
                  </pre>
                ) : (
                  <span className="text-sm text-muted-foreground italic">No data returned.</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
