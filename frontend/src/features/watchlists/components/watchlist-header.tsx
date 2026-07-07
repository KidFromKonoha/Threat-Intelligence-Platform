import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Settings2, Trash2, Shield, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useDeleteWatchlist, useUpdateWatchlist } from '../hooks/use-watchlist';
import type { WatchlistResponse } from '../types/watchlist';

interface Props {
  watchlist: WatchlistResponse;
}

export const WatchlistHeader: React.FC<Props> = ({ watchlist }) => {
  const navigate = useNavigate();
  const { mutate: deleteWatchlist, isPending: isDeleting } = useDeleteWatchlist();
  const { mutate: updateWatchlist, isPending: isUpdating } = useUpdateWatchlist();

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this watchlist?')) {
      deleteWatchlist(watchlist.id, {
        onSuccess: () => navigate('/watchlists'),
      });
    }
  };

  const toggleEnabled = () => {
    updateWatchlist({
      id: watchlist.id,
      data: { enabled: !watchlist.enabled },
    });
  };

  return (
    <Card className="mb-6">
      <CardContent className="p-6">
        <div className="flex items-start gap-4 mb-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/watchlists')} className="mt-1 flex-shrink-0">
            <ArrowLeft className="w-5 h-5" />
          </Button>
          
          <div className="flex-1">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <Shield className="w-6 h-6 text-primary" />
                <h1 className="text-2xl font-bold tracking-tight">{watchlist.name}</h1>
                <span className={`text-xs uppercase font-bold px-2.5 py-1 rounded-full tracking-wider ml-2 ${
                  watchlist.enabled ? 'bg-emerald-500/20 text-emerald-500' : 'bg-muted text-muted-foreground'
                }`}>
                  {watchlist.enabled ? 'Active' : 'Disabled'}
                </span>
                <span className="text-xs uppercase font-bold text-muted-foreground tracking-wider bg-secondary px-2.5 py-1 rounded-sm ml-1">
                  {watchlist.watchlist_type.replace('_', ' ')}
                </span>
              </div>
              
              <div className="flex items-center gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={toggleEnabled}
                  disabled={isUpdating}
                >
                  {watchlist.enabled ? 'Disable' : 'Enable'}
                </Button>
                <Button 
                  variant="destructive" 
                  size="sm" 
                  onClick={handleDelete}
                  disabled={isDeleting}
                >
                  <Trash2 className="w-4 h-4 mr-1.5" />
                  Delete
                </Button>
              </div>
            </div>
            
            {watchlist.description && (
              <p className="text-muted-foreground text-sm max-w-3xl ml-11 mb-4">
                {watchlist.description}
              </p>
            )}

            <div className="flex items-center gap-6 mt-4 ml-11 text-xs text-muted-foreground bg-secondary/30 py-2 px-3 rounded-md w-fit border border-border/50">
              <div className="flex items-center gap-1.5">
                <Settings2 className="w-4 h-4" />
                <span className="font-semibold text-foreground">Rule:</span>
                <span className="uppercase tracking-wider">{watchlist.matching_rule}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4" />
                <span className="font-semibold text-foreground">Values:</span>
                <span>{watchlist.values.length} tracked</span>
              </div>
              <div className="border-l border-border h-4 mx-2" />
              <div>
                <span>Created {new Date(watchlist.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
