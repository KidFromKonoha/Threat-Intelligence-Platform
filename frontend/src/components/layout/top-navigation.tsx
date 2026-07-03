import React from 'react';
import { Bell, Moon, Sun, Search, User } from 'lucide-react';
import { useTheme } from '../../providers/theme-provider';

export const TopNavigation: React.FC = () => {
  const { theme, setTheme } = useTheme();

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <header className="h-14 border-b border-border bg-card px-6 flex items-center justify-between">
      {/* Search Placeholder */}
      <div className="flex items-center max-w-md w-full bg-background border border-border rounded-md px-3 py-1.5 focus-within:ring-1 focus-within:ring-primary transition-shadow">
        <Search className="w-4 h-4 text-muted-foreground mr-2" />
        <input 
          type="text" 
          placeholder="Search indicators, actors, campaigns..." 
          className="bg-transparent border-none outline-none w-full text-sm text-foreground placeholder:text-muted-foreground"
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
