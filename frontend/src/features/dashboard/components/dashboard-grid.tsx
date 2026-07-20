import React from 'react';
import type { DashboardLayout, WidgetWidth } from '../framework/types';
import { widgetRegistry } from '../framework/registry';

interface DashboardGridProps {
  layout: DashboardLayout;
}

const widthToClass: Record<WidgetWidth, string> = {
  sm: 'col-span-12 md:col-span-3',
  md: 'col-span-12 lg:col-span-4',
  lg: 'col-span-12 lg:col-span-8',
  xl: 'col-span-12 lg:col-span-6',
  full: 'col-span-12',
};

export const DashboardGrid: React.FC<DashboardGridProps> = ({ layout }) => {
  return (
    <div className="flex flex-col gap-8">
      {layout.sections.map((section) => (
        <div key={section.id} className="flex flex-col gap-4">
          {section.title && (
            <h2 className="text-lg font-semibold tracking-tight text-foreground">
              {section.title}
            </h2>
          )}
          <div className="grid grid-cols-12 gap-4">
            {section.widgets.map((widgetConfig) => {
              const widget = widgetRegistry.get(widgetConfig.id);
              if (!widget) {
                console.warn(`Widget ${widgetConfig.id} not found in registry`);
                return null;
              }

              const WidgetComponent = widget.component;
              const width = widgetConfig.width || widget.defaultWidth;
              const gridClass = widthToClass[width] || 'col-span-12';

              return (
                <div key={widget.id} className={`${gridClass}`}>
                  <WidgetComponent />
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};
