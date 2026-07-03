import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { useDashboardThreatActivity } from '../hooks/use-dashboard';
import { BarChart, Bar, XAxis, Tooltip, ResponsiveContainer, YAxis, CartesianGrid } from 'recharts';

export const ThreatActivityCard: React.FC = () => {
  const { data, isLoading, isError } = useDashboardThreatActivity();

  if (isLoading) {
    return <Card className="h-full flex items-center justify-center min-h-[300px]"><span className="text-muted-foreground text-sm">Loading Threat Activity...</span></Card>;
  }

  if (isError || !data) {
    return <Card className="h-full flex items-center justify-center min-h-[300px]"><span className="text-destructive text-sm">Failed to load threat activity</span></Card>;
  }

  // Format data for chart
  const chartData = data.indicators_by_day.map(d => ({
    date: new Date(d.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    count: d.count
  }));

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle>Threat Activity</CardTitle>
        <CardDescription>Indicators over the last 30 days</CardDescription>
      </CardHeader>
      <CardContent className="w-full h-[240px] pt-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="currentColor" className="opacity-10" />
            <XAxis 
              dataKey="date" 
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 11, fill: 'currentColor' }}
              className="opacity-50"
              minTickGap={20}
            />
            <YAxis 
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 11, fill: 'currentColor' }}
              className="opacity-50"
            />
            <Tooltip 
              cursor={{ fill: 'currentColor', opacity: 0.1 }}
              contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '6px' }}
              labelStyle={{ color: 'hsl(var(--muted-foreground))', fontSize: '12px', marginBottom: '4px' }}
              itemStyle={{ color: 'hsl(var(--foreground))', fontSize: '14px', fontWeight: 500 }}
            />
            <Bar dataKey="count" fill="hsl(var(--primary))" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
