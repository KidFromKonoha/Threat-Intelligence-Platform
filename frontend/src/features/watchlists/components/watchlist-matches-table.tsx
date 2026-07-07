import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Link } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';
import type { WatchlistMatchResponse } from '../types/watchlist';

interface Props {
  matches: WatchlistMatchResponse[];
}

export const WatchlistMatchesTable: React.FC<Props> = ({ matches }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Matches</CardTitle>
        <CardDescription>Entities that have matched this watchlist's criteria.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="border border-border rounded-md overflow-hidden">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted-foreground uppercase bg-secondary/50">
              <tr>
                <th className="px-4 py-3 font-medium">Entity ID</th>
                <th className="px-4 py-3 font-medium">Type</th>
                <th className="px-4 py-3 font-medium">Reason</th>
                <th className="px-4 py-3 font-medium">Matched At</th>
                <th className="px-4 py-3 font-medium text-right">View</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {matches.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">
                    No matches found yet.
                  </td>
                </tr>
              ) : (
                matches.map((match) => {
                  const typeRoute = match.entity_type === 'threat_actor' ? 'threat-actor' : match.entity_type;
                  
                  return (
                    <tr key={match.id} className="hover:bg-secondary/10 transition-colors">
                      <td className="px-4 py-3 font-mono text-xs">{match.entity_id}</td>
                      <td className="px-4 py-3 uppercase text-xs font-semibold tracking-wider">{match.entity_type.replace('_', ' ')}</td>
                      <td className="px-4 py-3">
                        <span className="inline-block px-2 py-1 bg-secondary rounded text-xs">
                          {match.match_reason}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {new Date(match.created_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Link 
                          to={`/entities/${typeRoute}/${match.entity_id}`}
                          className="inline-flex items-center justify-center p-2 text-muted-foreground hover:text-primary transition-colors"
                          title="View Entity"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};
