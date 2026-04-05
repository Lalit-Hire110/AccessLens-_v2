"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import dynamic from "next/dynamic";
import { motion, AnimatePresence } from "framer-motion";
import { useAppStore } from "@/lib/store";
import { getAccessGapLevel, getAccessGapInfo } from "@/lib/utils";
import WhatIfSimulator from "@/components/WhatIfSimulator";
import { getExplanation } from "@/lib/api";
import type { ExplanationResponse, SchemeResult } from "@/lib/api";
import {
  pageContainer,
  staggerContainer,
  fadeUp,
  fadeIn,
  expandPanel,
  slideInLeft,
  scalePop,
  hoverLift,
  hoverButton,
  hoverSubtle,
} from "@/lib/motion";

const SchemeComparisonChart = dynamic(
  () => import("@/components/visualizations/SchemeComparisonChart"),
  {
    ssr: false,
    loading: () => (
      <div className="space-y-3">
        <div className="skeleton-line h-4 w-1/3" />
        <div className="skeleton h-56 rounded-xl" />
      </div>
    ),
  }
);

interface ExplainState {
  data: ExplanationResponse | null;
  loading: boolean;
  error: string | null;
}

// ── Skeleton card — shown while results load ─────────────────────────────────

function SkeletonCard() {
  return (
    <div className="card p-6 space-y-4">
      {/* name */}
      <div className="flex items-start justify-between gap-3">
        <div className="skeleton-line h-5 w-2/3 rounded" />
        <div className="skeleton-line h-6 w-16 rounded-full" />
      </div>
      {/* access gap */}
      <div className="skeleton-line h-14 rounded-xl" />
      {/* bars */}
      <div className="card-elevated p-4 space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="space-y-1.5">
            <div className="flex justify-between">
              <div className="skeleton-line h-3 w-24 rounded" />
              <div className="skeleton-line h-3 w-10 rounded" />
            </div>
            <div className="skeleton-line h-1.5 rounded-full" />
          </div>
        ))}
      </div>
      {/* actions */}
      <div className="flex gap-2 pt-2">
        <div className="skeleton-line h-8 w-32 rounded-xl" />
        <div className="skeleton-line h-8 w-24 rounded-lg" />
      </div>
    </div>
  );
}

// ── Empty state ──────────────────────────────────────────────────────────────

function EmptyState({ icon, title, body }: { icon: string; title: string; body: string }) {
  return (
    <motion.div
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      className="flex flex-col items-center justify-center py-12 text-center gap-3"
    >
      <span className="text-4xl">{icon}</span>
      <p className="text-sm font-semibold text-content-secondary">{title}</p>
      <p className="text-xs text-content-muted max-w-xs">{body}</p>
    </motion.div>
  );
}

// ── Animated progress bar ────────────────────────────────────────────────────

