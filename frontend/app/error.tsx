"use client";

import { useEffect } from "react";

interface Props {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: Props) {
  useEffect(() => {
    if (process.env.NODE_ENV === "production") {
      console.error("[AccessLens] Unhandled error:", error.message);
    }
  }, [error]);

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-6 text-center">
      <span className="text-5xl">⚠️</span>
      <h2 className="text-xl font-semibold text-content-primary">
        Something went wrong
      </h2>
      <p className="max-w-sm text-sm text-content-secondary">
        An unexpected error occurred. Please try again or return to the home
        screen.
      </p>
      {process.env.NODE_ENV === "development" && (
        <pre className="mt-2 max-w-lg overflow-auto rounded-lg p-4 text-left font-mono text-xs"
          style={{ background: "var(--bg-elevated)", color: "var(--danger)" }}>
          {error.message}
        </pre>
      )}
      <div className="flex gap-3 mt-2">
        <button onClick={reset} className="btn btn-primary text-sm">
          Try again
        </button>
        <a href="/" className="btn btn-secondary text-sm">
          Go home
        </a>
      </div>
    </div>
  );
}
