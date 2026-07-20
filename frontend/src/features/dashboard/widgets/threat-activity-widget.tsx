import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useDashboardThreatActivity } from '../hooks/use-dashboard';
import { LineChart, Line, XAxis, Tooltip, ResponsiveContainer, YAxis, CartesianGrid } from 'recharts';

export const ThreatActivityWidget: React.FC = () => {
  const [days, setDays] = useState<number>(30);
  const { data, isLoading, isError } = useDashboardThreatActivity(days);

  if (isLoading) {
    return (
      <Card className="h-full min-h-[300px] p-4">
        <div className="space-y-3">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-48" />
          <Skeleton className="h-48 w-full mt-4" />
        </div>
      </Card>
    );
  }

  if (isError || !data) {
    return <Card className="h-full flex items-center justify-center min-h-[300px]"><span className="text-destructive text-sm">Failed to load threat activity</span></Card>;
  }

  const chartData = data.indicators_by_day.map(d => ({
    date: new Date(d.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    count: d.count
  }));

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <div>
          <CardTitle>Threat Activity</CardTitle>
          <CardDescription>Indicators over time</CardDescription>
        </div>
        <div className="flex bg-secondary/50 p-0.5 rounded-md text-xs font-medium border border-border/50">
          {[1, 7, 30].map(d => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-2.5 py-1 rounded-sm transition-colors ${days === d ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
            >
              {d === 1 ? '24h' : `${d}d`}
            </button>
          ))}
        </div>
      </CardHeader>
      <CardContent className="w-full flex-1 pt-4 min-h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="currentColor" className="opacity-10" />
            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 11, fill: 'currentColor' }}
              className="opacity-50"
              minTickGap={30}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 11, fill: 'currentColor' }}
              className="opacity-50"
            />
            <Tooltip
              contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '6px' }}
              labelStyle={{ color: 'hsl(var(--muted-foreground))', fontSize: '12px', marginBottom: '4px' }}
              itemStyle={{ color: 'hsl(var(--primary))', fontSize: '14px', fontWeight: 500 }}
            />
            <Line 
              type="monotone" 
              dataKey="count" 
              stroke="hsl(var(--primary))" 
              strokeWidth={2} 
              dot={false}
              activeDot={{ r: 4, fill: 'hsl(var(--primary))' }} 
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