function ProgressBar({
  value,
  label,
  color,
}: {
  value: number;
  label: string;
  color: string;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs text-content-muted">{label}</span>
        <span className="text-xs font-mono font-semibold text-content-secondary">
          {value.toFixed(3)}
        </span>
      </div>
      <div
        className="h-1.5 rounded-full overflow-hidden"
        style={{ background: "var(--border-subtle)" }}
      >
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value * 100}%` }}
          transition={{ duration: 0.9, ease: "easeOut", delay: 0.15 }}
          className={`h-full rounded-full ${color}`}
        />
      </div>
    </div>
  );
}

// ── Explanation panel ────────────────────────────────────────────────────────

function ExplanationPanel({ exp }: { exp: ExplanationResponse }) {
  const [open, setOpen] = useState(false);

  return (
    <motion.div
      variants={expandPanel}
      initial="hidden"
      animate="visible"
      exit="exit"
      className="mt-3 overflow-hidden"
    >
      {/* Summary always visible */}
      <p className="text-sm leading-relaxed text-content-secondary">{exp.summary}</p>

      <motion.button
        {...hoverSubtle}
        onClick={() => setOpen(!open)}
        className="mt-2 flex items-center gap-1.5 text-xs font-medium text-brand-soft hover:text-brand transition-colors"
      >
        {open ? "Hide Details" : "View Details"}
        <motion.span
          animate={{ rotate: open ? 180 : 0 }}
          transition={{ duration: 0.25 }}
          className="inline-block"
        >
          ▼
        </motion.span>
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            variants={expandPanel}
            initial="hidden"
            animate="visible"
            exit="exit"
            className="mt-4 space-y-4 text-sm text-content-secondary overflow-hidden"
          >
            {[
              { label: "Eligibility", text: exp.eligibility_explanation },
              { label: "Risk", text: exp.risk_explanation },
              { label: "Access Gap", text: exp.access_gap_explanation },
            ].map((item, i) => (
              <motion.div
                key={item.label}
                variants={slideInLeft}
                initial="hidden"
                animate="visible"
                transition={{ delay: i * 0.08 }}
              >
                <p className="font-semibold text-content-primary mb-1">{item.label}</p>
                <p className="leading-relaxed">{item.text}</p>
              </motion.div>
            ))}

            {exp.key_barriers.length > 0 && (
              <motion.div
                variants={slideInLeft}
                initial="hidden"
                animate="visible"
                transition={{ delay: 0.24 }}
              >
                <p className="font-semibold text-content-primary mb-2">Key Barriers</p>
                <ul className="space-y-1.5">
                  {exp.key_barriers.map((b, i) => (
                    <motion.li
                      key={i}
                      variants={slideInLeft}
                      initial="hidden"
                      animate="visible"
                      transition={{ delay: 0.28 + i * 0.06 }}
                      className="flex gap-2"
                    >
                      <span className="text-warning shrink-0">⚠</span>
                      {b}
                    </motion.li>
                  ))}
                </ul>
              </motion.div>
            )}

            {exp.improvement_suggestions.length > 0 && (
              <motion.div
                variants={slideInLeft}
                initial="hidden"
                animate="visible"
                transition={{ delay: 0.32 }}
              >
                <p className="font-semibold text-content-primary mb-2">
                  Suggested Improvements
                </p>
                <ol className="list-decimal pl-5 space-y-1.5">
                  {exp.improvement_suggestions.map((s, i) => (
                    <motion.li
                      key={i}
                      variants={slideInLeft}
                      initial="hidden"
                      animate="visible"
                      transition={{ delay: 0.36 + i * 0.06 }}
                    >
                      {s}
                    </motion.li>
                  ))}
                </ol>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ── Per-scheme explain trigger ───────────────────────────────────────────────

function SchemeExplainSection({ rec }: { rec: SchemeResult }) {
  const [state, setState] = useState<ExplainState>({
    data: null,
    loading: false,
    error: null,
  });

  async function handleExplain() {
    if (state.data) {
      setState({ data: null, loading: false, error: null });
      return;
    }
    setState({ data: null, loading: true, error: null });
    try {
      const data = await getExplanation(rec);
      setState({ data, loading: false, error: null });
    } catch (err) {
      setState({
        data: null,
        loading: false,
        error: err instanceof Error ? err.message : "Failed",
      });
    }
  }

  return (
    <div
      className="mt-4 pt-4"
      style={{ borderTop: "1px solid var(--border-subtle)" }}
    >
      <motion.button
        {...hoverButton}
        onClick={handleExplain}
        disabled={state.loading}
        className="btn btn-secondary text-xs disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {state.loading ? (
          <span className="flex items-center gap-2">
            <svg className="h-3 w-3 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
              />
            </svg>
            Loading…
          </span>
        ) : state.data ? (
          "Hide AI Explanation"
        ) : (
          "🤖 View AI Explanation"
        )}
      </motion.button>

      {/* Empty prompt — shown before first click */}
      {!state.data && !state.loading && !state.error && (
        <p className="mt-2 text-xs text-content-muted">
          Click to generate an AI explanation for this scheme.
        </p>
      )}

      <AnimatePresence>
        {state.error && (
          <motion.p
            variants={fadeIn}
            initial="hidden"
            animate="visible"
            exit="exit"
            className="mt-2 text-xs text-warning"
          >
            ⚠ {state.error}
          </motion.p>
        )}
        {state.data && <ExplanationPanel exp={state.data} />}
      </AnimatePresence>
    </div>
  );
}

// ── Apply button ─────────────────────────────────────────────────────────────

function ApplyButton({ rec }: { rec: SchemeResult }) {
  const applyLink =
    rec.apply_link ||
    `https://www.google.com/search?q=${encodeURIComponent(rec.scheme_name)}`;
  const isOfficial = !!rec.apply_link;

  return (
    <div
      className="mt-4 pt-4"
      style={{ borderTop: "1px solid var(--border-subtle)" }}
    >
      <motion.a
        {...hoverButton}
        href={applyLink}
        target="_blank"
        rel="noopener noreferrer"
        title={
          isOfficial
            ? "Open official application page"
            : "Opens Google search results"
        }
        className="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-medium transition-colors badge-success"
      >
        Apply Now
        <motion.span
          animate={{ x: [0, 3, 0] }}
          transition={{ repeat: Infinity, duration: 1.6 }}
        >
          →
        </motion.span>
        {!isOfficial && <span title="Opens search results">🔍</span>}
      </motion.a>
      {!isOfficial && (
        <p className="mt-1.5 text-xs text-content-muted">
          Official link unavailable — search results will open
        </p>
      )}
    </div>
  );
}

