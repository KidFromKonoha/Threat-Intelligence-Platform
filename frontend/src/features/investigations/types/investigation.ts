export type InvestigationStatus = 'open' | 'in_progress' | 'closed';
export type InvestigationPriority = 'low' | 'medium' | 'high' | 'critical';

export interface InvestigationResponse {
  id: string;
  title: string;
  description?: string;
  status: InvestigationStatus;
  priority: InvestigationPriority;
  owner?: string;
  created_at: string;
  updated_at: string;
  closed_at?: string;
}

export interface InvestigationCreate {
  title: string;
  description?: string;
  status?: InvestigationStatus;
  priority?: InvestigationPriority;
}

export interface InvestigationUpdate {
  title?: string;
  description?: string;
  status?: InvestigationStatus;
  priority?: InvestigationPriority;
}

export interface InvestigationSummaryResponse {
  investigation: InvestigationResponse;
  indicators: any[];
  malware: any[];
  threat_actors: any[];
  campaigns: any[];
  reports: any[];
  mitre_techniques: any[];
  vulnerabilities: any[];
}

export interface InvestigationTimelineEvent {
  id?: string;
  investigation_id?: string;
  event_type: string;
  description: string;
  details?: Record<string, any>;
  timestamp: string;
}
