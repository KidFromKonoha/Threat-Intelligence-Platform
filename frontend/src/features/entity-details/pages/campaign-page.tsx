import React from 'react';
import { useParams } from 'react-router-dom';
import { useCampaign } from '../hooks/use-entity';
import { EntityHeader } from '../components/entity-header';
import { EntitySkeleton } from '../components/entity-skeleton';
import { EntityError } from '../components/entity-error';
import { TimelinePanel } from '../components/timeline-panel';
import { RelationshipList } from '../components/relationship-list';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Info } from 'lucide-react';

export const CampaignPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading, error } = useCampaign(id || '');

  if (isLoading) return <div className="p-6 max-w-7xl mx-auto w-full"><EntitySkeleton /></div>;
  if (error || !data) return <div className="p-6 max-w-7xl mx-auto w-full"><EntityError error={error as Error} /></div>;

  return (
    <div className="p-6 max-w-7xl mx-auto w-full flex flex-col h-full overflow-y-auto">
      <EntityHeader 
        type="Campaign"
        value={data.name}
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
              {data.description && <p className="text-sm text-muted-foreground mb-6 leading-relaxed">{data.description}</p>}
              <dl className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex flex-col gap-1">
                  <dt className="text-muted-foreground">First Seen</dt>
                  <dd className="font-medium">{data.first_seen ? new Date(data.first_seen).toLocaleString() : 'Unknown'}</dd>
                </div>
                <div className="flex flex-col gap-1">
                  <dt className="text-muted-foreground">Last Seen</dt>
                  <dd className="font-medium">{data.last_seen ? new Date(data.last_seen).toLocaleString() : 'Unknown'}</dd>
                </div>
              </dl>
            </CardContent>
          </Card>

          <TimelinePanel events={data.timeline} />
        </div>

        <div className="col-span-1 space-y-6">
          <RelationshipList title="Indicators" type="indicator" items={data.indicators} />
          <RelationshipList title="Threat Actors" type="threat-actor" items={data.threat_actors} />
          <RelationshipList title="Malware" type="malware" items={data.malware} />
          <RelationshipList title="Reports" type="report" items={data.reports} />
        </div>
      </div>
    </div>
  );
};
