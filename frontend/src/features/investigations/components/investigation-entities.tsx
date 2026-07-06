import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Link } from 'react-router-dom';
import { Shield, Target, Bug, Activity, Server, FileWarning } from 'lucide-react';
import type { InvestigationSummaryResponse } from '../types/investigation';

interface Props {
  summary: InvestigationSummaryResponse;
}

export const InvestigationEntities: React.FC<Props> = ({ summary }) => {
  
  const sections = [
    { title: 'Indicators', data: summary.indicators, icon: Target, linkPrefix: '/entities/indicator/' },
    { title: 'Malware', data: summary.malware, icon: Bug, linkPrefix: '/entities/malware/' },
    { title: 'Threat Actors', data: summary.threat_actors, icon: Shield, linkPrefix: '/entities/threat-actor/' },
    { title: 'Campaigns', data: summary.campaigns, icon: Activity, linkPrefix: '/entities/campaign/' },
    { title: 'Vulnerabilities', data: summary.vulnerabilities, icon: Server, linkPrefix: '/entities/vulnerability/' },
    { title: 'Reports', data: summary.reports, icon: FileWarning, linkPrefix: '/entities/report/' },
  ].filter(section => section.data && section.data.length > 0);

  if (sections.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Related Entities</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground text-sm">
            No related entities linked to this investigation.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {sections.map(section => (
        <Card key={section.title}>
          <CardHeader className="py-4">
            <CardTitle className="text-lg flex items-center gap-2">
              <section.icon className="w-5 h-5 text-muted-foreground" />
              {section.title} ({section.data.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="divide-y divide-border border rounded-md">
              {section.data.map((item: any) => (
                <div key={item.id} className="p-3 flex items-center justify-between hover:bg-muted/50 transition-colors">
                  <div className="flex flex-col">
                    <Link to={`${section.linkPrefix}${item.id}`} className="font-semibold text-sm hover:underline">
                      {item.value || item.name || item.title || item.cve_id || `ID: ${item.id}`}
                    </Link>
                    {item.description && (
                      <span className="text-xs text-muted-foreground line-clamp-1">{item.description}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
