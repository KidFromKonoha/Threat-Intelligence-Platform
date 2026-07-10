import React from 'react';
import { X } from 'lucide-react';
import { Button } from './button';

interface Props {
  isOpen: boolean;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
  isDestructive?: boolean;
}

export const ConfirmDialog: React.FC<Props> = ({
  isOpen,
  title,
  description,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  onCancel,
  isDestructive = false,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="w-full max-w-md bg-card border border-border rounded-lg shadow-lg flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-lg font-semibold">{title}</h2>
          <button onClick={onCancel} className="p-1 rounded-md hover:bg-secondary text-muted-foreground">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 text-sm text-muted-foreground">
          {description}
        </div>

        <div className="p-4 border-t border-border flex justify-end gap-3 bg-card rounded-b-lg">
          <Button type="button" variant="ghost" onClick={onCancel}>
            {cancelText}
          </Button>
          <Button 
            type="button" 
            variant={isDestructive ? 'destructive' : 'default'} 
            onClick={() => {
              onConfirm();
              onCancel();
            }}
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </div>
  );
};
