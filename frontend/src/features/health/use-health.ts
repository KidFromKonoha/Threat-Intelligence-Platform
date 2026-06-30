import { useQuery } from "@tanstack/react-query";

import { apiGet } from "@/lib/api-client";

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
    queryFn: () => apiGet<HealthResponse>("/health"),
    refetchInterval: 15000,
  });
}
