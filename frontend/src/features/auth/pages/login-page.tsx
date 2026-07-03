import React from 'react';

export const LoginPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md p-8 border border-border rounded-lg bg-card shadow-sm text-center">
        <h1 className="text-2xl font-bold text-foreground mb-2">Sign In</h1>
        <p className="text-muted-foreground text-sm mb-6">Login functionality will be implemented in Phase F2.</p>
        <div className="h-32 border border-dashed border-border rounded-md flex items-center justify-center bg-muted/30">
          <span className="text-sm font-medium text-muted-foreground">Auth Form Placeholder</span>
        </div>
      </div>
    </div>
  );
};
