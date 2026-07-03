import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../../hooks/use-auth';
import { authApi } from '../api/auth-api';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Button } from '../../../components/ui/button';
import { ShieldAlert, Loader2 } from 'lucide-react';

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [globalError, setGlobalError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormValues) => {
    try {
      setGlobalError(null);
      const tokenResponse = await authApi.login(data.username, data.password);
      // Immediately fetch user data using the new token
      // We manually set it in localStorage here first so the authApi.getCurrentUser request picks it up
      // though typically the interceptor handles it, it might not be initialized with it yet.
      // Wait, tokenStorage is used directly by interceptors, so let's use it.
      const { tokenStorage } = await import('../../../services/auth/token-storage');
      tokenStorage.setTokens(tokenResponse.access_token, tokenResponse.refresh_token);
      
      const user = await authApi.getCurrentUser();
      
      // Complete login process in Context
      login(tokenResponse.access_token, tokenResponse.refresh_token, user);
      
      const from = (location.state as any)?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    } catch (error: any) {
      console.error('Login error:', error);
      if (error.response?.status === 401 || error.response?.status === 400) {
        setGlobalError('Invalid username or password.');
      } else {
        setGlobalError('An unexpected error occurred. Please try again later.');
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4 relative">
      <div className="absolute top-0 left-0 w-full h-1 bg-primary/20" />
      
      <div className="w-full max-w-md p-8 border border-border rounded-lg bg-card shadow-lg flex flex-col items-center">
        <div className="flex items-center justify-center w-12 h-12 rounded-lg bg-secondary text-primary mb-6">
          <ShieldAlert className="w-6 h-6" />
        </div>
        
        <h1 className="text-xl font-bold tracking-tight text-foreground mb-1">
          Threat Intelligence Platform
        </h1>
        <p className="text-sm text-muted-foreground mb-8 text-center">
          Authenticate with your SOC credentials to access the platform.
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="w-full space-y-4">
          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              type="text"
              autoComplete="username"
              placeholder="admin"
              disabled={isSubmitting}
              {...register('username')}
            />
            {errors.username && (
              <p className="text-xs text-destructive">{errors.username.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="password">Password</Label>
            </div>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              placeholder="••••••••"
              disabled={isSubmitting}
              {...register('password')}
            />
            {errors.password && (
              <p className="text-xs text-destructive">{errors.password.message}</p>
            )}
          </div>

          {globalError && (
            <div className="p-3 text-sm text-destructive-foreground bg-destructive/90 rounded-md">
              {globalError}
            </div>
          )}

          <Button type="submit" className="w-full mt-6" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Authenticating...
              </>
            ) : (
              'Sign In'
            )}
          </Button>
        </form>
      </div>
    </div>
  );
};
