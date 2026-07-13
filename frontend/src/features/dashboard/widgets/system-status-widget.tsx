import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Server } from 'lucide-react';

export const SystemStatusWidget: React.FC = () => {
  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">System Status</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col space-y-3">
          {[
            { label: 'Core API Database', status: 'Operational' },
            { label: 'Redis Cache Worker', status: 'Operational' },
            { label: 'Background Job Queue', status: 'Operational' },
          ].map(({ label, status }) => (
            <div key={label} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Server className="w-3.5 h-3.5 text-muted-foreground" />
                <span className="text-sm">{label}</span>
              </div>
              <span className="text-xs font-medium text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-sm">
                {status}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
