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
  created_at?: string;
  source?: string;
}

export interface EntitySummary {
  id: string;
  name: string;
  entity_type: string;
  description: string | null;
}

// Phase 2.3 Legacy
export interface TrendMetric {
  count: number;
  trend: 'up' | 'down' | 'flat';
}

export interface DashboardIntelligenceSnapshotResponse {
  new_indicators: TrendMetric;
  new_threat_actors: TrendMetric;
  new_malware: TrendMetric;
  new_campaigns: TrendMetric;
  new_reports: TrendMetric;
  open_investigations: TrendMetric;
}

export interface DashboardHighSeverityIntelligenceResponse {
  indicators: IndicatorSummary[];
}

export interface IocDistribution {
  type: string;
  count: number;
}

export interface DashboardIocDistributionResponse {
  distribution: IocDistribution[];
}

export interface FeedContribution {
  feed_name: string;
  count: number;
}

export interface DashboardFeedContributionResponse {
  contribution: FeedContribution[];
}

export interface DashboardInvestigationSummaryResponse {
  open: number;
  high_priority: number;
  closed: number;
  recently_updated: number;
}

// ── New Phase 2.4 Types ─────────────────────────────────────────────────────

export interface Insight {
  id: string;
  type: string;
  title: string;
  description: string;
  severity: string;
  metric?: number;
  trend?: 'up' | 'down' | 'flat';
  entity_type?: string;
  entity_id?: string;
  timestamp: string;
}

export interface DashboardIntelligenceHighlightsResponse {
  insights: Insight[];
}

export interface PriorityQueueItem {
  id: string;
  icon: string;
  item_type: string;
  title: string;
  subtitle: string;
  priority: string;
  action: string;
  timestamp: string;
  reference_id?: string;
}

export interface DashboardPriorityQueueResponse {
  items: PriorityQueueItem[];
}

export interface DashboardInvestigationHealthResponse {
  open: number;
  high_priority: number;
  overdue: number;
  updated_today: number;
}

export interface WatchlistActivity {
  watchlist_id: string;
  watchlist_name: string;
  hits_today: number;
}

export interface DashboardWatchlistActivityResponse {
  activities: WatchlistActivity[];
}

export interface RecentIntelligenceItem {
  id: string;
  type: string;
  value: string;
  severity: string;
  confidence: number;
  risk_score: number;
  source?: string;
  created_at: string;
  tags: string[];
}

export interface DashboardRecentIntelligenceResponse {
  items: RecentIntelligenceItem[];
  total_count: number;
  page: number;
  has_next_page: boolean;
}

export interface GeospatialCountryCount {
  country: string;
  count: number;
}

export interface DashboardGeospatialResponse {
  countries: GeospatialCountryCount[];
}

export interface SupplierThreatCount {
  supplier_id: string;
  supplier_name: string;
  threat_count: number;
}

export interface DashboardSupplyChainResponse {
  suppliers: SupplierThreatCount[];
}
