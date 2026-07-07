import { useQuery, useMutation } from '@tanstack/react-query';
import { reportApi, type ReportType } from '../api/report-api';

export const REPORT_KEYS = {
  all: ['reports'] as const,
  type: (type: ReportType) => [...REPORT_KEYS.all, type] as const,
};

export function useReport(type: ReportType) {
  return useQuery({
    queryKey: REPORT_KEYS.type(type),
    queryFn: () => reportApi.getReport(type),
    staleTime: 5 * 60 * 1000, // Reports are heavy and generated on-the-fly, keep them cached for 5 mins
  });
}

export function useExportReport() {
  return useMutation({
    mutationFn: (type: ReportType) => reportApi.exportReport(type),
    onSuccess: (blob, type) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${type}-report-${new Date().toISOString().split('T')[0]}.pdf`; // Assuming PDF/CSV based on backend
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    },
  });
}
