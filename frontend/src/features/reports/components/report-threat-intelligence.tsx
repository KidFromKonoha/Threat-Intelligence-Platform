import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { ReportThreatIntelligence, TopEntityStats } from '../types/report';

interface Props {
  intel: ReportThreatIntelligence;
}

const TopList = ({ title, items }: { title: string; items: TopEntityStats[] }) => (
  <div className="space-y-3">
    <h3 className="text-sm font-semibold tracking-tight text-muted-foreground uppercase">{title}</h3>
    {items.length === 0 ? (
      <p className="text-xs text-muted-foreground italic">No data available.</p>
    ) : (
      <ul className="space-y-2">
        {items.map((item, idx) => (
          <li key={idx} className="flex items-center justify-between text-sm">
            <span className="font-medium truncate mr-2" title={item.name}>{item.name}</span>
            <span className="text-xs font-bold bg-secondary px-2 py-0.5 rounded-full text-muted-foreground">
              {item.count}
            </span>
          </li>
        ))}
      </ul>
    )}
  </div>
);

export const ReportThreatIntelligenceCard: React.FC<Props> = ({ intel }) => {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-lg">Threat Landscape</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <TopList title="Top Malware" items={intel.top_malware} />
          <TopList title="Top Threat Actors" items={intel.top_threat_actors} />
          <TopList title="Top Campaigns" items={intel.top_campaigns} />
          <TopList title="Top Mitre Techniques" items={intel.top_mitre_techniques} />
          <TopList title="Top Vulnerabilities" items={intel.top_vulnerabilities} />
          <TopList title="Most Active Countries" items={intel.most_active_countries} />
        </div>
      </CardContent>
    </Card>
  );
};
