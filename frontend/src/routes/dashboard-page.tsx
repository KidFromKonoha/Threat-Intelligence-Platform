import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useHealth } from "@/features/health/use-health";

function StatusBadge({ status }: { status: string }) {
  const color =
    status === "ok" ? "bg-green-500" : status === "degraded" ? "bg-amber-500" : "bg-red-500";
  return (
    <span className="inline-flex items-center gap-2 text-sm">
      <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
      {status}
    </span>
  );
}

export function DashboardPage() {
  const { data, isLoading, isError, error } = useHealth();

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Platform Status</h1>
        <p className="text-sm text-muted-foreground">
          Foundation phase connectivity check between frontend and backend services.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Backend Health</CardTitle>
          <CardDescription>Reported by GET /api/v1/health</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-sm text-muted-foreground">Checking backend...</p>}
          {isError && (
            <p className="text-sm text-red-500">
              Unable to reach backend: {(error as Error).message}
            </p>
          )}
          {data && (
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Overall</span>
                <StatusBadge status={data.status} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Database</span>
                <StatusBadge status={data.database.status} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Redis</span>
                <StatusBadge status={data.redis.status} />
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
