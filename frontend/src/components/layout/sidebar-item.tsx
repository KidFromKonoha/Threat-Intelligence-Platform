import React from 'react';
import { NavLink } from 'react-router-dom';
import type { NavigationItem } from '@/config/navigation';

interface SidebarItemProps {
  item: NavigationItem;
}

export const SidebarItem: React.FC<SidebarItemProps> = ({ item }) => {
  const Icon = item.icon;

  if (item.disabled) {
    return (
      <div
        className="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium text-muted-foreground/50 cursor-not-allowed"
        aria-disabled="true"
      >
        <Icon className="w-4 h-4 flex-shrink-0" />
        <span>{item.label}</span>
      </div>
    );
  }

  return (
    <NavLink to={item.path}>
      {({ isActive }) => (
        <div
          className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all active:scale-[0.98] ${
            isActive
              ? 'bg-secondary/60 text-foreground shadow-sm ring-1 ring-border/50'
              : 'text-muted-foreground hover:bg-secondary/40 hover:text-foreground'
          }`}
        >
          <Icon className={`w-4 h-4 flex-shrink-0 transition-colors ${isActive ? 'text-foreground' : 'opacity-70'}`} />
          <span>{item.label}</span>
        </div>
      )}
    </NavLink>
  );
};
