import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';

import { strings } from '../locales/ru';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary:', error, info.componentStack);
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="flex min-h-screen items-center justify-center bg-gray-950 text-white">
            <div className="text-center">
              <h1 className="mb-2 text-2xl font-bold">{strings.errorBoundary.heading}</h1>
              <p className="text-gray-400">{strings.errorBoundary.message}</p>
            </div>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
