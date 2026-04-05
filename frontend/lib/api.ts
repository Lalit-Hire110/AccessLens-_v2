// ---------------------------------------------------------------------------
// AccessLens v2 — API Client
// ---------------------------------------------------------------------------

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const PREDICT_TIMEOUT_MS  = 15_000;
const EXPLAIN_TIMEOUT_MS  =  8_000;
const SIMULATE_TIMEOUT_MS = 15_000;

// ---------------------------------------------------------------------------
// Types — /predict
// ---------------------------------------------------------------------------

export interface UserInput {
  age: number;
  gender: string;
  rural_urban: string;
  income_level: string;
  occupation: string;
  education_level: string;
  digital_access: string;
  document_completeness: number | string;
  institutional_dependency: string;
}

export interface ExplanationFactor {
  factor: string;
  value: string | number;
  threshold?: string | number;
}

export interface SchemeResult {
  scheme_id: string;
  scheme_name: string;
  eligibility_score: number;
  eligibility: string;
  risk_score: number;
  access_gap: number;
  insight: string | null;
  apply_link?: string | null;
  eligibility_factors?: ExplanationFactor[];
  risk_factors?: ExplanationFactor[];
  input_snapshot?: Record<string, unknown>;
}

export interface PredictionResponse {
  persona: Record<string, unknown>;
  recommendations: SchemeResult[];
}

// ---------------------------------------------------------------------------
// Types — /explain
// ---------------------------------------------------------------------------

export interface ExplanationInput {
  scheme_name: string;
  eligibility_score: number;
  risk_score: number;
  access_gap: number;
  eligibility_factors: ExplanationFactor[];
  risk_factors: ExplanationFactor[];
  input_snapshot: Record<string, unknown>;
}

export interface ExplanationResponse {
  summary: string;
  eligibility_explanation: string;
  risk_explanation: string;
  access_gap_explanation: string;
  key_barriers: string[];
  improvement_suggestions: string[];
}

// ---------------------------------------------------------------------------
// Types — /simulate
// ---------------------------------------------------------------------------

export interface SimulationChanges {
  document_completeness?: number;
  digital_access?: string;
}

export interface SimulateRequest {
  base_input: UserInput;
  changes: SimulationChanges;
}

export interface SimulateResponse {
  baseline: PredictionResponse;
  simulated: PredictionResponse;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

export function deriveLabel(score: number): string {
  if (score >= 0.7) return "high";
  if (score >= 0.4) return "medium";
  return "low";
}

export function buildExplanationInput(rec: SchemeResult): ExplanationInput {
  return {
    scheme_name: rec.scheme_name,
    eligibility_score: rec.eligibility_score,
    risk_score: rec.risk_score,
    access_gap: rec.access_gap,
    eligibility_factors: rec.eligibility_factors ?? [],
    risk_factors: rec.risk_factors ?? [],
    input_snapshot: rec.input_snapshot ?? {},
  };
}

// ---------------------------------------------------------------------------
// Internal fetch wrapper — timeout + 1 retry
// ---------------------------------------------------------------------------

async function fetchWithRetry(
  url: string,
  options: RequestInit,
  timeoutMs: number,
  retries = 1
): Promise<Response> {
  for (let attempt = 0; attempt <= retries; attempt++) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const res = await fetch(url, { ...options, signal: controller.signal });
      clearTimeout(timer);
      return res;
    } catch (err) {
      clearTimeout(timer);
      const isLast = attempt === retries;
      if (isLast) throw err;
      // Brief pause before retry
      await new Promise((r) => setTimeout(r, 400));
    }
  }
  // Unreachable — TypeScript needs this
  throw new Error("fetchWithRetry exhausted");
}

/** Parse a failed response into a human-readable message. */
async function parseErrorMessage(res: Response): Promise<string> {
  try {
    const text = await res.text();
    // Try to extract FastAPI detail field
    const json = JSON.parse(text);
    if (json?.detail) return String(json.detail);
    return text || `Server error ${res.status}`;
  } catch {
    return `Server error ${res.status}`;
  }
}

// ---------------------------------------------------------------------------
// Explanation cache (in-memory, session-scoped)
// ---------------------------------------------------------------------------

const explanationCache = new Map<string, ExplanationResponse>();

export function clearExplanationCache() {
  explanationCache.clear();
}

function explanationCacheKey(rec: SchemeResult): string {
  return `${rec.scheme_name}|${rec.eligibility_score}|${rec.risk_score}|${rec.access_gap}`;
}

// ---------------------------------------------------------------------------
// API — /predict
// ---------------------------------------------------------------------------

export async function getPrediction(data: UserInput): Promise<PredictionResponse> {
  let res: Response;
  try {
    res = await fetchWithRetry(
      `${API_URL}/predict`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      },
      PREDICT_TIMEOUT_MS
    );
  } catch (err) {
    const msg = err instanceof Error && err.name === "AbortError"
      ? "Request timed out. Please try again."
      : "Unable to reach the server. Check your connection.";
    if (process.env.NODE_ENV !== "production") console.error("[/predict]", err);
    throw new Error(msg);
  }

  if (!res.ok) {
    const msg = await parseErrorMessage(res);
    if (process.env.NODE_ENV !== "production") console.error("[/predict]", res.status, msg);
    throw new Error(msg);
  }

  return res.json();
}

// ---------------------------------------------------------------------------
// API — /explain  (on-demand, button-triggered, cached)
// ---------------------------------------------------------------------------

export async function getExplanation(
  rec: SchemeResult,
  cacheKey?: string
): Promise<ExplanationResponse> {
  const key = cacheKey ?? explanationCacheKey(rec);
  if (explanationCache.has(key)) return explanationCache.get(key)!;

  const payload = buildExplanationInput(rec);

  let res: Response;
  try {
    res = await fetchWithRetry(
      `${API_URL}/explain`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      EXPLAIN_TIMEOUT_MS
    );
  } catch (err) {
    const msg = err instanceof Error && err.name === "AbortError"
      ? "Explanation timed out. Please try again."
      : "Unable to reach the server.";
    if (process.env.NODE_ENV !== "production") console.error("[/explain]", err);
    throw new Error(msg);
  }

  if (!res.ok) {
    const msg = await parseErrorMessage(res);
    if (process.env.NODE_ENV !== "production") console.error("[/explain]", res.status, msg);
    throw new Error(msg);
  }

  const result: ExplanationResponse = await res.json();
  result.key_barriers = result.key_barriers ?? [];
  result.improvement_suggestions = result.improvement_suggestions ?? [];

  explanationCache.set(key, result);
  return result;
}

// ---------------------------------------------------------------------------
// API — /simulate
// ---------------------------------------------------------------------------

export async function simulate(request: SimulateRequest): Promise<SimulateResponse> {
  let res: Response;
  try {
    res = await fetchWithRetry(
      `${API_URL}/simulate`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      },
      SIMULATE_TIMEOUT_MS
    );
  } catch (err) {
    const msg = err instanceof Error && err.name === "AbortError"
      ? "Simulation timed out. Please try again."
      : "Unable to reach the server.";
    if (process.env.NODE_ENV !== "production") console.error("[/simulate]", err);
    throw new Error(msg);
  }

  if (!res.ok) {
    const msg = await parseErrorMessage(res);
    if (process.env.NODE_ENV !== "production") console.error("[/simulate]", res.status, msg);
    throw new Error(msg);
  }

  return res.json();
}
