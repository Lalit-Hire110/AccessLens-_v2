"use client";

import { useState } from "react";
import UserForm from "@/components/UserForm";
import ResultsDisplay from "@/components/ResultsDisplay";
import WhatIfSimulator from "@/components/WhatIfSimulator";
import { getPrediction, fetchAllExplanations } from "@/lib/api";
import type {
  UserInput,
  PredictionResponse,
  ExplanationResponse,
} from "@/lib/api";

export default function Home() {
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [userInput, setUserInput] = useState<UserInput | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Explanation state — keyed by recommendation index
  const [explanations, setExplanations] = useState<
    Record<number, ExplanationResponse | null>
  >({});
  const [explanationErrors, setExplanationErrors] = useState<
    Record<number, boolean>
  >({});
  const [explanationsLoading, setExplanationsLoading] = useState(false);

  async function handleSubmit(data: UserInput) {
    setLoading(true);
    setError(null);
    setResult(null);
    setUserInput(null);
    setExplanations({});
    setExplanationErrors({});
    setExplanationsLoading(false);

    try {
      // 1. Fetch predictions (blocking)
      const prediction = await getPrediction(data);
      setResult(prediction);
      setUserInput(data); // Store user input for what-if simulator
      setLoading(false);

      // 2. Fetch explanations in the background (non-blocking)
      if (prediction.recommendations.length > 0) {
        setExplanationsLoading(true);
        fetchAllExplanations(prediction.persona, prediction.recommendations)
          .then(({ data: expData, errors: expErrors }) => {
            setExplanations(expData);
            setExplanationErrors(expErrors);
          })
          .catch(() => {
            // Mark all as errored
            const allErrors: Record<number, boolean> = {};
            prediction.recommendations.forEach((_, i) => {
              allErrors[i] = true;
            });
            setExplanationErrors(allErrors);
          })
          .finally(() => setExplanationsLoading(false));
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unexpected error occurred"
      );
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-8 px-4 py-10">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-100">AccessLens v2</h1>
        <p className="mt-1 text-sm text-gray-400">
          Policy access simulation &amp; scheme recommendation system
        </p>
      </div>

      {/* Form */}
      <UserForm onSubmit={handleSubmit} loading={loading} />

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-red-800 bg-red-900/30 px-4 py-3 text-sm text-red-300">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <>
          <ResultsDisplay
            data={result}
            explanations={explanations}
            explanationErrors={explanationErrors}
            explanationsLoading={explanationsLoading}
          />

          {/* What-If Simulator */}
          {userInput && (
            <WhatIfSimulator
              baseInput={userInput}
              baselineRecommendations={result.recommendations}
            />
          )}
        </>
      )}
    </main>
  );
}
