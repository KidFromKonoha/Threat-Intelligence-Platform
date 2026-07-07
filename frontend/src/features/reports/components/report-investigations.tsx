import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileSearch } from 'lucide-react';
import type { ReportInvestigations, InvestigationSummary } from '../types/report';

interface Props {
  investigations: ReportInvestigations;
}

const InvestigationList = ({ title, items }: { title: string; items: InvestigationSummary[] }) => (
  <div className="space-y-3">
    <h3 className="text-sm font-semibold tracking-tight text-muted-foreground uppercase">{title}</h3>
    {items.length === 0 ? (
      <p className="text-xs text-muted-foreground italic">No investigations.</p>
    ) : (
      <div className="space-y-2 max-h-[350px] overflow-y-auto pr-2">
        {items.map(inv => (
          <div key={inv.id} className="p-3 bg-secondary/30 rounded-md border border-border flex items-start gap-3">
            <FileSearch className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="text-sm font-medium leading-none mb-1.5">{inv.title}</h4>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider ${
                  inv.status === 'open' ? 'bg-amber-500/10 text-amber-500' : 'bg-emerald-500/10 text-emerald-500'
                }`}>
                  {inv.status}
                </span>
                <span>Created {new Date(inv.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    )}
  </div>
);

export const ReportInvestigationsCard: React.FC<Props> = ({ investigations }) => {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Investigations</CardTitle>
          <div className="flex items-center gap-3 text-sm">
            <span className="font-semibold">{investigations.statistics.total} <span className="font-normal text-muted-foreground">Total</span></span>
            <span className="text-amber-500 font-semibold">{investigations.statistics.open} <span className="font-normal text-muted-foreground">Open</span></span>
            <span className="text-emerald-500 font-semibold">{investigations.statistics.closed} <span className="font-normal text-muted-foreground">Closed</span></span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InvestigationList title="Currently Open" items={investigations.open_investigations} />
          <InvestigationList title="Recently Created" items={investigations.recently_created} />
          <InvestigationList title="Recently Closed" items={investigations.recently_closed} />
        </div>
      </CardContent>
    </Card>
  );
};
