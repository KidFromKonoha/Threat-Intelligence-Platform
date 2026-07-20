import React, { useState, useEffect, useRef } from 'react';
import { Bell, Moon, Sun, Search, User } from 'lucide-react';
import { useTheme } from '../../providers/theme-provider';
import { useNavigate } from 'react-router-dom';
import { investigationApi } from '@/features/investigation/api/investigation-api';
import type { UnifiedSearchResponse } from '@/features/investigation/api/investigation-api';
import { Badge } from '@/components/ui/badge';

export const TopNavigation: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<UnifiedSearchResponse | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (query.trim().length >= 2) {
        investigationApi.search(query).then(res => {
          setResults(res);
          setShowDropdown(true);
        }).catch(console.error);
      } else {
        setResults(null);
        setShowDropdown(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  const navigateTo = (path: string) => {
    setShowDropdown(false);
    setQuery('');
    navigate(path);
  };

  return (
    <header className="h-14 border-b border-border/40 bg-background/95 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Search */}
      <div ref={wrapperRef} className="relative w-full max-w-md">
        <div className="flex items-center w-full bg-black/5 dark:bg-white/[0.02] border border-border/60 rounded-md px-3 h-8 focus-within:ring-2 focus-within:ring-primary/20 transition-all shadow-sm">
          <Search className="w-3.5 h-3.5 text-muted-foreground mr-2" />
          <input 
            type="text" 
            placeholder="Search indicators, actors, campaigns..." 
            className="bg-transparent border-none outline-none w-full text-xs text-foreground placeholder:text-muted-foreground"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => { if (results) setShowDropdown(true); }}
          />
        </div>
        
        {/* Dropdown */}
        {showDropdown && results && (
          <div className="absolute top-10 left-0 w-full bg-card border shadow-lg rounded-md overflow-hidden z-50 max-h-[400px] overflow-y-auto">
            {results.indicators.length > 0 && (
              <div className="p-2 border-b">
                <div className="text-xs font-semibold text-muted-foreground mb-1 uppercase px-2">Indicators</div>
                {results.indicators.map(i => (
                  <div key={i.id} onClick={() => navigateTo(`/investigation/indicator/${i.id}`)} className="px-2 py-1.5 hover:bg-muted cursor-pointer rounded text-sm flex items-center justify-between">
                    <span>{i.value}</span>
                    <Badge variant="outline" className="text-[10px] h-4 px-1">{i.type}</Badge>
                  </div>
                ))}
              </div>
            )}
            {results.threat_actors.length > 0 && (
              <div className="p-2 border-b">
                <div className="text-xs font-semibold text-muted-foreground mb-1 uppercase px-2">Threat Actors</div>
                {results.threat_actors.map(t => (
                  <div key={t.id} onClick={() => navigateTo(`/investigation/threat-actor/${t.id}`)} className="px-2 py-1.5 hover:bg-muted cursor-pointer rounded text-sm">{t.name}</div>
                ))}
              </div>
            )}
            {results.campaigns.length > 0 && (
              <div className="p-2 border-b">
                <div className="text-xs font-semibold text-muted-foreground mb-1 uppercase px-2">Campaigns</div>
                {results.campaigns.map(c => (
                  <div key={c.id} onClick={() => navigateTo(`/investigation/campaign/${c.id}`)} className="px-2 py-1.5 hover:bg-muted cursor-pointer rounded text-sm">{c.name}</div>
                ))}
              </div>
            )}
            {results.indicators.length === 0 && results.threat_actors.length === 0 && results.campaigns.length === 0 && (
              <div className="p-4 text-sm text-center text-muted-foreground">No results found</div>
            )}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4">
        <button 
          onClick={toggleTheme}
          className="text-muted-foreground hover:text-foreground transition-colors p-1.5 rounded-md hover:bg-secondary"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
        <button className="text-muted-foreground hover:text-foreground transition-colors p-1.5 rounded-md hover:bg-secondary relative">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full"></span>
        </button>
        <button className="flex items-center justify-center w-8 h-8 rounded-full bg-secondary text-foreground ml-2 border border-border">
          <User className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};

