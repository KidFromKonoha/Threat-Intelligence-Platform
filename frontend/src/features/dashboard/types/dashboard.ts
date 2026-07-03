export interface FeedHealthScore {
  healthy_feeds: number;
  error_feeds: number;
  total_active_feeds: number;
  health_percentage: number;
}

export interface DashboardOverviewResponse {
  total_indicators: number;
  new_indicators_24h: number;
  active_feeds: number;
  feed_health: FeedHealthScore;
  open_investigations: number;
}

export interface DashboardOrganizationResponse {
  high_risk_asset_matches: number;
  supplier_threats: number;
  automotive_threats: number;
  active_watchlist_matches: number;
}

export interface DailyCount {
  date: string;
  count: number;
}

export interface TopEntity {
  id: string;
  name: string;
  count: number;
}

export interface DashboardThreatActivityResponse {
  indicators_by_day: DailyCount[];
  top_threat_actors: TopEntity[];
  top_malware_families: TopEntity[];
  top_campaigns: TopEntity[];
  top_countries: TopEntity[];
  top_mitre_techniques: TopEntity[];
}

export interface FeedStatusDetail {
  id: string;
  name: string;
  status: 'active' | 'disabled' | 'error';
  last_success: string | null;
  last_failure: string | null;
  records_imported: number;
  last_run_duration: number | null;
  average_run_duration: number | null;
  total_runs: number;
  failed_runs: number;
}

export interface DashboardFeedStatusResponse {
  feeds: FeedStatusDetail[];
}

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

export interface DashboardRecentIntelligenceResponse {
  indicators: IndicatorSummary[];
  campaigns: EntitySummary[];
  malware: EntitySummary[];
  threat_actors: EntitySummary[];
  vulnerabilities: EntitySummary[];
}
