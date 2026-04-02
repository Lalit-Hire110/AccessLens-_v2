"""
AccessLens v2 — Integration Pipeline v1
=========================================
Full pipeline connecting:
  - Persona Mapping Function  (PMF)
  - Eligibility Discovery Module  (EDM)
  - Access Risk Model

Pipeline:
    1. Map user input → persona  (PMF)
    2. Load schemes & rank by eligibility  (EDM)
    3. For each top-K scheme, compute access risk score
    4. Derive access gap & generate insight
    5. Return unified recommendation payload
"""

import json
import logging
import os
import sys

import pandas as pd

# ---------------------------------------------------------------------------
# Path setup — add parent directories so sibling packages are importable
# ---------------------------------------------------------------------------

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_PHASE2_DIR = os.path.join(_PROJECT_ROOT, "phase 2 - Access Risk Model v1")

# Ensure both phase dirs are on sys.path
for _p in (_SCRIPT_DIR, _PHASE2_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# Imports from project modules
# ---------------------------------------------------------------------------

from persona_mapping_v1 import map_persona, load_personas
from eligibility_engine_v1 import load_schemes, rank_schemes
from access_risk_model_v1 import compute_access_risk_score

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("accesslens.pipeline")

# ---------------------------------------------------------------------------
# Data paths
# ---------------------------------------------------------------------------

PERSONAS_CSV = os.path.join(_PROJECT_ROOT, "data", "personas", "personas_v1.csv")
BARRIERS_CSV = os.path.join(_PROJECT_ROOT, "data", "barriers", "barriers_v0.csv")


# ---------------------------------------------------------------------------
# Helper — load barriers
# ---------------------------------------------------------------------------


def _load_barriers() -> pd.DataFrame:
    """Load barriers CSV and normalise string columns."""
    if not os.path.isfile(BARRIERS_CSV):
        raise FileNotFoundError(f"Barriers file not found: {BARRIERS_CSV}")
    df = pd.read_csv(BARRIERS_CSV)
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip().str.lower()
    return df


# ---------------------------------------------------------------------------
# Insight generation
# ---------------------------------------------------------------------------


def _generate_insight(eligibility_label: str, risk_score: float) -> str:
    """Generate a human-readable insight from eligibility label and risk score.

    Rules
    -----
    * eligibility high AND risk high (≥ 0.5) →
        "High eligibility but significant access barriers"
    * eligibility high AND risk low (< 0.5) →
        "Highly accessible and recommended"
    * eligibility medium →
        "Moderate eligibility with some barriers"
    * otherwise →
        "Low priority scheme"
    """
    risk_high = risk_score >= 0.5

    if eligibility_label == "high" and risk_high:
        return "High eligibility but significant access barriers"
    elif eligibility_label == "high" and not risk_high:
        return "Highly accessible and recommended"
    elif eligibility_label == "medium":
        return "Moderate eligibility with some barriers"
    else:
        return "Low priority scheme"


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def run_accesslens_pipeline(
    user_input: dict,
    top_k: int = 5,
) -> dict:
    """Run the full AccessLens recommendation pipeline.

    Parameters
    ----------
    user_input : dict
        Raw user profile dictionary (age, gender, income_level, etc.).
    top_k : int, default 5
        Number of top-ranked schemes to include in recommendations.

    Returns
    -------
    dict
        ``{"persona": {...}, "recommendations": [...]}``.
        Each recommendation contains scheme_id, scheme_name,
        eligibility_score, eligibility, risk_score, access_gap, and insight.
    """

    # ------------------------------------------------------------------
    # 1. Load reference data
    # ------------------------------------------------------------------
    logger.info("Loading personas …")
    personas_df = load_personas(PERSONAS_CSV)

    logger.info("Loading schemes …")
    schemes_df = load_schemes(_PROJECT_ROOT, verbose=False)

    logger.info("Loading barriers …")
    barriers_df = _load_barriers()

    # ------------------------------------------------------------------
    # 2. MAP PERSONA  (PMF)
    # ------------------------------------------------------------------
    logger.info("Mapping persona …")
    try:
        persona_result = map_persona(user_input, personas_df)
    except Exception as exc:
        logger.error("Persona mapping failed: %s", exc)
        raise RuntimeError(f"Persona mapping failed: {exc}") from exc

    persona_data: dict = persona_result["matched_persona"]

    # ------------------------------------------------------------------
    # 3. RUN EDM — rank schemes by eligibility
    # ------------------------------------------------------------------
    logger.info("Ranking schemes by eligibility …")
    try:
        ranked_schemes = rank_schemes(persona_data, schemes_df, verbose=False)
    except Exception as exc:
        logger.error("Eligibility ranking failed: %s", exc)
        raise RuntimeError(f"Eligibility ranking failed: {exc}") from exc

    # ------------------------------------------------------------------
    # 4. SELECT TOP K
    # ------------------------------------------------------------------
    top_schemes = ranked_schemes[:top_k]

    # ------------------------------------------------------------------
    # 5 – 8. COMPUTE ACCESS RISK, GAP & INSIGHT for each top scheme
    # ------------------------------------------------------------------
    recommendations: list[dict] = []

    for scheme_entry in top_schemes:
        scheme_id = scheme_entry["scheme_id"]
        eligibility_score = scheme_entry["score"]
        eligibility_label = scheme_entry["eligibility"]

        # Find the full scheme row from the EDM DataFrame
        scheme_rows = schemes_df[schemes_df["scheme_id"] == scheme_id]

        if scheme_rows.empty:
            logger.warning("Scheme '%s' not found in DataFrame — skipping", scheme_id)
            continue

        scheme_row = scheme_rows.iloc[0]

        # Convert persona dict → pd.Series for the risk model
        persona_series = pd.Series(persona_data)

        # Compute access risk
        try:
            _, _, _, normalised_risk = compute_access_risk_score(
                scheme_row, persona_series, barriers_df
            )
            risk_score = round(float(normalised_risk), 6)
        except Exception as exc:
            logger.warning(
                "Access risk computation failed for '%s': %s — defaulting to 0.0",
                scheme_id, exc,
            )
            risk_score = 0.0

        # Access gap = eligibility − risk
        access_gap = round(eligibility_score - risk_score, 6)

        # Insight
        insight = _generate_insight(eligibility_label, risk_score)

        recommendations.append({
            "scheme_id": scheme_id,
            "scheme_name": scheme_entry["scheme_name"],
            "eligibility_score": eligibility_score,
            "eligibility": eligibility_label,
            "risk_score": risk_score,
            "access_gap": access_gap,
            "insight": insight,
        })

    # ------------------------------------------------------------------
    # 9. FINAL OUTPUT
    # ------------------------------------------------------------------
    return {
        "persona": persona_data,
        "recommendations": recommendations,
    }


# ---------------------------------------------------------------------------
# 10. CLI Test Block
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="  [%(levelname)s] %(name)s — %(message)s",
    )

    print("=" * 72)
    print("  AccessLens v2 — Integration Pipeline v1  —  Test Run")
    print("=" * 72)

    # Sample user input
    sample_user = {
        "age": 26,
        "gender": "male",
        "rural_urban": "urban",
        "income_level": "middle",
        "occupation": "worker",
        "education_level": "graduate",
        "digital_access": "full",
        "document_completeness": 0.75,
        "institutional_dependency": "low",
    }

    print("\n  User Input:")
    for k, v in sample_user.items():
        print(f"    {k:30s}: {v}")

    print("\n  Running pipeline (top_k=5) …\n")

    result = run_accesslens_pipeline(sample_user, top_k=5)

    # --- Print persona ---
    print("-" * 72)
    print("  MATCHED PERSONA")
    print("-" * 72)
    for k, v in result["persona"].items():
        print(f"    {k:30s}: {v}")

    # --- Print recommendations ---
    print("\n" + "-" * 72)
    print("  RECOMMENDATIONS")
    print("-" * 72)
    print(
        f"  {'#':<4}{'Scheme ID':<12}{'Elig.':<10}{'Risk':<10}"
        f"{'Gap':<10}{'Label':<16}{'Insight'}"
    )
    print("  " + "-" * 68)

    for i, rec in enumerate(result["recommendations"], start=1):
        print(
            f"  {i:<4}{rec['scheme_id']:<12}"
            f"{rec['eligibility_score']:<10.4f}"
            f"{rec['risk_score']:<10.4f}"
            f"{rec['access_gap']:<10.4f}"
            f"{rec['eligibility']:<16}"
            f"{rec['insight']}"
        )

    # --- JSON dump ---
    print("\n" + "-" * 72)
    print("  FULL JSON OUTPUT")
    print("-" * 72)
    print(json.dumps(result, indent=2, default=str))
    print("=" * 72)
