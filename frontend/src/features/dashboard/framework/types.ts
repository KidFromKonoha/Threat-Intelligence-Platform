import { ReactNode } from 'react';

export type Role = 'admin' | 'analyst' | 'executive';
export type WidgetWidth = 'sm' | 'md' | 'lg' | 'xl' | 'full';

export interface WidgetMetadata {
  id: string;
  title: string;
  description?: string;
  supportedRoles: Role[];
  defaultWidth: WidgetWidth;
  defaultHeight?: number; // Row span or fixed height
  priority: number;
}

export interface WidgetRegistryEntry extends WidgetMetadata {
  component: React.ComponentType;
}

export interface DashboardSection {
  id: string;
  title?: string;
  widgets: {
    id: string;
    width?: WidgetWidth;
  }[];
}

export interface DashboardLayout {
  role: Role;
  sections: DashboardSection[];
}
