import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useDashboardSupplyChain } from '../hooks/use-dashboard';
import { ShieldAlert, Factory, Maximize2, Minimize2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export const SupplyChainMatrixWidget: React.FC = () => {
  const { data, isLoading, isError } = useDashboardSupplyChain();
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (isLoading) {
    return <Card className="h-full p-6 bg-background/50 backdrop-blur-xl border-border/50"><Skeleton className="h-48 w-full" /></Card>;
  }

  if (isError || !data) {
    return <Card className="h-full p-6 bg-background/50 backdrop-blur-xl"><span className="text-destructive text-sm">Failed to load matrix</span></Card>;
  }

  // Create heat levels based on threat count
  const maxThreats = Math.max(...data.suppliers.map(s => s.threat_count), 1);
  
  const getHeatClass = (count: number) => {
    if (count === 0) return 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500';
    const ratio = count / maxThreats;
    if (ratio > 0.7) return 'bg-destructive/20 border-destructive/50 text-destructive-foreground shadow-[0_0_15px_rgba(239,68,68,0.2)]';
    if (ratio > 0.3) return 'bg-amber-500/20 border-amber-500/50 text-amber-500';
    return 'bg-blue-500/20 border-blue-500/50 text-blue-500';
  };

  return (
    <Card className={`flex flex-col bg-gradient-to-br from-background to-background/80 backdrop-blur-xl border-border/50 shadow-xl overflow-hidden relative transition-all duration-300 ${isFullscreen ? 'fixed inset-4 z-50 h-auto' : 'h-full min-h-[300px]'}`}>
      <div className="absolute inset-0 bg-grid-white/[0.02] bg-[length:16px_16px]" />
      
      <CardHeader className="pb-4 relative z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-indigo-500/10 rounded-md">
              <Factory className="w-4 h-4 text-indigo-400" />
            </div>
            <CardTitle className="text-sm font-semibold tracking-wider uppercase text-foreground/90">Supply Chain Matrix</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-muted-foreground bg-muted/50 px-2 py-1 rounded-full border border-border/50">
              Tier 1 & 2 Suppliers
            </span>
            <button 
              onClick={() => setIsFullscreen(!isFullscreen)} 
              className="p-1.5 hover:bg-muted/50 rounded-md text-muted-foreground transition-colors"
              title={isFullscreen ? "Restore size" : "Maximize"}
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 overflow-auto relative z-10">
        {data.suppliers.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-3">
            <ShieldAlert className="w-8 h-8 text-emerald-500/50" />
            <p className="text-sm text-muted-foreground">No active threats detected against registered suppliers.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 pb-2">
            {data.suppliers.map((supplier) => (
              <Link 
                key={supplier.supplier_id} 
                to={`/search?asset=${supplier.supplier_id}`}
                className={`group relative overflow-hidden flex flex-col p-3 rounded-lg border transition-all hover:scale-[1.02] ${getHeatClass(supplier.threat_count)}`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-semibold truncate pr-2 z-10" title={supplier.supplier_name}>
                    {supplier.supplier_name}
                  </span>
                  <span className="text-xs font-bold tabular-nums z-10">
                    {supplier.threat_count}
                  </span>
                </div>
                
                <div className="mt-auto z-10">
                  <span className="text-[10px] uppercase tracking-wider opacity-80 font-medium">
                    {supplier.threat_count > 0 ? 'Active Threats' : 'Clear'}
                  </span>
                </div>
                
                {/* Subtle gradient overlay on hover */}
                <div className="absolute inset-0 opacity-0 group-hover:opacity-20 transition-opacity bg-gradient-to-t from-background to-transparent" />
              </Link>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
