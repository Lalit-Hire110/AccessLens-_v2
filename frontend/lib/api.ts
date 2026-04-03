// ---------------------------------------------------------------------------
// AccessLens v2 — API Client
// ---------------------------------------------------------------------------

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** Timeout (ms) for /explain requests. */
const EXPLAIN_TIMEOUT_MS = 8_000;

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
  top_k?: number;
}

export interface SchemeResult {
  scheme_id: string;
  scheme_name: string;
  eligibility_score: number;
  eligibility: string;
  risk_score: number;
  access_gap: number;
  insight: string | null;
}

export interface PredictionResponse {
  persona: Record<string, unknown>;
  recommendations: SchemeResult[];
}

// ---------------------------------------------------------------------------
// Types — /explain
// ---------------------------------------------------------------------------

export interface ExplanationInput {
  persona_summary: {
    age: number;
    occupation: string;
    income_level: string;
    digital_access: string;
    document_completeness: number | string;
  };
  scheme: { scheme_name: string };
  eligibility: { score: number; label: string };
  risk: { score: number; label: string };
  access_gap: number;
}

export interface ExplanationResponse {
  summary: string;
  eligibility_explanation: string;
  barriers: string[];
  access_gap_explanation: string;
  next_steps: string[];
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

/** Convert a 0-1 numeric score to a lowercase label. */
export function deriveLabel(score: number): string {
  if (score >= 0.7) return "high";
  if (score >= 0.4) return "medium";
  return "low";
}

/** Build a unique cache key for a recommendation. */
function explanationCacheKey(rec: SchemeResult): string {
  return `${rec.scheme_name}|${rec.eligibility_score}|${rec.risk_score}|${rec.access_gap}`;
}

// ---------------------------------------------------------------------------
// Explanation cache (in-memory, lives for the page session)
// ---------------------------------------------------------------------------

const explanationCache = new Map<string, ExplanationResponse>();

export function clearExplanationCache() {
  explanationCache.clear();
}

// ---------------------------------------------------------------------------
// API — /predict
// ---------------------------------------------------------------------------

export async function getPrediction(
  data: UserInput
): Promise<PredictionResponse> {
  const response = await fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API error ${response.status}: ${errorBody}`);
  }

  return response.json();
}

// ---------------------------------------------------------------------------
// API — /explain (single call with timeout + caching)
// ---------------------------------------------------------------------------

export async function getExplanation(
  data: ExplanationInput,
  cacheKey?: string
): Promise<ExplanationResponse> {
  // Return cached result if available
  if (cacheKey && explanationCache.has(cacheKey)) {
    return explanationCache.get(cacheKey)!;
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), EXPLAIN_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_URL}/explain`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
      signal: controller.signal,
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`API error ${response.status}: ${errorBody}`);
    }

    const result: ExplanationResponse = await response.json();

    // Normalise empty arrays
    result.barriers = result.barriers ?? [];
    result.next_steps = result.next_steps ?? [];

    // Cache it
    if (cacheKey) {
      explanationCache.set(cacheKey, result);
    }

    return result;
  } finally {
    clearTimeout(timer);
  }
}

// ---------------------------------------------------------------------------
// Orchestrator — fetch explanations for many recommendations (max concurrency)
// ---------------------------------------------------------------------------

const MAX_PARALLEL = 5;

export interface ExplanationResults {
  /** Keyed by recommendation index. null = still loading (shouldn't happen). */
  data: Record<number, ExplanationResponse | null>;
  errors: Record<number, boolean>;
}

/**
 * Fetch explanations for a list of recommendations with:
 *  - max `MAX_PARALLEL` concurrent requests
 *  - per-request 8 s timeout
 *  - in-memory caching
 */
export async function fetchAllExplanations(
  persona: Record<string, unknown>,
  recommendations: SchemeResult[]
): Promise<ExplanationResults> {
  const data: Record<number, ExplanationResponse | null> = {};
  const errors: Record<number, boolean> = {};

  // Build inputs + cache keys
  const tasks = recommendations.map((rec, idx) => {
    const input: ExplanationInput = {
      persona_summary: {
        age: Number(persona.age ?? 0),
        occupation: String(persona.occupation ?? ""),
        income_level: String(persona.income_level ?? ""),
        digital_access: String(persona.digital_access ?? ""),
        document_completeness: persona.document_completeness as number | string ?? 0,
      },
      scheme: { scheme_name: rec.scheme_name },
      eligibility: {
        score: rec.eligibility_score,
        label: deriveLabel(rec.eligibility_score),
      },
      risk: {
        score: rec.risk_score,
        label: deriveLabel(rec.risk_score),
      },
      access_gap: rec.access_gap,
    };
    return { idx, input, key: explanationCacheKey(rec) };
  });

  // Process in batches of MAX_PARALLEL
  for (let i = 0; i < tasks.length; i += MAX_PARALLEL) {
    const batch = tasks.slice(i, i + MAX_PARALLEL);
    const results = await Promise.allSettled(
      batch.map((t) => getExplanation(t.input, t.key))
    );

    results.forEach((result, batchIdx) => {
      const taskIdx = batch[batchIdx].idx;
      if (result.status === "fulfilled") {
        data[taskIdx] = result.value;
        errors[taskIdx] = false;
      } else {
        data[taskIdx] = null;
        errors[taskIdx] = true;
      }
    });
  }

  return { data, errors };
}

// ---------------------------------------------------------------------------
// API — /simulate
// ---------------------------------------------------------------------------

/**
 * Run what-if simulation by comparing baseline vs modified inputs.
 * 
 * @param request - Simulation request with base input and changes
 * @returns Baseline and simulated results for comparison
 */
export async function simulate(
  request: SimulateRequest
): Promise<SimulateResponse> {
  const response = await fetch(`${API_URL}/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API error ${response.status}: ${errorBody}`);
  }

  return response.json();
}
