# Access Risk Model v1 — Model Specification

## Overview

Access Risk Model v1 computes a **normalized Access Risk Score ∈ [0, 1]** for a given
(scheme, persona) pair.

| Score | Interpretation |
|-------|----------------|
| 0.0   | Minimal access friction |
| 0.5   | Moderate friction |
| 1.0   | Very high access friction |

This score represents **relative access difficulty**, not eligibility or approval probability.
The model is fully deterministic — no ML, no randomness.

---

## Input Data

| File | Key Fields Used |
|------|----------------|
| `schemes_v0.csv`  | `application_mode`, `documents_requiered_count`, `digital_only`, `assisted_access_available`, `source_confidence` |
| `barriers_v0.csv` | `barrier_id`, `barrier_type`, `affected_stage`, `default_severity` |
| `personas_v0.csv` | `literacy_level`, `digital_access`, `document_completeness`, `institutional_dependency` |

---

## Step 1 — Scheme → Barrier Activation

Each barrier type receives an **activation level label** derived from scheme attributes.

### Activation Multiplier Map

| Label    | Multiplier |
|----------|-----------|
| high     | 1.0       |
| medium   | 0.7       |
| low      | 0.4       |
| reduced  | 0.3       |
| none     | 0.0       |

### Activation Rules (evaluated in order)

| Condition | Barrier Type | Activation Level |
|-----------|-------------|-----------------|
| `digital_only == 1` | digital | high |
| `application_mode == "online"` | digital | medium |
| `application_mode == "hybrid"` | digital | low |
| `documents_requiered_count >= 4` | documentation | high |
| `assisted_access_available == 1` | institutional | reduced |
| `source_confidence == "medium"` | awareness | low |
| (default) | any | none |

---

## Step 2 — Persona → Barrier Amplification

Each barrier type receives a persona-specific **amplification factor**.

| Barrier Type | Persona Feature | low | medium | high |
|--------------|----------------|-----|--------|------|
| awareness | `literacy_level` | 1.3 | 1.1 | 1.0 |
| digital | `digital_access` | 1.4 | 1.2 | 1.0 |
| documentation | `document_completeness` | 1.4 | 1.2 | 1.0 |
| institutional | `institutional_dependency` | 1.0 | 1.1 | 1.3 |

---

## Step 3 — Barrier Contribution

```
Barrier Contribution = default_severity × activation_multiplier × amplification_factor
```

- If activation label is `none`, contribution = **0.0** (barrier skipped).

---

## Step 4 — Aggregation and Normalization

```
Raw Risk Score           = Σ(barrier contributions)
Maximum Possible Score   = Σ(default_severity × 1.0 × 1.4)   [over all barriers]
Normalized Access Risk   = Raw Risk Score / Maximum Possible Score
```

The **Maximum Possible Score** represents the theoretical worst case: every barrier
fully activated (multiplier = 1.0) with maximum amplification (1.4).

---

## Checker Section

The script always prints a structured CHECKER block at the end of each run containing:

1. Activated barriers (non-zero contribution) with breakdown
2. Skipped barriers (zero activation)
3. Maximum Possible Score used for normalization
4. Sanity check — confirms the final score is in [0, 1]
5. Dominant barrier type analysis

This section is designed to be shared with reviewers for validation.
