"""
AccessLens v2 — Access Risk Model v1
=====================================
Computes a normalized Access Risk Score in [0, 1] for a given scheme and persona.

Score interpretation:
  0.0 = minimal access friction
  1.0 = very high access friction

This is NOT a prediction model. It is a deterministic policy-access friction simulator.
"""

import os
import pandas as pd

# ---------------------------------------------------------------------------
# PATHS  (all relative to this script's location so it stays portable)
# ---------------------------------------------------------------------------

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_ROOT  = os.path.join(_SCRIPT_DIR, "..", "data")

SCHEMES_CSV  = os.path.join(_DATA_ROOT, "schemes",  "schemes_v0.csv")
BARRIERS_CSV = os.path.join(_DATA_ROOT, "barriers", "barriers_v0.csv")
PERSONAS_CSV = os.path.join(_DATA_ROOT, "personas", "personas_v0.csv")

# ---------------------------------------------------------------------------
# ACTIVATION MULTIPLIER MAP  (Step 1)
# ---------------------------------------------------------------------------

ACTIVATION_MULTIPLIER = {
    "high":    1.0,
    "medium":  0.7,
    "low":     0.4,
    "reduced": 0.3,
    "none":    0.0,
}

# ---------------------------------------------------------------------------
# PERSONA AMPLIFICATION MAPS  (Step 2)
# ---------------------------------------------------------------------------

AWARENESS_AMPLIFICATION = {
    "low":    1.3,
    "medium": 1.1,
    "high":   1.0,
}

DIGITAL_AMPLIFICATION = {
    "low":    1.4,
    "medium": 1.2,
    "high":   1.0,
}

DOCUMENTATION_AMPLIFICATION = {
    "low":    1.4,
    "medium": 1.2,
    "high":   1.0,
}

INSTITUTIONAL_AMPLIFICATION = {
    "high":   1.3,
    "medium": 1.1,
    "low":    1.0,
}

# ---------------------------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------------------------

