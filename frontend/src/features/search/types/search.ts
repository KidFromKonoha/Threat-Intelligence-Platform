export interface IndicatorSummary {
  id: string;
  type: string;
  value: string;
  confidence: number;
  severity: string;
  entity_type: string;
}

export interface EntitySummary {
  id: string;
  name: string;
  entity_type: string;
  description: string | null;
}

export interface GlobalSearchResult {
  query: string;
  total_hits: number;
  indicators: IndicatorSummary[];
  malware: EntitySummary[];
  threat_actors: EntitySummary[];
  campaigns: EntitySummary[];
  reports: EntitySummary[];
  techniques: EntitySummary[];
  vulnerabilities: EntitySummary[];
}

export interface SearchParams {
  q: string;
  limit?: number;
}
