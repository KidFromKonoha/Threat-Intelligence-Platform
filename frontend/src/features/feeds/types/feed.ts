export type FeedType = 'open_source' | 'commercial' | 'internal';
export type FeedStatus = 'active' | 'disabled' | 'error';

export interface FeedResponse {
  name: string;
  description: string | null;
  type: FeedType;
  enabled: boolean;
  status: FeedStatus;
  schedule: string | null;
  rate_limit: number | null;
  priority: number;
  id: string;
  authentication: Record<string, any> | null;
  last_success: string | null;
  last_failure: string | null;
  records_imported: number;
  created_at: string;
  updated_at: string;
}

export interface FeedUpdate {
  name?: string | null;
  description?: string | null;
  type?: FeedType | null;
  enabled?: boolean | null;
  status?: FeedStatus | null;
  schedule?: string | null;
  rate_limit?: number | null;
  priority?: number | null;
  authentication?: Record<string, any> | null;
}

export interface FeedRunResponse {
  id: string;
  feed_id: string;
  start_time: string;
  end_time: string | null;
  duration: number | null;
  status: string;
  records_received: number;
  records_added: number;
  records_updated: number;
  records_skipped: number;
  errors: any[] | null;
}

export interface FeedStatusDetail {
  id: string;
  name: string;
  status: string;
  last_success: string | null;
  last_failure: string | null;
  records_imported: number;
  last_run_duration: number | null;
  average_run_duration: number | null;
  total_runs: number;
  failed_runs: number;
}
