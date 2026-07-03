import React from 'react';
import { NavLink } from 'react-router-dom';
import { NavigationItem } from '../../config/navigation';

interface SidebarItemProps {
  item: NavigationItem;
}

export const SidebarItem: React.FC<SidebarItemProps> = ({ item }) => {
  const Icon = item.icon;

  if (item.disabled) {
    return (
      <div className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-muted-foreground opacity-50 cursor-not-allowed">
        <Icon className="w-4 h-4" />
        <span>{item.label}</span>
      </div>
    );
  }

  return (
    <NavLink
      to={item.path}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
          isActive 
            ? 'bg-secondary text-secondary-foreground' 
            : 'text-muted-foreground hover:bg-secondary/50 hover:text-foreground'
        }`
      }
    >
      <Icon className="w-4 h-4" />
      <span>{item.label}</span>
    </NavLink>
  );
};
