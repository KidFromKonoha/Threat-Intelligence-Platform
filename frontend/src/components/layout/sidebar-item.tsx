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
    <NavLink
      to={item.path}
      className={({ isActive }) =>
        `flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
          isActive
            ? 'bg-primary text-primary-foreground'
            : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
        }`
      }
    >
      <Icon className="w-4 h-4 flex-shrink-0" />
      <span>{item.label}</span>
    </NavLink>
  );
};
