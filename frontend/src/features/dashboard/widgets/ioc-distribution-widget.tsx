import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useDashboardIocDistribution } from '../hooks/use-dashboard';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertCircle, Clock, PieChart } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export const IocDistributionWidget: React.FC = () => {
  const { data, isLoading, isError, dataUpdatedAt } = useDashboardIocDistribution();

  if (isLoading) {
    return (
      <Card className="h-full min-h-[300px] max-h-[450px] flex flex-col">
        <CardHeader>
          <CardTitle>IOC Distribution</CardTitle>
          <CardDescription>Breakdown by indicator type</CardDescription>
        </CardHeader>
        <CardContent className="flex-1 p-6 pt-0">
          <Skeleton className="h-full w-full" />
        </CardContent>
      </Card>
    );
  }

  if (isError || !data) {
    return (
      <Card className="h-full min-h-[300px] max-h-[450px] flex flex-col border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            Error Loading IOC Distribution
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center">
          <span className="text-muted-foreground text-sm">Failed to load IOC distribution</span>
        </CardContent>
      </Card>
    );
  }

  const rawData = data.distribution || [];
  
  // Take top 5, sum the rest as "Other"
  const processedData = rawData.slice(0, 5).map(d => ({
    name: d.type.toUpperCase(),
    value: d.count
  }));
  
  if (rawData.length > 5) {
    const otherCount = rawData.slice(5).reduce((sum, item) => sum + item.count, 0);
    processedData.push({ name: 'OTHER', value: otherCount });
  }

  return (
    <Card className="h-full min-h-[300px] max-h-[450px] flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle>IOC Distribution</CardTitle>
        <CardDescription>Breakdown by indicator type</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 w-full pt-0 pb-0">
        {processedData.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center pb-6">
            <PieChart className="w-10 h-10 text-muted-foreground mb-4 opacity-50" />
            <p className="text-muted-foreground">No indicators available to display.</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={processedData} layout="vertical" margin={{ top: 0, right: 20, left: 0, bottom: 0 }}>
              <XAxis type="number" hide />
              <YAxis 
                type="category" 
                dataKey="name" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: 'currentColor', fontSize: 10, fontWeight: 500 }} 
                className="opacity-70"
                width={80}
              />
              <Tooltip
                cursor={{ fill: 'currentColor', opacity: 0.05 }}
                contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: '6px' }}
                itemStyle={{ color: 'hsl(var(--foreground))', fontSize: '14px', fontWeight: 500 }}
                labelStyle={{ display: 'none' }}
              />
              <Bar dataKey="value" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} barSize={20} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
      <CardFooter className="pt-4 pb-4 text-xs text-muted-foreground flex items-center gap-1 border-t mt-auto">
        <Clock className="w-3 h-3" />
        Last updated {dataUpdatedAt ? formatDistanceToNow(dataUpdatedAt, { addSuffix: true }) : 'never'}
      </CardFooter>
    </Card>
  );
};
