import React, { useState } from 'react';
import { Bell, Moon, Sun, Search, User } from 'lucide-react';
import { useTheme } from '../../providers/theme-provider';
import { useNavigate } from 'react-router-dom';

export const TopNavigation: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const navigate = useNavigate();
  const [headerSearch, setHeaderSearch] = useState('');

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const handleSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && headerSearch.trim()) {
      const params = new URLSearchParams();
      params.set('q', headerSearch.trim());
      navigate(`/search?${params.toString()}`);
      setHeaderSearch('');
    }
  };

  return (
    <header className="h-14 border-b border-border/40 bg-background/95 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Search */}
      <div className="flex items-center max-w-md w-full bg-black/5 dark:bg-white/[0.02] border border-border/60 rounded-md px-3 h-8 focus-within:ring-2 focus-within:ring-primary/20 transition-all shadow-sm">
        <Search className="w-3.5 h-3.5 text-muted-foreground mr-2" />
        <input 
          type="text" 
          placeholder="Search indicators, actors, campaigns..." 
          className="bg-transparent border-none outline-none w-full text-xs text-foreground placeholder:text-muted-foreground"
          value={headerSearch}
          onChange={(e) => setHeaderSearch(e.target.value)}
          onKeyDown={handleSearch}
        />
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4">
        <button 
          onClick={toggleTheme}
          className="text-muted-foreground hover:text-foreground transition-colors p-1.5 rounded-md hover:bg-secondary"
        >
          {theme === 'dark' ? (
            <Sun className="w-4 h-4" />
          ) : (
            <Moon className="w-4 h-4" />
          )}
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
