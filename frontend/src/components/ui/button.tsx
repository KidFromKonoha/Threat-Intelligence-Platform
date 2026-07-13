import React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cn } from '../../lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', asChild = false, ...props }, ref) => {
    
    const variants = {
      default: "bg-primary text-primary-foreground shadow-sm shadow-black/20 border border-black/10 dark:border-white/10 hover:bg-primary/90 hover:shadow-md transition-all active:scale-[0.98]",
      destructive: "bg-destructive text-destructive-foreground shadow-sm shadow-red-900/20 border border-destructive/20 hover:bg-destructive/90 transition-all active:scale-[0.98]",
      outline: "border border-input bg-background/50 shadow-sm backdrop-blur-sm hover:bg-accent hover:text-accent-foreground transition-all active:scale-[0.98]",
      secondary: "bg-secondary text-secondary-foreground shadow-sm border border-transparent hover:bg-secondary/80 hover:border-border transition-all active:scale-[0.98]",
      ghost: "hover:bg-accent hover:text-accent-foreground transition-colors active:scale-[0.98]",
      link: "text-primary underline-offset-4 hover:underline",
    };
    
    const sizes = {
      default: "h-9 px-4 py-2",
      sm: "h-8 rounded-md px-3 text-xs",
      lg: "h-10 rounded-md px-8",
      icon: "h-9 w-9",
    };

    const Comp = asChild ? Slot : "button";

    return (
      <Comp
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";
