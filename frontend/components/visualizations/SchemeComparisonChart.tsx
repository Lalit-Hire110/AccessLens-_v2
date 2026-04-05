"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SchemeData {
  scheme_name: string;
  eligibility_score: number;
  risk_score: number;
  access_gap: number;
}

interface Props {
  recommendations: SchemeData[];
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Shorten long scheme names for the X-axis */
function shortenName(name: string, max = 18): string {
  return name.length > max ? name.slice(0, max - 1) + "…" : name;
}

// ---------------------------------------------------------------------------
// Custom tooltip
// ---------------------------------------------------------------------------

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;

  return (
    <div className="rounded-xl border border-border-subtle bg-surface-card px-4 py-3 shadow-xl text-xs space-y-1.5">
      <p className="font-semibold text-content-primary mb-2">{label}</p>
      {payload.map((entry) => (
        <div key={entry.name} className="flex items-center justify-between gap-6">
          <span className="flex items-center gap-1.5">
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-content-secondary capitalize">
              {entry.name.replace(/_/g, " ")}
            </span>
          </span>
          <span className="font-mono font-semibold text-content-primary">
            {entry.value.toFixed(3)}
          </span>
        </div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function SchemeComparisonChart({ recommendations }: Props) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <p className="text-sm text-gray-400 py-4">No data available</p>
    );
  }

  const data = recommendations.map((r) => ({
    name: shortenName(r.scheme_name),
    full_name: r.scheme_name,
    eligibility_score: r.eligibility_score,
    risk_score: r.risk_score,
    access_gap: r.access_gap,
  }));

  return (
    <div className="space-y-6">
      {/* Bar chart */}
      <div className="rounded-2xl border border-border-subtle bg-surface-card p-5">
        <p className="mb-1 text-sm font-semibold text-content-primary">
          Score Comparison
        </p>
        <p className="mb-5 text-xs text-content-muted">
          Eligibility, risk, and access gap across all matched schemes
        </p>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart
            data={data}
            margin={{ top: 4, right: 8, left: -16, bottom: 4 }}
            barCategoryGap="28%"
            barGap={3}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" vertical={false} />
            <XAxis dataKey="name" tick={{ fill: "#475569", fontSize: 11 }} axisLine={{ stroke: "#2d2d3d" }} tickLine={false} />
            <YAxis domain={[0, 1]} tick={{ fill: "#475569", fontSize: 11 }} axisLine={false} tickLine={false} tickCount={6} />
            <Tooltip
              content={<CustomTooltip />}
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: "#475569", paddingTop: 16 }}
              formatter={(value: string) =>
                value.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase())
              }
            />
            <Bar dataKey="eligibility_score" fill="#22c55e" radius={[4, 4, 0, 0]} maxBarSize={40} />
            <Bar dataKey="risk_score"        fill="#f59e0b" radius={[4, 4, 0, 0]} maxBarSize={40} />
            <Bar dataKey="access_gap"        fill="#ef4444" radius={[4, 4, 0, 0]} maxBarSize={40} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Score legend / key */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Eligibility Score", color: "bg-success", desc: "Higher = better match" },
          { label: "Risk Score",        color: "bg-warning", desc: "Higher = more risk" },
          { label: "Access Gap",        color: "bg-danger",  desc: "Higher = harder to access" },
        ].map((item) => (
          <div
            key={item.label}
            className="rounded-xl border border-border-subtle bg-surface-card p-3 space-y-1"
          >
            <div className="flex items-center gap-2">
              <span className={`h-2.5 w-2.5 rounded-full ${item.color}`} />
              <span className="text-xs font-medium text-content-primary">{item.label}</span>
            </div>
            <p className="text-xs text-content-muted">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
