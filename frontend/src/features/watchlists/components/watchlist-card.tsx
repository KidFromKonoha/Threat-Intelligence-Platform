import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Shield, Settings2, Fingerprint, Bug, Skull, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { WatchlistResponse } from '../types/watchlist';

interface Props {
  watchlist: WatchlistResponse;
  matchCount?: number;
}

export const WatchlistCard: React.FC<Props> = ({ watchlist, matchCount }) => {
  const getIcon = () => {
    switch (watchlist.watchlist_type) {
      case 'indicator': return <Fingerprint className="w-5 h-5 text-blue-500" />;
      case 'malware': return <Bug className="w-5 h-5 text-orange-500" />;
      case 'threat_actor': return <Skull className="w-5 h-5 text-red-500" />;
      case 'campaign': return <Shield className="w-5 h-5 text-purple-500" />;
      default: return <Eye className="w-5 h-5 text-muted-foreground" />;
    }
  };

  return (
    <Link to={`/watchlists/${watchlist.id}`} className="block h-full">
      <Card className="h-full hover:bg-secondary/20 transition-colors border-border group relative overflow-hidden">
        <CardContent className="p-5 flex flex-col h-full">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-secondary rounded-md">
                {getIcon()}
              </div>
              <div>
                <h3 className="font-semibold tracking-tight text-foreground group-hover:text-primary transition-colors">
                  {watchlist.name}
                </h3>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${watchlist.enabled ? 'bg-emerald-500/10 text-emerald-500' : 'bg-muted text-muted-foreground'}`}>
                    {watchlist.enabled ? 'Active' : 'Disabled'}
                  </span>
                  <span className="text-xs text-muted-foreground uppercase font-medium tracking-wider">
                    {watchlist.watchlist_type.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </div>
            {matchCount !== undefined && matchCount > 0 && (
              <div className="flex items-center justify-center bg-destructive/10 text-destructive text-xs font-bold px-2 py-1 rounded-full">
                {matchCount} Match{matchCount !== 1 ? 'es' : ''}
              </div>
            )}
          </div>
          
          <p className="text-sm text-muted-foreground line-clamp-2 mb-4 flex-1">
            {watchlist.description || 'No description provided.'}
          </p>

          <div className="flex items-center justify-between mt-auto pt-4 border-t border-border/50 text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <Settings2 className="w-3.5 h-3.5" />
              <span>{watchlist.matching_rule}</span>
            </div>
            <div>
              <span className="font-semibold text-foreground">{watchlist.values.length}</span> values
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
};
