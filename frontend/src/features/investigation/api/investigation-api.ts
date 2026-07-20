import { apiClient as api } from '@/api/client';

export interface EntityEvent {
  id: string;
  entity_type: string;
  entity_id: string;
  event_type: string;
  payload: any;
  created_at: string;
}

export interface InvestigationIndicatorBundle {
  indicator: any;
  risk_score: number | null;
  enrichment: any[];
  threat_actors: any[];
  campaigns: any[];
  malware: any[];
  mitre_techniques: any[];
  assets: any[];
  timeline: EntityEvent[];
}

export interface InvestigationThreatActorBundle {
  threat_actor: any;
  indicators: any[];
  campaigns: any[];
  malware: any[];
  mitre_techniques: any[];
}

export interface InvestigationCampaignBundle {
  campaign: any;
  threat_actors: any[];
  indicators: any[];
  malware: any[];
  mitre_techniques: any[];
}

export interface UnifiedSearchResponse {
  indicators: any[];
  threat_actors: any[];
  campaigns: any[];
  malware: any[];
  assets: any[];
}

export const investigationApi = {
  getIndicatorBundle: async (id: string): Promise<InvestigationIndicatorBundle> => {
    const res = await api.get(`/investigation/indicator/${id}`);
    return res.data;
  },

  getThreatActorBundle: async (id: string): Promise<InvestigationThreatActorBundle> => {
    const res = await api.get(`/investigation/threat-actor/${id}`);
    return res.data;
  },

  getCampaignBundle: async (id: string): Promise<InvestigationCampaignBundle> => {
    const res = await api.get(`/investigation/campaign/${id}`);
    return res.data;
  },

  search: async (q: string): Promise<UnifiedSearchResponse> => {
    const res = await api.get(`/investigation/search`, { params: { q } });
    return res.data;
  },
  
  getGraph: async (id: string, depth: number = 2): Promise<any> => {
    const res = await api.get(`/graph/${id}`, { params: { depth } });
    return res.data;
  },

  getAlertsForIndicator: async (id: string): Promise<any[]> => {
    const res = await api.get(`/watchlists/alerts`, { params: { indicator_id: id } });
    return res.data;
  }
};
