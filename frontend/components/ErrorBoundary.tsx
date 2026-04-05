"use client";

import { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, message: "" };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message ?? "Unknown error" };
  }

  componentDidCatch(error: Error) {
    // Only log in production — dev already shows the overlay
    if (process.env.NODE_ENV === "production") {
      console.error("[AccessLens] Unhandled error:", error.message);
    }
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-6 text-center">
          <span className="text-5xl">⚠️</span>
          <h2 className="text-xl font-semibold text-content-primary">
            Something went wrong
          </h2>
          <p className="max-w-sm text-sm text-content-secondary">
            An unexpected error occurred. Please refresh the page or go back to
            the home screen.
          </p>
          {process.env.NODE_ENV === "development" && (
            <pre className="mt-2 max-w-lg rounded-lg bg-surface-elevated p-4 text-left font-mono text-xs text-danger/80 overflow-auto">
              {this.state.message}
            </pre>
          )}
          <div className="flex gap-3 mt-2">
            <button
              onClick={() => window.location.reload()}
              className="btn btn-primary text-sm"
            >
              Refresh page
            </button>
            <a href="/" className="btn btn-secondary text-sm">
              Go home
            </a>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
