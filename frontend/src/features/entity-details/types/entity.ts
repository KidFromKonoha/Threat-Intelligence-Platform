export interface EntitySummary {
  id: string;
  name: string;
  entity_type: string;
  description: string | null;
}

export interface IndicatorSummary {
  id: string;
  type: string;
  value: string;
  confidence: number;
  severity: string;
  entity_type: string;
}

export interface TimelineEvent {
  event_type: string;
  description: string;
  timestamp: string;
}

export interface EnrichmentData {
  provider: string;
  status: string;
  data: any | null;
  timestamp: string;
}

export interface IndicatorFullDetailResponse {
  id: string;
  type: string;
  value: string;
  confidence: number;
  severity: string;
  risk_score: number;
  status: string;
  first_seen: string | null;
  last_seen: string | null;
  tags: string[] | null;
  created_at: string;
  updated_at: string;
  feed_sources: EntitySummary[];
  related_indicators: IndicatorSummary[];
  threat_actors: EntitySummary[];
  malware: EntitySummary[];
  campaigns: EntitySummary[];
  vulnerabilities: EntitySummary[];
  assets: EntitySummary[];
  mitre_techniques: EntitySummary[];
  whois: any | null;
  passive_dns: any[] | null;
  enrichments: EnrichmentData[];
  timeline: TimelineEvent[];
  comments: any[];
}

export interface ThreatActorDetailResponse {
  id: string;
  name: string;
  aliases: string[] | null;
  description: string | null;
  motivation: string | null;
  country: string | null;
  sophistication: string;
  first_seen: string | null;
  last_seen: string | null;
  created_at: string;
  updated_at: string;
  references: string[] | null;
  campaigns: EntitySummary[];
  malware: EntitySummary[];
  indicators: IndicatorSummary[];
  mitre_techniques: EntitySummary[];
  timeline: TimelineEvent[];
}

export interface MalwareDetailResponse {
  id: string;
  name: string;
  aliases: string[] | null;
  family: string | null;
  category: string | null;
  description: string | null;
  capabilities: string[] | null;
  persistence: string | null;
  communication: string | null;
  created_at: string;
  updated_at: string;
  campaigns: EntitySummary[];
  threat_actors: EntitySummary[];
  indicators: IndicatorSummary[];
  mitre_techniques: EntitySummary[];
  timeline: TimelineEvent[];
}

export interface CampaignDetailResponse {
  id: string;
  name: string;
  description: string | null;
  first_seen: string | null;
  last_seen: string | null;
  created_at: string;
  updated_at: string;
  references: string[] | null;
  threat_actors: EntitySummary[];
  malware: EntitySummary[];
  indicators: IndicatorSummary[];
  reports: EntitySummary[];
  timeline: TimelineEvent[];
}

export interface VulnerabilityDetailResponse {
  id: string;
  cve: string;
  description: string | null;
  cvss: number | null;
  epss: number | null;
  kev: boolean;
  exploited: boolean;
  patch_available: boolean;
  created_at: string;
  updated_at: string;
  references: string[] | null;
  threat_actors: EntitySummary[];
  malware: EntitySummary[];
  campaigns: EntitySummary[];
  timeline: TimelineEvent[];
}
