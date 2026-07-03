import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { PageError } from './page-error';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <PageError 
          title="Application Error" 
          message={this.state.error?.message || 'An unexpected error occurred.'}
          onRetry={this.handleReset}
        />
      );
    }

    return this.props.children;
  }
}
