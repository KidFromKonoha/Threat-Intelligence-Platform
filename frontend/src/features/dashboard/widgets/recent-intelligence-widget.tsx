import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useDashboardRecentIntelligence } from '../hooks/use-dashboard';
import { Link } from 'react-router-dom';
import { Clock, AlertCircle, ChevronLeft, ChevronRight, ArrowUpDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { formatDistanceToNow } from 'date-fns';

export const RecentIntelligenceWidget: React.FC = () => {
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState('created_at');
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');
  const limit = 10;
  
  const skip = (page - 1) * limit;

  const { data, isLoading, isError, dataUpdatedAt } = useDashboardRecentIntelligence(skip, limit, sortBy, order);

  const toggleSort = (column: string) => {
    if (sortBy === column) {
      setOrder(order === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setOrder('desc');
    }
    setPage(1);
  };

  if (isLoading) {
    return (
      <Card className="h-full min-h-[300px] max-h-[450px] flex flex-col">
        <CardHeader>
          <CardTitle>Recent Intelligence</CardTitle>
          <CardDescription>Latest indicators identified across all feeds</CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <Skeleton className="h-48 w-full" />
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
            Error Loading Intelligence
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center">
          <span className="text-muted-foreground text-sm">Failed to load recent intelligence</span>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full min-h-[300px] max-h-[450px] flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle>Recent Intelligence</CardTitle>
        <CardDescription>Latest indicators identified across all feeds</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 px-0 overflow-y-auto">
        <div className="min-w-[600px] px-6">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted-foreground uppercase border-b border-border/50 sticky top-0 bg-card z-10">
              <tr>
                <th className="pb-3 font-medium cursor-pointer hover:text-foreground" onClick={() => toggleSort('value')}>
                  <div className="flex items-center gap-1">Indicator <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="pb-3 font-medium cursor-pointer hover:text-foreground" onClick={() => toggleSort('type')}>
                  <div className="flex items-center gap-1">Type <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="pb-3 font-medium cursor-pointer hover:text-foreground" onClick={() => toggleSort('severity')}>
                  <div className="flex items-center gap-1">Severity <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="pb-3 font-medium cursor-pointer hover:text-foreground" onClick={() => toggleSort('confidence')}>
                  <div className="flex items-center gap-1">Confidence <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="pb-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {data.items.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-muted-foreground">No recent intelligence found.</td>
                </tr>
              ) : (
                data.items.map((item) => (
                  <tr key={item.id} className="group hover:bg-muted/50 transition-colors">
                    <td className="py-2.5">
                      <Link to={`/entities/indicator/${item.id}`} className="font-medium hover:underline text-foreground">
                        {item.value}
                      </Link>
                    </td>
                    <td className="py-2.5 text-muted-foreground uppercase text-xs">{item.type}</td>
                    <td className="py-2.5">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider ${
                        item.severity === 'critical' ? 'bg-destructive/10 text-destructive' :
                        item.severity === 'high' ? 'bg-orange-500/10 text-orange-500' :
                        item.severity === 'medium' ? 'bg-yellow-500/10 text-yellow-500' :
                        'bg-emerald-500/10 text-emerald-500'
                      }`}>
                        {item.severity}
                      </span>
                    </td>
                    <td className="py-2.5 text-muted-foreground">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 rounded-full bg-secondary overflow-hidden">
                          <div 
                            className="h-full bg-primary" 
                            style={{ width: `${item.confidence}%` }}
                          />
                        </div>
                        <span className="text-xs tabular-nums">{item.confidence}%</span>
                      </div>
                    </td>
                    <td className="py-2.5 text-right">
                      <div className="flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button variant="ghost" size="sm" className="h-6 text-[10px] px-2">Open</Button>
                        <Button variant="ghost" size="sm" className="h-6 text-[10px] px-2">Action</Button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
      <CardFooter className="pt-3 pb-3 text-xs text-muted-foreground flex items-center justify-between border-t mt-auto">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          Last updated {dataUpdatedAt ? formatDistanceToNow(dataUpdatedAt, { addSuffix: true }) : 'never'}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground">
            Page {data.page} of {Math.max(1, Math.ceil(data.total_count / limit))}
          </span>
          <div className="flex gap-1">
            <Button 
              variant="outline" 
              size="icon" 
              className="h-6 w-6" 
              disabled={page === 1}
              onClick={() => setPage(p => p - 1)}
            >
              <ChevronLeft className="h-3 w-3" />
            </Button>
            <Button 
              variant="outline" 
              size="icon" 
              className="h-6 w-6" 
              disabled={!data.has_next_page}
              onClick={() => setPage(p => p + 1)}
            >
              <ChevronRight className="h-3 w-3" />
            </Button>
          </div>
        </div>
      </CardFooter>
    </Card>
  );
};
