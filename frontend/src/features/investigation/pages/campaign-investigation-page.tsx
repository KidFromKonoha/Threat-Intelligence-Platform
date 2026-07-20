import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { investigationApi, InvestigationCampaignBundle } from '../api/investigation-api';
import { EntitySummaryCard } from '../components/entity-summary-card';
import { RelationshipExplorer } from '../components/relationship-explorer';
import { RelatedEntitiesPanel } from '../components/related-entities-panel';
import { Skeleton } from '@/components/ui/skeleton';

export const CampaignInvestigationPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [bundle, setBundle] = useState<InvestigationCampaignBundle | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    let isMounted = true;
    setLoading(true);
    investigationApi.getCampaignBundle(id).then(data => {
      if (isMounted) {
        setBundle(data);
        setLoading(false);
      }
    }).catch(console.error);
    return () => { isMounted = false; };
  }, [id]);

  if (loading) return <div className="p-6"><Skeleton className="h-[500px] w-full" /></div>;
  if (!bundle) return <div className="p-6 text-red-500">Failed to load investigation bundle.</div>;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6 flex flex-col min-h-screen">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Campaign Investigation</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1 flex flex-col gap-6">
          <EntitySummaryCard 
            title={bundle.campaign.name} 
            type="Campaign"
            attributes={bundle.campaign}
          />
        </div>
        
        <div className="md:col-span-2 flex flex-col gap-6">
          <div className="h-[500px] border rounded-lg overflow-hidden shadow-sm bg-background">
            <RelationshipExplorer entityId={id!} entityType="campaign" />
          </div>
          <RelatedEntitiesPanel 
            threatActors={bundle.threat_actors}
            malware={bundle.malware}
            mitreTechniques={bundle.mitre_techniques}
            indicators={bundle.indicators}
          />
        </div>
      </div>
    </div>
  );
};
