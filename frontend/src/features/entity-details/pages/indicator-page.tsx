import React from 'react';
import { useParams } from 'react-router-dom';
import { useIndicator } from '../hooks/use-entity';
import { EntityHeader } from '../components/entity-header';
import { EntitySkeleton } from '../components/entity-skeleton';
import { EntityError } from '../components/entity-error';
import { TimelinePanel } from '../components/timeline-panel';
import { EnrichmentPanel } from '../components/enrichment-panel';
import { RelationshipList } from '../components/relationship-list';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Info } from 'lucide-react';

export const IndicatorPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading, error } = useIndicator(id || '');

  if (isLoading) return <div className="p-6 max-w-7xl mx-auto w-full"><EntitySkeleton /></div>;
  if (error || !data) return <div className="p-6 max-w-7xl mx-auto w-full"><EntityError error={error as Error} /></div>;

  return (
    <div className="p-6 max-w-7xl mx-auto w-full flex flex-col h-full overflow-y-auto">
      <EntityHeader 
        type="Indicator"
        value={data.value}
        severity={data.severity}
        confidence={data.confidence}
        status={data.status}
        description={data.type}
        graphEntityType="indicator"
        entityId={id}
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-1 md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Info className="w-5 h-5 text-muted-foreground" />
                Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex flex-col gap-1">
                  <dt className="text-muted-foreground">Type</dt>
                  <dd className="font-medium uppercase">{data.type}</dd>
                </div>
                <div className="flex flex-col gap-1">
                  <dt className="text-muted-foreground">Risk Score</dt>
                  <dd className="font-medium">{data.risk_score}</dd>
                </div>
                <div className="flex flex-col gap-1">
                  <dt className="text-muted-foreground">First Seen</dt>
                  <dd className="font-medium">{data.first_seen ? new Date(data.first_seen).toLocaleString() : 'Unknown'}</dd>
                </div>
                <div className="flex flex-col gap-1">
                  <dt className="text-muted-foreground">Last Seen</dt>
                  <dd className="font-medium">{data.last_seen ? new Date(data.last_seen).toLocaleString() : 'Unknown'}</dd>
                </div>
                {data.tags && data.tags.length > 0 && (
                  <div className="flex flex-col gap-1 col-span-2 mt-2">
                    <dt className="text-muted-foreground mb-1">Tags</dt>
                    <dd className="flex flex-wrap gap-2">
                      {data.tags.map(tag => (
                        <span key={tag} className="bg-secondary px-2 py-1 rounded-md text-xs font-medium">{tag}</span>
                      ))}
                    </dd>
                  </div>
                )}
              </dl>
            </CardContent>
          </Card>

          <TimelinePanel events={data.timeline} />
          
          <EnrichmentPanel enrichments={data.enrichments} />
        </div>

        <div className="col-span-1 space-y-6">
          <RelationshipList title="Related Indicators" type="indicator" items={data.related_indicators} />
          <RelationshipList title="Threat Actors" type="threat-actor" items={data.threat_actors} />
          <RelationshipList title="Malware" type="malware" items={data.malware} />
          <RelationshipList title="Campaigns" type="campaign" items={data.campaigns} />
          <RelationshipList title="Vulnerabilities" type="vulnerability" items={data.vulnerabilities} />
          <RelationshipList title="Mitre Techniques" type="mitre_technique" items={data.mitre_techniques} />
          <RelationshipList title="Feed Sources" type="feed" items={data.feed_sources} />
        </div>
      </div>
    </div>
  );
};
