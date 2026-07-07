export interface ReportPlatformOverview {
  total_indicators: number;
  new_indicators: number;
  active_feeds: number;
  feed_health_percentage: number;
  open_investigations: number;
  active_watchlist_matches: number;
}

export interface TopEntityStats {
  name: string;
  count: number;
}

export interface ReportThreatIntelligence {
  top_malware: TopEntityStats[];
  top_threat_actors: TopEntityStats[];
  top_campaigns: TopEntityStats[];
  top_mitre_techniques: TopEntityStats[];
  top_vulnerabilities: TopEntityStats[];
  most_active_countries: TopEntityStats[];
}

export interface InvestigationSummary {
  id: string;
  title: string;
  status: string;
  created_at: string;
  closed_at: string | null;
}

export interface InvestigationStats {
  total: number;
  open: number;
  closed: number;
}

export interface ReportInvestigations {
  open_investigations: InvestigationSummary[];
  recently_created: InvestigationSummary[];
  recently_closed: InvestigationSummary[];
  statistics: InvestigationStats;
}

export interface FeedStat {
  name: string;
  status: string;
  total_imports: number;
  failed_runs: number;
  average_runtime_seconds: number;
}

export interface ReportFeedStatistics {
  feeds: FeedStat[];
}

export interface ReportResponse {
  report_type: string;
  generated_at: string;
  platform_overview: ReportPlatformOverview;
  threat_intelligence: ReportThreatIntelligence;
  investigations: ReportInvestigations;
  feed_statistics: ReportFeedStatistics;
}
