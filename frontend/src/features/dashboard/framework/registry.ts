import { WidgetRegistryEntry } from './types';

class WidgetRegistry {
  private widgets: Map<string, WidgetRegistryEntry> = new Map();

  register(widget: WidgetRegistryEntry) {
    if (this.widgets.has(widget.id)) {
      console.warn(`Widget with ID ${widget.id} is already registered. Overwriting.`);
    }
    this.widgets.set(widget.id, widget);
  }

  get(id: string): WidgetRegistryEntry | undefined {
    return this.widgets.get(id);
  }

  getAll(): WidgetRegistryEntry[] {
    return Array.from(this.widgets.values());
  }

  getForRole(role: string): WidgetRegistryEntry[] {
    return this.getAll().filter(w => w.supportedRoles.includes(role as any));
  }
}

export const widgetRegistry = new WidgetRegistry();
