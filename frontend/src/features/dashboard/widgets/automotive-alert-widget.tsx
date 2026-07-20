import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle } from 'lucide-react';
import { useDashboardPriorityAlerts } from '../hooks/use-dashboard';

export const AutomotiveAlertWidget: React.FC<{ width?: 'sm' | 'md' | 'lg' | 'xl' | 'full' }> = ({ width = 'full' }) => {
  const { data, isLoading } = useDashboardPriorityAlerts(5, 50);

  const alerts = data?.items || [];

  return (
    <Card className={`col-span-${width === 'full' ? '12' : '6'} border-red-900/50 bg-red-950/10`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-red-500">
          <AlertTriangle className="h-5 w-5" />
          Automotive Priority Alerts
        </CardTitle>
        <CardDescription>High risk_score observables prioritized by the Scoring Engine.</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
             {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-12 w-full animate-pulse bg-muted rounded-md" />
             ))}
          </div>
        ) : alerts.length > 0 ? (
          <div className="space-y-4">
            {alerts.map((alert: any) => (
              <div key={alert.id} className="flex flex-col sm:flex-row justify-between p-3 rounded-lg border border-red-900/30 bg-background/50 hover:bg-background/80 transition-colors">
                <div className="flex flex-col">
                  <span className="font-mono text-sm font-semibold">{alert.value}</span>
                  <span className="text-xs text-muted-foreground capitalize">{alert.type} • Source: {alert.source_count}</span>
                </div>
                <div className="flex items-center gap-2 mt-2 sm:mt-0">
                  <Badge variant="destructive" className="font-bold">
                    Score: {alert.risk_score}
                  </Badge>
                  <Badge variant="outline" className={alert.severity === 'critical' ? 'text-red-500 border-red-500' : 'text-orange-500 border-orange-500'}>
                    {alert.severity}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
            <AlertTriangle className="h-8 w-8 mb-2 opacity-50" />
            <p>No high-priority alerts detected.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