def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load schemes, barriers, and personas CSVs. Strip whitespace from all string columns."""
    schemes  = pd.read_csv(SCHEMES_CSV)
    barriers = pd.read_csv(BARRIERS_CSV)
    personas = pd.read_csv(PERSONAS_CSV)

    # Normalise string columns to lowercase, strip whitespace
    for df in (schemes, barriers, personas):
        str_cols = df.select_dtypes(include="object").columns
        df[str_cols] = df[str_cols].apply(lambda col: col.str.strip().str.lower())

    return schemes, barriers, personas


# ---------------------------------------------------------------------------
# STEP 1 — SCHEME → BARRIER ACTIVATION LEVELS
# ---------------------------------------------------------------------------

def compute_activation_levels(scheme_row: pd.Series) -> dict[str, str]:
    """
    Given a single scheme row, derive activation level (label) for each barrier type.

    Returns a dict: { barrier_type: activation_label }
    """
    activation = {
        "awareness":     "none",
        "documentation": "none",
        "digital":       "none",
        "institutional": "none",
    }

    # --- digital ---
    digital_only = int(scheme_row.get("digital_only", 0) or 0)
    app_mode     = str(scheme_row.get("application_mode", "") or "").strip().lower()

    if digital_only == 1:
        activation["digital"] = "high"
    elif app_mode == "online":
        activation["digital"] = "medium"
    elif app_mode == "hybrid":
        activation["digital"] = "low"

    # --- documentation ---
    doc_count_raw = scheme_row.get("documents_requiered_count", None)
    if pd.notna(doc_count_raw) and doc_count_raw != "":
        try:
            if int(doc_count_raw) >= 4:
                activation["documentation"] = "high"
        except (ValueError, TypeError):
            pass

    # --- institutional ---
    assisted_raw = scheme_row.get("assisted_access_available", 0)
    try:
        assisted = int(assisted_raw) if pd.notna(assisted_raw) else 0
    except (ValueError, TypeError):
        assisted = 0

    if assisted == 1:
        activation["institutional"] = "reduced"

    # --- awareness ---
    src_confidence = str(scheme_row.get("source_confidence", "") or "").strip().lower()
    if src_confidence == "medium":
        activation["awareness"] = "low"

    return activation


# ---------------------------------------------------------------------------
# STEP 2 — PERSONA → BARRIER AMPLIFICATION FACTORS
# ---------------------------------------------------------------------------

def compute_amplification_factors(persona_row: pd.Series) -> dict[str, float]:
    """
    Given a single persona row, derive amplification factor for each barrier type.

    Returns a dict: { barrier_type: amplification_factor }
    """
    literacy        = str(persona_row.get("literacy_level",          "high")).strip().lower()
    digital_access  = str(persona_row.get("digital_access",          "high")).strip().lower()
    doc_completeness = str(persona_row.get("document_completeness",  "high")).strip().lower()
    inst_dependency  = str(persona_row.get("institutional_dependency","low" )).strip().lower()

    return {
        "awareness":     AWARENESS_AMPLIFICATION.get(literacy,         1.0),
        "digital":       DIGITAL_AMPLIFICATION.get(digital_access,     1.0),
        "documentation": DOCUMENTATION_AMPLIFICATION.get(doc_completeness, 1.0),
        "institutional": INSTITUTIONAL_AMPLIFICATION.get(inst_dependency,  1.0),
    }


# ---------------------------------------------------------------------------
# STEP 3 — BARRIER CONTRIBUTION
# ---------------------------------------------------------------------------

def compute_barrier_contribution(
    barrier_row: pd.Series,
    activation_label: str,
    amplification_factor: float,
) -> float:
    """
    Barrier Contribution = default_severity × activation_multiplier × amplification_factor.
    Returns 0.0 if activation_label == 'none'.
    """
    if activation_label == "none":
        return 0.0

    severity     = float(barrier_row["default_severity"])
    act_mult     = ACTIVATION_MULTIPLIER[activation_label]
    return severity * act_mult * amplification_factor


# ---------------------------------------------------------------------------
# STEP 4 — RAW SCORE + NORMALISATION
# ---------------------------------------------------------------------------

def compute_maximum_possible_score(barriers: pd.DataFrame) -> float:
    """
    Maximum Possible Score = sum( default_severity × 1.0 × 1.4 ) across all barriers.
    (Activation multiplier at maximum = 1.0; amplification at maximum = 1.4)
    """
    return float((barriers["default_severity"].astype(float) * 1.0 * 1.4).sum())


def compute_access_risk_score(
    scheme_row: pd.Series,
    persona_row: pd.Series,
    barriers: pd.DataFrame,
) -> tuple[list[dict], float, float, float]:
    """
    Full pipeline for one (scheme, persona) pair.

    Returns:
        barrier_details  : list of per-barrier result dicts
        raw_score        : sum of all contributions
        max_possible     : maximum theoretically possible score
        normalized_score : raw_score / max_possible
    """
    activation_levels    = compute_activation_levels(scheme_row)
    amplification_factors = compute_amplification_factors(persona_row)
    max_possible         = compute_maximum_possible_score(barriers)

    barrier_details = []
    raw_score       = 0.0

    for _, barrier in barriers.iterrows():
        b_type        = str(barrier["barrier_type"]).strip().lower()
        act_label     = activation_levels.get(b_type, "none")
        amp_factor    = amplification_factors.get(b_type, 1.0)
        contribution  = compute_barrier_contribution(barrier, act_label, amp_factor)
        raw_score    += contribution

        barrier_details.append({
            "barrier_id":           barrier["barrier_id"],
            "barrier_type":         b_type,
            "affected_stage":       barrier["affected_stage"],
            "default_severity":     float(barrier["default_severity"]),
            "activation_label":     act_label,
            "activation_multiplier": ACTIVATION_MULTIPLIER.get(act_label, 0.0),
            "amplification_factor": amp_factor,
            "contribution":         contribution,
        })

    normalized_score = raw_score / max_possible if max_possible > 0 else 0.0
    return barrier_details, raw_score, max_possible, normalized_score


# ---------------------------------------------------------------------------
# OUTPUT PRINTER
# ---------------------------------------------------------------------------

def print_results(
    scheme_id: str,
    persona_id: str,
    barrier_details: list[dict],
    raw_score: float,
    max_possible: float,
    normalized_score: float,
) -> None:
    """Print a structured results block to stdout."""
    SEP  = "=" * 70
    SEP2 = "-" * 70

    print(SEP)
    print("  ACCESS RISK MODEL v1 — RESULTS")
    print(SEP)
    print(f"  Scheme ID  : {scheme_id}")
    print(f"  Persona ID : {persona_id}")
    print(SEP2)
    print(f"  {'Barrier ID':<12} {'Type':<16} {'Severity':>9} {'Act.Mult':>9} {'Amp.Factor':>11} {'Contribution':>13}")
    print(SEP2)

    for b in barrier_details:
        print(
            f"  {b['barrier_id']:<12} "
            f"{b['barrier_type']:<16} "
            f"{b['default_severity']:>9.3f} "
            f"{b['activation_multiplier']:>9.3f} "
            f"{b['amplification_factor']:>11.3f} "
            f"{b['contribution']:>13.4f}"
        )

    print(SEP2)
    print(f"  Raw Risk Score           : {raw_score:.4f}")
    print(f"  Normalized Access Risk   : {normalized_score:.4f}")
    print(SEP)


# ---------------------------------------------------------------------------
# CHECKER
# ---------------------------------------------------------------------------

def print_checker(
    barrier_details: list[dict],
    max_possible: float,
    normalized_score: float,
) -> None:
    """Print the mandatory CHECKER section for reviewer validation."""
    SEP  = "=" * 70
    SEP2 = "-" * 70

    activated = [b for b in barrier_details if b["contribution"] > 0.0]
    skipped   = [b for b in barrier_details if b["contribution"] == 0.0]

    print()
    print(SEP)
    print("  CHECKER — VALIDATION SECTION")
    print(SEP)

    # 1. Activated barriers
    print("  [1] ACTIVATED BARRIERS (non-zero contribution):")
    if activated:
        for b in activated:
            print(f"      - {b['barrier_id']} | {b['barrier_type']:16} | "
                  f"act={b['activation_label']:8} | "
                  f"contribution={b['contribution']:.4f}")
    else:
        print("      None")

    print()

    # 2. Skipped barriers
    print("  [2] SKIPPED BARRIERS (zero activation):")
    if skipped:
        for b in skipped:
            print(f"      - {b['barrier_id']} | {b['barrier_type']:16} | act={b['activation_label']}")
    else:
        print("      None — all barriers were activated")

    print()

    # 3. Maximum possible score
    print(f"  [3] MAXIMUM POSSIBLE SCORE (used for normalization): {max_possible:.4f}")
    print()

    # 4. Sanity check
    in_range = 0.0 <= normalized_score <= 1.0
    print(f"  [4] SANITY CHECK:")
    print(f"      Normalized Score = {normalized_score:.4f}")
    print(f"      Is score in [0, 1]? {'YES — PASS' if in_range else 'NO — FAIL (INVESTIGATE)'}")
    print()

    # 5. Dominant barrier type summary
    type_totals: dict[str, float] = {}
    for b in barrier_details:
        type_totals[b["barrier_type"]] = type_totals.get(b["barrier_type"], 0.0) + b["contribution"]

    total_contribution = sum(type_totals.values())
    print("  [5] BARRIER TYPE DOMINANCE SUMMARY:")
    if total_contribution > 0:
        ranked = sorted(type_totals.items(), key=lambda x: x[1], reverse=True)
        for btype, contrib in ranked:
            pct = (contrib / total_contribution) * 100
            print(f"      {btype:<16} : {contrib:.4f}  ({pct:.1f}% of raw score)")

        dominant = ranked[0]
        print()
        print(f"      >> The '{dominant[0]}' barrier type dominates the score,")
        print(f"         contributing {dominant[1]:.4f} "
              f"({(dominant[1]/total_contribution)*100:.1f}% of raw risk).")

        zero_types = [bt for bt, c in type_totals.items() if c == 0.0]
        if zero_types:
            print(f"      >> The following barrier types had zero contribution: "
                  f"{', '.join(zero_types)}.")
    else:
        print("      No barrier contributed any score. Raw risk = 0.")

    print(SEP)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def run(scheme_id: str, persona_id: str) -> None:
    """
    Entry point. Loads data, computes access risk for the given IDs, and prints results + checker.

    Args:
        scheme_id  : ID from schemes_v0.csv (scheme_id column)
        persona_id : ID from personas_v0.csv (persona_id column)
    """
    # --- load ---
    schemes, barriers, personas = load_data()

    # --- look up rows ---
    scheme_matches  = schemes[schemes["scheme_id"].str.strip() == scheme_id.strip().lower()]
    persona_matches = personas[personas["persona_id"].str.strip() == persona_id.strip().lower()]

    if scheme_matches.empty:
        raise ValueError(
            f"scheme_id '{scheme_id}' not found in schemes_v0.csv. "
            f"Available IDs: {list(schemes['scheme_id'])}"
        )
    if persona_matches.empty:
        raise ValueError(
            f"persona_id '{persona_id}' not found in personas_v0.csv. "
            f"Available IDs: {list(personas['persona_id'])}"
        )

    scheme_row  = scheme_matches.iloc[0]
    persona_row = persona_matches.iloc[0]

    # --- compute ---
    barrier_details, raw_score, max_possible, normalized_score = compute_access_risk_score(
        scheme_row, persona_row, barriers
    )

    # --- print results ---
    print_results(scheme_id, persona_id, barrier_details, raw_score, max_possible, normalized_score)

    # --- print checker ---
    print_checker(barrier_details, max_possible, normalized_score)


# ---------------------------------------------------------------------------
# ENTRY POINT — change these two IDs to run for any scheme/persona pair
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # -----------------------------------------------------------------------
    # Configure the target pair here.
    # No hardcoding of logic — only the input IDs live here.
    # Available scheme_ids : pmjay, pmmvy, jsy, mjpjay, kasp, nmmss, csss,
    #                        permatricsc, postmatricsc, mahadbt
    # Available persona_ids: p01 through p12
    # -----------------------------------------------------------------------

    TARGET_SCHEME_ID  = "pmmvy"   # Example: Pradhan Mantri Matru Vandana Yojana
    TARGET_PERSONA_ID = "p05"     # Example: low literacy, low digital, low docs, high inst. dependency

    run(TARGET_SCHEME_ID, TARGET_PERSONA_ID)
