"use client";

import { useState } from "react";
import type { UserInput, SimulateResponse, SchemeResult } from "@/lib/api";
import { simulate } from "@/lib/api";
import {
  getAccessGapLevel,
  getAccessGapInfo,
  getScoreLabel,
  formatScoreChange,
} from "@/lib/utils";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface Props {
  baseInput: UserInput;
  baselineRecommendations: SchemeResult[];
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function WhatIfSimulator({
  baseInput,
  baselineRecommendations,
}: Props) {
  const [documentCompleteness, setDocumentCompleteness] = useState(
    typeof baseInput.document_completeness === "number"
      ? baseInput.document_completeness
      : 0.75
  );
  const [digitalAccess, setDigitalAccess] = useState(
    baseInput.digital_access || "full"
  );

  const [simulationResult, setSimulationResult] =
    useState<SimulateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"original" | "simulated">(
    "original"
  );

  // Check if changes were made
  const hasChanges =
    documentCompleteness !==
      (typeof baseInput.document_completeness === "number"
        ? baseInput.document_completeness
        : 0.75) || digitalAccess !== baseInput.digital_access;

  async function handleSimulate() {
    if (!hasChanges) return;

    setLoading(true);
    setError(null);

    try {
      const result = await simulate({
        base_input: baseInput,
        changes: {
          document_completeness: documentCompleteness,
          digital_access: digitalAccess,
        },
      });

      setSimulationResult(result);
      setViewMode("simulated");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Simulation failed"
      );
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setDocumentCompleteness(
      typeof baseInput.document_completeness === "number"
        ? baseInput.document_completeness
        : 0.75
    );
    setDigitalAccess(baseInput.digital_access || "full");
    setSimulationResult(null);
    setViewMode("original");
    setError(null);
  }

  // Get recommendations to display based on view mode
  const displayRecommendations =
    viewMode === "simulated" && simulationResult
      ? simulationResult.simulated.recommendations
      : baselineRecommendations;

  return (
    <div className="space-y-6">
      {/* What-If Controls */}
      <div className="rounded-2xl border border-gray-700 bg-gray-900 p-6 shadow-lg">
        <h2 className="mb-4 text-lg font-semibold text-gray-100">
          What If You Improve Your Situation?
        </h2>
        <p className="mb-6 text-sm text-gray-400">
          Adjust the factors below to see how improving your situation could
          affect your access to schemes.
        </p>

        <div className="space-y-6">
          {/* Document Completeness Slider */}
          <div>
            <label
              htmlFor="doc-completeness"
              className="mb-2 flex items-center justify-between text-sm font-medium text-gray-300"
            >
              <span>Document Completeness</span>
              <span className="font-mono text-blue-400">
                {documentCompleteness.toFixed(2)}
              </span>
            </label>
            <input
              id="doc-completeness"
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={documentCompleteness}
              onChange={(e) =>
                setDocumentCompleteness(parseFloat(e.target.value))
              }
              className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-gray-700 accent-blue-500"
            />
            <div className="mt-1 flex justify-between text-xs text-gray-500">
              <span>None (0.0)</span>
              <span>Complete (1.0)</span>
            </div>
          </div>

          {/* Digital Access Dropdown */}
          <div>
            <label
              htmlFor="digital-access"
              className="mb-2 block text-sm font-medium text-gray-300"
            >
              Digital Access
            </label>
            <select
              id="digital-access"
              value={digitalAccess}
              onChange={(e) => setDigitalAccess(e.target.value)}
              className="w-full rounded-lg border border-gray-600 bg-gray-800 px-3 py-2 text-sm text-gray-100 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
              <option value="none">None</option>
              <option value="limited">Limited</option>
              <option value="full">Full</option>
            </select>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleSimulate}
              disabled={loading || !hasChanges}
              className="flex-1 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Simulating..." : "Simulate Changes"}
            </button>
            {simulationResult && (
              <button
                onClick={handleReset}
                className="rounded-lg border border-gray-600 bg-gray-800 px-4 py-2.5 text-sm font-medium text-gray-300 transition-colors hover:bg-gray-700"
              >
                Reset
              </button>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="rounded-lg border border-red-800 bg-red-900/30 px-4 py-3 text-sm text-red-300">
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>
      </div>

      {/* View Toggle (only show if simulation exists) */}
      {simulationResult && (
        <div className="flex justify-center gap-2">
          <button
            onClick={() => setViewMode("original")}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              viewMode === "original"
                ? "bg-blue-600 text-white"
                : "bg-gray-800 text-gray-400 hover:bg-gray-700"
            }`}
          >
            Original
          </button>
          <button
            onClick={() => setViewMode("simulated")}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              viewMode === "simulated"
                ? "bg-blue-600 text-white"
                : "bg-gray-800 text-gray-400 hover:bg-gray-700"
            }`}
          >
            Simulated
          </button>
        </div>
      )}

      {/* Comparison View */}
      {simulationResult && (
        <div className="rounded-2xl border border-gray-700 bg-gray-900 p-6 shadow-lg">
          <h2 className="mb-4 text-lg font-semibold text-gray-100">
            {viewMode === "original"
              ? "Original Results"
              : "Simulated Results"}
          </h2>

          <div className="space-y-4">
            {displayRecommendations.map((rec, idx) => {
              // Find matching baseline recommendation
              const baselineRec = baselineRecommendations.find(
                (b) => b.scheme_id === rec.scheme_id
              );

              const accessGapLevel = getAccessGapLevel(rec.access_gap);
              const accessGapInfo = getAccessGapInfo(accessGapLevel);
              const eligibilityLabel = getScoreLabel(rec.eligibility_score);
              const riskLabel = getScoreLabel(rec.risk_score);

              // Calculate changes if in simulated view
              const showChanges = viewMode === "simulated" && baselineRec;
              const eligibilityChange = showChanges
                ? formatScoreChange(
                    baselineRec.eligibility_score,
                    rec.eligibility_score
                  )
                : null;
              const riskChange = showChanges
                ? formatScoreChange(baselineRec.risk_score, rec.risk_score)
                : null;
              const accessGapChange = showChanges
                ? formatScoreChange(baselineRec.access_gap, rec.access_gap)
                : null;

              return (
                <div
                  key={rec.scheme_id}
                  className="rounded-xl border border-gray-700 bg-gray-800 p-5 shadow-md"
                >
                  {/* Header */}
                  <div className="mb-4 flex items-start justify-between gap-3">
                    <h3 className="text-base font-semibold leading-tight text-gray-100">
                      {idx + 1}. {rec.scheme_name}
                    </h3>
                    <span className="shrink-0 rounded-full bg-blue-600/20 px-3 py-1 text-xs font-medium text-blue-400">
                      {rec.eligibility}
                    </span>
                  </div>

                  {/* Access Gap */}
                  <div
                    className={`mb-4 rounded-lg border ${accessGapInfo.borderColor} ${accessGapInfo.bgColor} p-3`}
                  >
                    <div className="flex items-center gap-2">
                      <span className={`text-lg ${accessGapInfo.color}`}>
                        {accessGapInfo.icon}
                      </span>
                      <div className="flex-1">
                        <p
                          className={`text-sm font-semibold ${accessGapInfo.color}`}
                        >
                          {accessGapInfo.level}
                        </p>
                        <div className="mt-0.5 flex items-center gap-2">
                          <p className="text-xs text-gray-400">
                            Gap Score: {rec.access_gap.toFixed(3)}
                          </p>
                          {accessGapChange && (
                            <span
                              className={`text-xs font-medium ${accessGapChange.color}`}
                            >
                              {accessGapChange.formatted}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Scores Grid */}
                  <div className="grid grid-cols-2 gap-4 rounded-lg bg-gray-900/50 p-4">
                    <div>
                      <span className="text-xs text-gray-400">
                        Eligibility
                      </span>
                      <div className="mt-1 flex items-center gap-2">
                        <p className="text-sm font-semibold text-gray-100">
                          {eligibilityLabel}{" "}
                          <span className="font-mono text-xs text-gray-400">
                            ({rec.eligibility_score.toFixed(3)})
                          </span>
                        </p>
                        {eligibilityChange && (
                          <span
                            className={`text-xs font-medium ${eligibilityChange.color}`}
                          >
                            {eligibilityChange.formatted}
                          </span>
                        )}
                      </div>
                    </div>
                    <div>
                      <span className="text-xs text-gray-400">Risk</span>
                      <div className="mt-1 flex items-center gap-2">
                        <p className="text-sm font-semibold text-gray-100">
                          {riskLabel}{" "}
                          <span className="font-mono text-xs text-gray-400">
                            ({rec.risk_score.toFixed(3)})
                          </span>
                        </p>
                        {riskChange && (
                          <span
                            className={`text-xs font-medium ${riskChange.color}`}
                          >
                            {riskChange.formatted}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
