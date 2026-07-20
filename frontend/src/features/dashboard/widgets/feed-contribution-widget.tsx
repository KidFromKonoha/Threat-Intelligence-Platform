import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useDashboardFeedContribution } from '../hooks/use-dashboard';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export const FeedContributionWidget: React.FC = () => {
  const { data, isLoading, isError } = useDashboardFeedContribution();

  if (isLoading) {
    return <Card className="h-full p-6 min-h-[300px]"><Skeleton className="h-full w-full" /></Card>;
  }

  if (isError || !data) {
    return <Card className="h-full p-6"><span className="text-destructive text-sm">Failed to load feed contribution</span></Card>;
  }

  const chartData = data.contribution.slice(0, 8); // Top 8 feeds

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle>Feed Contribution</CardTitle>
        <CardDescription>Intelligence sources by volume</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 w-full pt-0">
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 20, left: 30, bottom: 0 }}>
            <XAxis type="number" hide />
            <YAxis 
              type="category" 
              dataKey="feed_name" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: 'currentColor', fontSize: 11 }} 
              className="opacity-70"
            />
            <Tooltip
              cursor={{ fill: 'currentColor', opacity: 0.05 }}
              contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '6px' }}
              itemStyle={{ color: 'hsl(var(--foreground))', fontSize: '14px', fontWeight: 500 }}
              labelStyle={{ display: 'none' }}
            />
            <Bar dataKey="count" fill="hsl(var(--chart-2, var(--primary)))" radius={[0, 4, 4, 0]} barSize={24} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};
