import React from 'react';
import { MAIN_NAVIGATION, BOTTOM_NAVIGATION } from '../../config/navigation';
import { SidebarItem } from './sidebar-item';
import { LogOut, User } from 'lucide-react';

export const Sidebar: React.FC = () => {
  return (
    <div className="w-64 h-full border-r border-border bg-card flex flex-col">
      {/* Brand */}
      <div className="h-14 flex items-center px-6 border-b border-border">
        <span className="font-semibold text-sm tracking-wide text-foreground">TIP Platform</span>
      </div>

      {/* Main Nav */}
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        {MAIN_NAVIGATION.map((item) => (
          <SidebarItem key={item.id} item={item} />
        ))}
      </div>

      {/* Bottom Nav */}
      <div className="px-3 py-2">
        {BOTTOM_NAVIGATION.map((item) => (
          <SidebarItem key={item.id} item={item} />
        ))}
      </div>

      {/* Footer */}
      <div className="border-t border-border p-4">
        <div className="flex items-center gap-3 text-sm text-muted-foreground mb-4">
          <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-foreground">
            <User className="w-4 h-4" />
          </div>
          <div className="flex flex-col">
            <span className="font-medium text-foreground">Current User</span>
            <span className="text-xs">SOC Analyst</span>
          </div>
        </div>
        
        <button className="flex items-center gap-3 px-3 py-2 w-full rounded-md text-sm font-medium text-muted-foreground hover:bg-secondary/50 hover:text-foreground transition-colors">
          <LogOut className="w-4 h-4" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};
