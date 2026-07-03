import React from 'react';
import type { GlobalSearchResult, IndicatorSummary, EntitySummary } from '../types/search';
import { Card, CardContent } from '@/components/ui/card';
import { Fingerprint, Bug, Skull, ShieldAlert, FileText, Wrench, AlertOctagon, Search } from 'lucide-react';

interface SearchResultsProps {
  data: GlobalSearchResult;
}

export const SearchResults: React.FC<SearchResultsProps> = ({ data }) => {
  if (data.total_hits === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
        <SearchEmptyState />
      </div>
    );
  }

  return (
    <div className="space-y-8 w-full max-w-4xl pb-10">
      <h2 className="text-sm font-medium text-muted-foreground">Found {data.total_hits} results for "{data.query}"</h2>
      
      {data.indicators.length > 0 && (
        <ResultSection title="Indicators" icon={<Fingerprint className="w-5 h-5" />}>
          {data.indicators.map(ind => (
            <IndicatorResultCard key={ind.id} item={ind} />
          ))}
        </ResultSection>
      )}

      {data.threat_actors.length > 0 && (
        <ResultSection title="Threat Actors" icon={<Skull className="w-5 h-5" />}>
          {data.threat_actors.map(actor => (
            <EntityResultCard key={actor.id} item={actor} />
          ))}
        </ResultSection>
      )}

      {data.malware.length > 0 && (
        <ResultSection title="Malware" icon={<Bug className="w-5 h-5" />}>
          {data.malware.map(mw => (
            <EntityResultCard key={mw.id} item={mw} />
          ))}
        </ResultSection>
      )}

      {data.campaigns.length > 0 && (
        <ResultSection title="Campaigns" icon={<ShieldAlert className="w-5 h-5" />}>
          {data.campaigns.map(camp => (
            <EntityResultCard key={camp.id} item={camp} />
          ))}
        </ResultSection>
      )}

      {data.vulnerabilities.length > 0 && (
        <ResultSection title="Vulnerabilities" icon={<AlertOctagon className="w-5 h-5" />}>
          {data.vulnerabilities.map(vuln => (
            <EntityResultCard key={vuln.id} item={vuln} />
          ))}
        </ResultSection>
      )}

      {data.techniques.length > 0 && (
        <ResultSection title="Techniques" icon={<Wrench className="w-5 h-5" />}>
          {data.techniques.map(tech => (
            <EntityResultCard key={tech.id} item={tech} />
          ))}
        </ResultSection>
      )}

      {data.reports.length > 0 && (
        <ResultSection title="Reports" icon={<FileText className="w-5 h-5" />}>
          {data.reports.map(rep => (
            <EntityResultCard key={rep.id} item={rep} />
          ))}
        </ResultSection>
      )}
    </div>
  );
};

const ResultSection: React.FC<{ title: string; icon: React.ReactNode; children: React.ReactNode }> = ({ title, icon, children }) => (
  <div className="space-y-3">
    <div className="flex items-center gap-2 border-b border-border pb-2">
      <div className="text-muted-foreground">{icon}</div>
      <h3 className="text-lg font-semibold">{title}</h3>
    </div>
    <div className="grid grid-cols-1 gap-3">
      {children}
    </div>
  </div>
);

const IndicatorResultCard: React.FC<{ item: IndicatorSummary }> = ({ item }) => (
  <Card className="overflow-hidden hover:bg-muted/50 transition-colors">
    <CardContent className="p-4 flex items-center justify-between">
      <div className="flex flex-col min-w-0">
        <span className="text-base font-medium truncate font-mono">{item.value}</span>
        <span className="text-xs text-muted-foreground mt-1 uppercase tracking-wider">{item.type}</span>
      </div>
      <div className="flex flex-col items-end ml-4 flex-shrink-0">
        <SeverityBadge severity={item.severity} />
        <span className="text-xs text-muted-foreground mt-1">Confidence: {item.confidence}%</span>
      </div>
    </CardContent>
  </Card>
);

const EntityResultCard: React.FC<{ item: EntitySummary }> = ({ item }) => (
  <Card className="overflow-hidden hover:bg-muted/50 transition-colors">
    <CardContent className="p-4 flex items-center justify-between">
      <div className="flex flex-col min-w-0 flex-1">
        <span className="text-base font-medium truncate">{item.name}</span>
        {item.description ? (
          <span className="text-sm text-muted-foreground mt-1 line-clamp-1">{item.description}</span>
        ) : (
          <span className="text-sm text-muted-foreground mt-1 italic opacity-50">No description provided.</span>
        )}
      </div>
    </CardContent>
  </Card>
);

const SeverityBadge: React.FC<{ severity: string }> = ({ severity }) => {
  const norm = severity.toLowerCase();
  let colorClass = 'bg-secondary text-secondary-foreground';
  
  if (norm === 'critical') colorClass = 'bg-destructive/20 text-destructive';
  else if (norm === 'high') colorClass = 'bg-amber-500/20 text-amber-500';
  else if (norm === 'medium') colorClass = 'bg-yellow-500/20 text-yellow-500';
  else if (norm === 'low') colorClass = 'bg-emerald-500/20 text-emerald-500';

  return (
    <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full tracking-wider ${colorClass}`}>
      {severity}
    </span>
  );
};

const SearchEmptyState = () => (
  <div className="flex flex-col items-center text-center p-8 border border-dashed rounded-lg bg-muted/10 w-full max-w-2xl">
    <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-4">
      <Search className="w-6 h-6 text-muted-foreground" />
    </div>
    <h3 className="text-lg font-semibold mb-2">No results found</h3>
    <p className="text-sm text-muted-foreground">Try adjusting your search query or removing filters.</p>
  </div>
);
