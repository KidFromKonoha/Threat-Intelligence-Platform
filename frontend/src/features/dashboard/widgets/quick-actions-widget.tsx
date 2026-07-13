import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Search, ShieldCheck, Plus, Server } from 'lucide-react';
import { Link } from 'react-router-dom';

export const QuickActionsWidget: React.FC = () => {
  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wide">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-2">
        <Button variant="outline" size="sm" className="justify-start" asChild>
          <Link to="/search" className="flex items-center">
            <Search className="w-3.5 h-3.5 mr-2" /> Search Indicators
          </Link>
        </Button>
        <Button variant="outline" size="sm" className="justify-start" asChild>
          <Link to="/watchlists" className="flex items-center">
            <ShieldCheck className="w-3.5 h-3.5 mr-2" /> View Watchlists
          </Link>
        </Button>
        <Button variant="outline" size="sm" className="justify-start" asChild>
          <Link to="/investigations" className="flex items-center">
            <Plus className="w-3.5 h-3.5 mr-2" /> New Investigation
          </Link>
        </Button>
        <Button variant="outline" size="sm" className="justify-start" asChild>
          <Link to="/feeds" className="flex items-center">
            <Server className="w-3.5 h-3.5 mr-2" /> Manage Feeds
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
};
