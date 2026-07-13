import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Trash2, Search } from 'lucide-react';
import { useUpdateWatchlist } from '../hooks/use-watchlist';
import type { WatchlistResponse } from '../types/watchlist';

interface Props {
  watchlist: WatchlistResponse;
}

export const WatchlistEntityTable: React.FC<Props> = ({ watchlist }) => {
  const [newValue, setNewValue] = useState('');
  const [search, setSearch] = useState('');
  const { mutate: updateWatchlist, isPending } = useUpdateWatchlist();

  const handleAddValue = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newValue.trim() || watchlist.values.includes(newValue.trim())) return;
    
    updateWatchlist({
      id: watchlist.id,
      data: { values: [...watchlist.values, newValue.trim()] },
    }, {
      onSuccess: () => setNewValue('')
    });
  };

  const handleRemoveValue = (valToRemove: string) => {
    if (window.confirm(`Are you sure you want to stop watching "${valToRemove}"?`)) {
      updateWatchlist({
        id: watchlist.id,
        data: { values: watchlist.values.filter(v => v !== valToRemove) },
      });
    }
  };

  const filteredValues = watchlist.values.filter(v => 
    v.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <CardTitle>Tracked Values</CardTitle>
            <CardDescription>Entities currently monitored by this watchlist.</CardDescription>
          </div>
          <form onSubmit={handleAddValue} className="flex items-center gap-2 max-w-sm w-full">
            <input
              type="text"
              value={newValue}
              onChange={e => setNewValue(e.target.value)}
              className="flex-1 px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary"
              placeholder="Add new value..."
              disabled={isPending}
            />
            <Button type="submit" size="sm" disabled={!newValue.trim() || isPending}>
              <Plus className="w-4 h-4 mr-1" />
              Add
            </Button>
          </form>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="flex items-center px-3 py-2 bg-secondary/20 border border-border rounded-md mb-4 max-w-sm">
          <Search className="w-4 h-4 text-muted-foreground mr-2" />
          <input
            type="text"
            placeholder="Search tracked values..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-transparent border-none outline-none text-sm"
          />
        </div>

        <div className="border border-border/60 rounded-xl overflow-hidden bg-card/50 shadow-sm">
          <table className="w-full text-sm text-left">
            <thead className="text-[11px] text-muted-foreground uppercase tracking-wider bg-black/5 dark:bg-white/[0.02] border-b border-border/60">
              <tr>
                <th className="px-4 py-3 font-medium">Value</th>
                <th className="px-4 py-3 font-medium w-[100px] text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {filteredValues.length === 0 ? (
                <tr>
                  <td colSpan={2} className="px-4 py-8 text-center text-muted-foreground">
                    No values found.
                  </td>
                </tr>
              ) : (
                filteredValues.map((val) => (
                  <tr key={val} className="hover:bg-black/5 dark:hover:bg-white/[0.02] transition-colors">
                    <td className="px-4 py-3 font-mono text-xs">{val}</td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => handleRemoveValue(val)}
                        disabled={isPending}
                        className="text-muted-foreground hover:text-destructive transition-colors disabled:opacity-50"
                        title="Remove value"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};
