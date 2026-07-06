import React from 'react';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useCreateInvestigation } from '../hooks/use-investigation';

const createSchema = z.object({
  title: z.string().min(1, 'Title is required').max(100),
  description: z.string().optional(),
  status: z.enum(['open', 'in_progress', 'closed']).optional(),
  priority: z.enum(['low', 'medium', 'high', 'critical']).optional(),
});

type CreateFormValues = z.infer<typeof createSchema>;

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export const InvestigationCreateModal: React.FC<Props> = ({ isOpen, onClose }) => {
  const { mutateAsync: createInvestigation, isPending } = useCreateInvestigation();
  
  const { register, handleSubmit, reset, formState: { errors } } = useForm<CreateFormValues>({
    resolver: zodResolver(createSchema),
    defaultValues: {
      title: '',
      description: '',
      status: 'open',
      priority: 'medium',
    }
  });

  const onSubmit = async (data: CreateFormValues) => {
    try {
      await createInvestigation({
        title: data.title,
        description: data.description,
        status: data.status,
        priority: data.priority,
      });
      reset();
      onClose();
    } catch (err) {
      console.error('Failed to create investigation', err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="bg-card border border-border w-full max-w-[500px] rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Create Investigation</h2>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Title *</label>
            <Input 
              {...register('title')} 
              placeholder="e.g., Suspicious Login from Unknown IP" 
              className={errors.title ? 'border-destructive' : ''}
            />
            {errors.title && <span className="text-xs text-destructive">{errors.title.message}</span>}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Description</label>
            <textarea 
              {...register('description')} 
              placeholder="Detailed description of the incident..." 
              className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Priority</label>
              <select 
                {...register('priority')}
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Status</label>
              <select 
                {...register('status')}
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              >
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="closed">Closed</option>
              </select>
            </div>
          </div>

          <div className="pt-4 flex justify-end gap-3">
            <Button type="button" variant="outline" onClick={onClose} disabled={isPending}>
              Cancel
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? 'Creating...' : 'Create Investigation'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
