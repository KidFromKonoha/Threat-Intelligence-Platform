import { 
  LayoutDashboard, 
  Search, 
  ShieldAlert, 
  Network, 
  Eye, 
  FileText, 
  Database,
  Settings 
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon: LucideIcon;
  disabled?: boolean;
  // Future RBAC fields
  roles?: string[];
  permissions?: string[];
  featureFlag?: string;
}

export const MAIN_NAVIGATION: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    path: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    id: 'search',
    label: 'Search',
    path: '/search',
    icon: Search,
  },
  {
    id: 'investigations',
    label: 'Investigations',
    path: '/investigations',
    icon: ShieldAlert,
  },
  {
    id: 'threat-graph',
    label: 'Threat Graph',
    path: '/threat-graph',
    icon: Network,
    disabled: true,
  },
  {
    id: 'watchlists',
    label: 'Watchlists',
    path: '/watchlists',
    icon: Eye,
  },
  {
    id: 'reports',
    label: 'Reports',
    path: '/reports',
    icon: FileText,
  },
  {
    id: 'feeds',
    label: 'Feeds',
    path: '/feeds',
    icon: Database,
  }
];

export const BOTTOM_NAVIGATION: NavigationItem[] = [
  {
    id: 'settings',
    label: 'Settings',
    path: '/settings',
    icon: Settings,
  }
];
