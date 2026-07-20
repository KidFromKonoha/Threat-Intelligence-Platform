import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { investigationApi } from '../api/investigation-api';
import { AlertCircle } from 'lucide-react';

interface Props {
  indicatorId: string;
}

export const AlertHistoryPanel: React.FC<Props> = ({ indicatorId }) => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    investigationApi.getAlertsForIndicator(indicatorId).then(data => {
      if (isMounted) {
        setAlerts(data);
        setLoading(false);
      }
    }).catch(() => {
      if (isMounted) setLoading(false);
    });
    return () => { isMounted = false; };
  }, [indicatorId]);

  if (loading) return null;

  if (alerts.length === 0) {
    return (
      <Card>
        <CardHeader className="py-3 px-4">
          <CardTitle className="text-sm flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-muted-foreground" />
            Watchlist Alerts
          </CardTitle>
        </CardHeader>
        <CardContent className="px-4 pb-4">
          <p className="text-sm text-muted-foreground">No alerts triggered for this indicator.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-red-500/20">
      <CardHeader className="py-3 px-4 bg-red-500/5">
        <CardTitle className="text-sm flex items-center gap-2 text-red-500">
          <AlertCircle className="w-4 h-4" />
          Triggered Watchlists ({alerts.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="px-4 pb-4 pt-4">
        <div className="space-y-3">
          {alerts.map(alert => (
            <div key={alert.id} className="text-sm border-b pb-2 last:border-0 last:pb-0">
              <div className="flex justify-between items-center mb-1">
                <span className="font-semibold text-foreground">Rule: {JSON.parse(alert.matched_rule || '{}').rule_type}</span>
                <Badge variant={alert.status === 'NEW' ? 'destructive' : 'secondary'} className="text-[10px]">
                  {alert.status}
                </Badge>
              </div>
              <div className="text-muted-foreground text-xs">
                Matched Value: {alert.matched_value}
              </div>
              <div className="text-muted-foreground text-xs mt-1">
                Triggered: {format(new Date(alert.updated_at), 'MMM d, yyyy HH:mm:ss')}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
