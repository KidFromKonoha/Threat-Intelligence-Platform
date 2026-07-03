import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useDashboardOrganization } from '../hooks/use-dashboard';
import { Building2, Eye, Truck, Car } from 'lucide-react';

export const OrganizationCard: React.FC = () => {
  const { data, isLoading, isError } = useDashboardOrganization();

  if (isLoading) {
    return <Card className="h-full flex items-center justify-center min-h-[160px]"><span className="text-muted-foreground text-sm">Loading Organization...</span></Card>;
  }

  if (isError || !data) {
    return <Card className="h-full flex items-center justify-center min-h-[160px]"><span className="text-destructive text-sm">Failed to load organization</span></Card>;
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Organization Summary</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-4">
        <div className="flex flex-col">
          <div className="flex items-center text-muted-foreground mb-1">
            <Building2 className="w-4 h-4 mr-2" />
            <span className="text-xs font-medium uppercase truncate">High Risk Assets</span>
          </div>
          <span className="text-2xl font-semibold text-destructive">{data.high_risk_asset_matches}</span>
        </div>
        
        <div className="flex flex-col">
          <div className="flex items-center text-muted-foreground mb-1">
            <Eye className="w-4 h-4 mr-2" />
            <span className="text-xs font-medium uppercase truncate">Watchlist Hits</span>
          </div>
          <span className="text-2xl font-semibold text-amber-500">{data.active_watchlist_matches}</span>
        </div>

        <div className="flex flex-col mt-2">
          <div className="flex items-center text-muted-foreground mb-1">
            <Truck className="w-4 h-4 mr-2" />
            <span className="text-xs font-medium uppercase truncate">Supplier Threats</span>
          </div>
          <span className="text-2xl font-semibold">{data.supplier_threats}</span>
        </div>
        
        <div className="flex flex-col mt-2">
          <div className="flex items-center text-muted-foreground mb-1">
            <Car className="w-4 h-4 mr-2" />
            <span className="text-xs font-medium uppercase truncate">Automotive Threats</span>
          </div>
          <span className="text-2xl font-semibold">{data.automotive_threats}</span>
        </div>
      </CardContent>
    </Card>
  );
};
