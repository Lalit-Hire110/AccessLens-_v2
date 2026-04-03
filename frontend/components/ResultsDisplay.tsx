"use client";

import { useState } from "react";
import type { PredictionResponse, ExplanationResponse } from "@/lib/api";
import { getAccessGapLevel, getAccessGapInfo, getScoreLabel } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Animated loading messages with rotating effect
// ---------------------------------------------------------------------------

const LOADING_MESSAGES = [
  "Analyzing eligibility...",
  "Evaluating barriers...",
  "Generating insights...",
];

function ExplanationLoader() {
  return (
    <div className="mt-4 space-y-2 border-t border-gray-700 pt-4">
      {LOADING_MESSAGES.map((msg, idx) => (
        <p
          key={msg}
          className="animate-pulse text-xs text-gray-400"
          style={{
            animationDelay: `${idx * 200}ms`,
            animationDuration: "1.5s",
          }}
        >
          {msg}
        </p>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Collapsible explanation section
// ---------------------------------------------------------------------------

function ExplanationSection({ exp }: { exp: ExplanationResponse }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const barriers = exp.barriers?.length ? exp.barriers : null;
  const nextSteps = exp.next_steps?.length ? exp.next_steps : null;

  return (
    <div className="mt-4 border-t border-gray-700 pt-4">
      {/* Summary - Always visible */}
      <div className="mb-3">
        <p className="text-sm leading-relaxed text-gray-300">{exp.summary}</p>
      </div>

      {/* Toggle button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-xs font-medium text-blue-400 transition-colors hover:text-blue-300"
      >
        <span>{isExpanded ? "Hide Details" : "View Details"}</span>
        <span className="transition-transform" style={{ transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)" }}>
          ▼
        </span>
      </button>

      {/* Expanded details */}
      {isExpanded && (
        <div className="mt-4 space-y-4 text-sm text-gray-300">
          {/* Barriers - Enhanced styling */}
          <div>
            <h4 className="mb-1.5 font-semibold text-gray-200">
              Potential Barriers
            </h4>
            {barriers && barriers.length > 0 ? (
              <ul className="space-y-2">
                {barriers.map((b, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="mt-0.5 text-yellow-400">⚠</span>
                    <span className="leading-relaxed">{b}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-green-400">✓ No major barriers identified</p>
            )}
          </div>

          {/* Next steps */}
          {nextSteps && nextSteps.length > 0 && (
            <div>
              <h4 className="mb-1.5 font-semibold text-gray-200">
                Recommended Next Steps
              </h4>
              <ul className="list-decimal space-y-1.5 pl-5">
                {nextSteps.map((s, i) => (
                  <li key={i} className="leading-relaxed">
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface Props {
  data: PredictionResponse;
  explanations: Record<number, ExplanationResponse | null>;
  explanationErrors: Record<number, boolean>;
  explanationsLoading: boolean;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ResultsDisplay({
  data,
  explanations,
  explanationErrors,
  explanationsLoading,
}: Props) {
  const { persona, recommendations } = data;

  return (
    <div className="space-y-6">
      {/* ---- Persona Card ---- */}
      <div className="rounded-2xl border border-gray-700 bg-gray-900 p-6 shadow-lg">
        <h2 className="mb-4 text-lg font-semibold text-gray-100">
          Matched Persona
        </h2>
        <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-3">
          {Object.entries(persona).map(([key, value]) => (
            <div key={key}>
              <span className="font-medium text-gray-400">
                {key.replace(/_/g, " ")}
              </span>
              <p className="text-gray-100">{String(value)}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ---- Recommendations ---- */}
      <div className="rounded-2xl border border-gray-700 bg-gray-900 p-6 shadow-lg">
        <h2 className="mb-4 text-lg font-semibold text-gray-100">
          Recommendations ({recommendations.length})
        </h2>

        {recommendations.length === 0 ? (
          <p className="text-sm text-gray-400">No recommendations found.</p>
        ) : (
          <div className="space-y-4">
            {recommendations.map((rec, idx) => {
              const exp = explanations[idx];
              const hasError = explanationErrors[idx] === true;
              const isLoading =
                explanationsLoading && exp === undefined && !hasError;

              const accessGapInfo = getAccessGapInfo(getAccessGapLevel(rec.access_gap));
              const eligibilityLabel = getScoreLabel(rec.eligibility_score);
              const riskLabel = getScoreLabel(rec.risk_score);

              return (
                <div
                  key={rec.scheme_id}
                  className="rounded-xl border border-gray-700 bg-gray-800 p-5 shadow-md transition-all hover:border-gray-600 hover:shadow-lg"
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

                  {/* Access Gap - PROMINENT */}
                  <div
                    className={`mb-4 rounded-lg border ${accessGapInfo.borderColor} ${accessGapInfo.bgColor} p-3`}
                  >
                    <div className="flex items-center gap-2">
                      <span className={`text-lg ${accessGapInfo.color}`}>
                        {accessGapInfo.icon}
                      </span>
                      <div className="flex-1">
                        <p className={`text-sm font-semibold ${accessGapInfo.color}`}>
                          {accessGapInfo.level}
                        </p>
                        <p className="mt-0.5 text-xs text-gray-400">
                          Gap Score: {rec.access_gap.toFixed(3)}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Scores Grid - With Labels */}
                  <div className="mb-4 grid grid-cols-2 gap-4 rounded-lg bg-gray-900/50 p-4">
                    <div>
                      <span className="text-xs text-gray-400">Eligibility</span>
                      <p className="mt-1 text-sm font-semibold text-gray-100">
                        {eligibilityLabel}{" "}
                        <span className="font-mono text-xs text-gray-400">
                          ({rec.eligibility_score.toFixed(3)})
                        </span>
                      </p>
                    </div>
                    <div>
                      <span className="text-xs text-gray-400">Risk</span>
                      <p className="mt-1 text-sm font-semibold text-gray-100">
                        {riskLabel}{" "}
                        <span className="font-mono text-xs text-gray-400">
                          ({rec.risk_score.toFixed(3)})
                        </span>
                      </p>
                    </div>
                  </div>

                  {/* Insight */}
                  {rec.insight && (
                    <div className="mb-4 rounded-lg bg-blue-500/5 p-3">
                      <p className="text-xs leading-relaxed text-gray-300">
                        💡 {rec.insight}
                      </p>
                    </div>
                  )}

                  {/* Explanation */}
                  {isLoading && <ExplanationLoader />}

                  {hasError && (
                    <div className="mt-4 border-t border-gray-700 pt-4">
                      <p className="mb-1 text-sm font-medium text-yellow-400/90">
                        ⚠ AI Explanation Unavailable
                      </p>
                      <p className="text-xs leading-relaxed text-gray-400">
                        We could not fetch detailed AI insights for this recommendation. The baseline eligibility and risk scores remain fully accurate.
                      </p>
                    </div>
                  )}

                  {exp && <ExplanationSection exp={exp} />}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
