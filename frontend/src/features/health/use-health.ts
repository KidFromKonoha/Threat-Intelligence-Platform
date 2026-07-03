import { useQuery } from "@tanstack/react-query";

import { apiClient as apiGet } from "@/api/client";

export interface ServiceStatus {
  status: string;
  detail?: string | null;
}

export interface HealthResponse {
  status: string;
  database: ServiceStatus;
  redis: ServiceStatus;
}

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const response = await apiGet.get<HealthResponse>("/health");
      return response.data;
    },
    refetchInterval: 15000,
  });
}
