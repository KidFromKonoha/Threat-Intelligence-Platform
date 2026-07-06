import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useDashboardRecentIntelligence } from '../hooks/use-dashboard';
import { ShieldAlert, Fingerprint, Bug, Skull } from 'lucide-react';

export const RecentIntelligenceCard: React.FC = () => {
  const { data, isLoading, isError } = useDashboardRecentIntelligence();

  if (isLoading) {
    return <Card className="h-full flex items-center justify-center min-h-[300px]"><span className="text-muted-foreground text-sm">Loading Recent Intelligence...</span></Card>;
  }

  if (isError || !data) {
    return <Card className="h-full flex items-center justify-center min-h-[300px]"><span className="text-destructive text-sm">Failed to load recent intelligence</span></Card>;
  }

  // Flatten the arrays to just show a mixed list of recent intel, sorted by... well it comes back as separate arrays.
  // We'll show top 2 from each category.
  
  const recentItems = [
    ...data.indicators.slice(0, 2).map(i => ({ id: i.id, icon: <Fingerprint className="w-4 h-4" />, title: i.value, type: i.type, severity: i.severity })),
    ...data.campaigns.slice(0, 2).map(c => ({ id: c.id, icon: <ShieldAlert className="w-4 h-4" />, title: c.name, type: 'Campaign', severity: 'high' })),
    ...data.malware.slice(0, 2).map(m => ({ id: m.id, icon: <Bug className="w-4 h-4" />, title: m.name, type: 'Malware', severity: 'high' })),
    ...data.threat_actors.slice(0, 2).map(t => ({ id: t.id, icon: <Skull className="w-4 h-4" />, title: t.name, type: 'Threat Actor', severity: 'critical' }))
  ];

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle>Recent Intelligence</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto pr-2 -mr-2">
        <div className="flex flex-col">
          {recentItems.length === 0 && (
            <span className="text-sm text-muted-foreground pt-2">No recent intelligence found.</span>
          )}
          {recentItems.map((item, index) => (
            <div key={`${item.id}-${index}`} className="flex items-center gap-3 border-b border-border py-3 first:pt-0 last:border-0 last:pb-0">
              <div className="p-1.5 bg-secondary text-muted-foreground rounded-md flex-shrink-0">
                {item.icon}
              </div>
              <div className="flex flex-col flex-1 min-w-0">
                <span className="text-sm font-medium leading-tight break-all line-clamp-2">{item.title}</span>
                <span className="text-xs text-muted-foreground mt-0.5">{item.type}</span>
              </div>
              <div className="flex flex-col items-end flex-shrink-0 ml-2">
                <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full tracking-wider ${
                  item.severity === 'critical' ? 'bg-destructive/20 text-destructive' :
                  item.severity === 'high' ? 'bg-amber-500/20 text-amber-500' :
                  item.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-500' :
                  'bg-emerald-500/20 text-emerald-500'
                }`}>
                  {item.severity}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
