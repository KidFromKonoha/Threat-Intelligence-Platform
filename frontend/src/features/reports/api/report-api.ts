import { apiClient } from '@/api/client';
import type { ReportResponse } from '../types/report';

export type ReportType = 'daily' | 'weekly' | 'monthly' | 'executive';

export const reportApi = {
  getReport: async (type: ReportType): Promise<ReportResponse> => {
    const response = await apiClient.get(`/reports/${type}`);
    return response.data;
  },

  exportReport: async (type: ReportType): Promise<Blob> => {
    const response = await apiClient.get(`/reports/${type}/export?format=pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
