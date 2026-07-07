import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X, Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useCreateWatchlist } from '../hooks/use-watchlist';
import type { WatchlistCreate } from '../types/watchlist';

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional().nullable(),
  enabled: z.boolean(),
  watchlist_type: z.string().min(1, 'Type is required'),
  matching_rule: z.enum(['exact', 'substring', 'regex']),
  values: z.array(z.string().min(1, 'Value cannot be empty')).min(1, 'At least one value is required'),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  onClose: () => void;
}

export const WatchlistCreateModal: React.FC<Props> = ({ onClose }) => {
  const { mutate: createWatchlist, isPending } = useCreateWatchlist();
  
  const [newValue, setNewValue] = useState('');

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: '',
      description: '',
      enabled: true,
      watchlist_type: 'indicator',
      matching_rule: 'exact',
      values: [],
    },
  });

  const values = watch('values');

  const handleAddValue = (e: React.FormEvent) => {
    e.preventDefault();
    if (newValue.trim() && !values.includes(newValue.trim())) {
      setValue('values', [...values, newValue.trim()]);
      setNewValue('');
    }
  };

  const handleRemoveValue = (valToRemove: string) => {
    setValue('values', values.filter(v => v !== valToRemove));
  };

  const onSubmit = (data: FormValues) => {
    createWatchlist(data as WatchlistCreate, {
      onSuccess: () => {
        onClose();
      },
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="w-full max-w-lg bg-card border border-border rounded-lg shadow-lg flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-lg font-semibold">Create Watchlist</h2>
          <button onClick={onClose} className="p-1 rounded-md hover:bg-secondary text-muted-foreground">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 overflow-y-auto flex-1">
          <form id="watchlist-form" onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Name</label>
              <input
                {...register('name')}
                className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                placeholder="e.g. Cobalt Strike C2s"
              />
              {errors.name && <p className="text-xs text-destructive mt-1">{errors.name.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Description (Optional)</label>
              <textarea
                {...register('description')}
                className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary min-h-[60px]"
                placeholder="Description of the watchlist..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Entity Type</label>
                <select
                  {...register('watchlist_type')}
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  <option value="indicator">Indicator</option>
                  <option value="threat_actor">Threat Actor</option>
                  <option value="malware">Malware</option>
                  <option value="campaign">Campaign</option>
                </select>
                {errors.watchlist_type && <p className="text-xs text-destructive mt-1">{errors.watchlist_type.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Matching Rule</label>
                <select
                  {...register('matching_rule')}
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  <option value="exact">Exact</option>
                  <option value="substring">Substring</option>
                  <option value="regex">Regex</option>
                </select>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="enabled"
                {...register('enabled')}
                className="rounded border-border bg-background"
              />
              <label htmlFor="enabled" className="text-sm font-medium">Enabled</label>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Tracked Values</label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newValue}
                  onChange={e => setNewValue(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddValue(e);
                    }
                  }}
                  className="flex-1 px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                  placeholder="Value to watch..."
                />
                <Button type="button" variant="secondary" onClick={handleAddValue}>
                  <Plus className="w-4 h-4" />
                </Button>
              </div>
              {errors.values && <p className="text-xs text-destructive mt-1">{errors.values.message}</p>}
              
              {values.length > 0 && (
                <div className="border border-border rounded-md max-h-[150px] overflow-y-auto mt-2 divide-y divide-border/50">
                  {values.map(val => (
                    <div key={val} className="flex items-center justify-between px-3 py-2 text-sm bg-secondary/20">
                      <span className="font-mono truncate mr-2">{val}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveValue(val)}
                        className="text-muted-foreground hover:text-destructive flex-shrink-0"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </form>
        </div>

        <div className="p-4 border-t border-border flex justify-end gap-3 bg-card rounded-b-lg">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isPending}>
            Cancel
          </Button>
          <Button type="submit" form="watchlist-form" disabled={isPending}>
            {isPending ? 'Creating...' : 'Create Watchlist'}
          </Button>
        </div>
      </div>
    </div>
  );
};
