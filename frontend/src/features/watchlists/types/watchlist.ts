export interface WatchlistResponse {
  id: string;
  name: string;
  description: string | null;
  enabled: boolean;
  watchlist_type: string;
  matching_rule: string;
  values: string[];
  created_at: string;
  updated_at: string;
}

export interface WatchlistCreate {
  name: string;
  description?: string | null;
  enabled?: boolean;
  watchlist_type: string;
  matching_rule?: string;
  values: string[];
}

export interface WatchlistUpdate {
  name?: string | null;
  description?: string | null;
  enabled?: boolean | null;
  watchlist_type?: string | null;
  matching_rule?: string | null;
  values?: string[] | null;
}

export interface WatchlistMatchResponse {
  id: string;
  watchlist_id: string;
  entity_type: string;
  entity_id: string;
  match_reason: string;
  created_at: string;
  updated_at: string;
}