// ── Scheme card ──────────────────────────────────────────────────────────────

function SchemeCard({ rec, idx }: { rec: SchemeResult; idx: number }) {
  const gapLevel = getAccessGapLevel(rec.access_gap);
  const gapInfo = getAccessGapInfo(gapLevel);

  // Access gap badge color map — semantic, not decorative
  const gapBadgeClass =
    gapLevel === "low"
      ? "badge-success"
      : gapLevel === "moderate"
      ? "badge-warning"
      : "badge-danger";

  const gapIcon =
    gapLevel === "low" ? "✓" : gapLevel === "moderate" ? "⚠" : "⚠";

  return (
    <motion.div
      variants={fadeUp}
      {...hoverLift}
      className="card card-hover p-6 group"
    >
      {/* ── 1. Scheme name + eligibility badge ── */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <h3 className="text-base font-semibold text-content-primary leading-snug group-hover:text-white transition-colors">
          {idx + 1}. {rec.scheme_name}
        </h3>
        <motion.span
          variants={scalePop}
          initial="hidden"
          animate="visible"
          className="badge badge-primary shrink-0"
        >
          {rec.eligibility}
        </motion.span>
      </div>

      {/* ── 2. Access Gap — dominant, immediately visible ── */}
      <motion.div
        variants={fadeUp}
        className={`mb-5 rounded-xl border ${gapInfo.borderColor} ${gapInfo.bgColor} px-4 py-3`}
      >
        <div className="flex items-center gap-3">
          {/* Large icon */}
          <span
            className={`text-2xl font-bold leading-none ${gapInfo.color}`}
            aria-hidden="true"
          >
            {gapIcon}
          </span>
          <div className="flex-1 min-w-0">
            {/* Level label — large, prominent */}
            <p className={`text-base font-bold ${gapInfo.color}`}>
              {gapInfo.level}
            </p>
            {/* Score — secondary, smaller */}
            <p className="text-xs text-content-muted mt-0.5">
              Gap score:{" "}
              <span className="font-mono">{rec.access_gap.toFixed(3)}</span>
            </p>
          </div>
          {/* Score pill — right-aligned */}
          <span className={`badge ${gapBadgeClass} shrink-0 text-xs`}>
            {(rec.access_gap * 100).toFixed(0)}%
          </span>
        </div>
      </motion.div>

      {/* ── 3. Progress bars ── */}
      <div className="mb-5 space-y-3 rounded-xl p-4 card-elevated">
        <ProgressBar
          value={rec.eligibility_score}
          label="Eligibility"
          color="bg-success"
        />
        <ProgressBar
          value={rec.risk_score}
          label="Risk"
          color="bg-warning"
        />
        <ProgressBar
          value={rec.access_gap}
          label="Access Gap"
          color="bg-danger"
        />
      </div>

      {/* ── 4. Insight (secondary, smaller) ── */}
      {rec.insight && (
        <div
          className="mb-4 rounded-lg p-3"
          style={{
            background: "rgba(59,130,246,0.05)",
            border: "1px solid rgba(59,130,246,0.1)",
          }}
        >
          <p className="text-xs leading-relaxed text-content-secondary">
            💡 {rec.insight}
          </p>
        </div>
      )}

      {/* ── 5. Actions ── */}
      <SchemeExplainSection rec={rec} />
      <ApplyButton rec={rec} />
    </motion.div>
  );
}

// ── Main page ────────────────────────────────────────────────────────────────

export default function ResultsPage() {
  const router = useRouter();
  const { result, userInput } = useAppStore();
  const [activeSection, setActiveSection] = useState<"whatif" | "viz" | null>(null);
  // Progressive rendering: show skeleton briefly while page mounts
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!result) {
      router.replace("/input");
      return;
    }
    // Small delay so cards animate in after page paint
    const t = setTimeout(() => setReady(true), 80);
    return () => clearTimeout(t);
  }, [result, router]);

  if (!result) return null;

  const { persona, recommendations } = result;

  return (
    <motion.main
      initial="hidden"
      animate="visible"
      variants={pageContainer}
      className="mx-auto w-full max-w-4xl flex-1 px-4 py-10 space-y-8"
    >
      {/* Header */}
      <motion.div
        variants={fadeUp}
        className="flex items-start justify-between gap-4"
      >
        <div>
          <h1 className="text-3xl font-bold text-content-primary">
            Your Recommendations
          </h1>
          <p className="mt-2 text-sm text-content-secondary">
            {recommendations.length} scheme
            {recommendations.length !== 1 ? "s" : ""} matched to your profile
          </p>
        </div>
        <motion.div {...hoverButton}>
          <Link href="/input" className="btn btn-secondary text-xs">
            ← Edit Profile
          </Link>
        </motion.div>
      </motion.div>

      {/* Persona Card */}
      <motion.div variants={fadeUp} className="card p-6">
        <p className="mb-4 text-sm font-semibold text-content-primary">
          Matched Persona
        </p>
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm sm:grid-cols-3"
        >
          {Object.entries(persona).map(([key, value]) => (
            <motion.div key={key} variants={slideInLeft}>
              <span className="text-xs text-content-muted capitalize">
                {key.replace(/_/g, " ")}
              </span>
              <p className="text-content-primary font-medium">{String(value)}</p>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>

      {/* Scheme Cards — skeleton until ready, then progressive stagger */}
      {!ready ? (
        <div className="space-y-5">
          {Array.from({ length: Math.min(recommendations.length || 3, 3) }).map(
            (_, i) => (
              <SkeletonCard key={i} />
            )
          )}
        </div>
      ) : recommendations.length === 0 ? (
        <div className="card p-6">
          <EmptyState
            icon="🔍"
            title="No matching schemes found"
            body="Try adjusting your profile details — different income level, occupation, or location may surface relevant schemes."
          />
        </div>
      ) : (
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="space-y-5"
        >
          {recommendations.map((rec, idx) => (
            <SchemeCard key={rec.scheme_id} rec={rec} idx={idx} />
          ))}
        </motion.div>
      )}

      {/* Action Buttons */}
      <motion.div variants={fadeUp} className="card p-6 space-y-4">
        <p className="text-sm font-semibold text-content-primary">
          Explore Further
        </p>
        <div className="flex flex-wrap gap-3">
          {(
            [
              { key: "whatif" as const, label: "🔮 Run What-If Simulation" },
              { key: "viz" as const, label: "📊 View Visualizations" },
            ] as const
          ).map(({ key, label }) => (
            <motion.button
              key={key}
              {...hoverButton}
              onClick={() =>
                setActiveSection(activeSection === key ? null : key)
              }
              className={`btn transition-all ${
                activeSection === key
                  ? "btn-primary glow-primary"
                  : "btn-secondary"
              }`}
            >
              {label}
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* What-If Panel */}
      <AnimatePresence>
        {activeSection === "whatif" && userInput && (
          <motion.div
            variants={expandPanel}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <WhatIfSimulator
              baseInput={userInput}
              baselineRecommendations={recommendations}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Visual Insights Panel */}
      <AnimatePresence>
        {activeSection === "viz" && (
          <motion.div
            variants={expandPanel}
            initial="hidden"
            animate="visible"
            exit="exit"
            className="card p-6 space-y-4"
          >
            <div>
              <h2 className="text-xl font-semibold text-content-primary">
                Visual Insights
              </h2>
              <p className="mt-1 text-xs text-content-muted">
                Side-by-side score breakdown for all matched schemes
              </p>
            </div>
            <div className="section-divider" />
            {recommendations.length < 2 ? (
              <EmptyState
                icon="📊"
                title="Not enough data to display insights"
                body="Visual comparisons require at least 2 matched schemes."
              />
            ) : (
              <SchemeComparisonChart recommendations={recommendations} />
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.main>
  );
}
