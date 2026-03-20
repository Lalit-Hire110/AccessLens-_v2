"""
AccessLens v2 - Batch Simulation Engine v1
=====================================================
Runs Access Risk Model v1 and Counterfactual Simulation Engine v1
in batch mode across multiple scheme/persona combinations.

Produces a structured pandas DataFrame and exports to CSV.
"""

# Force UTF-8 output on Windows consoles
import sys
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import pandas as pd

# ---------------------------------------------------------------------------
# Ensure the Phase 2 folder is on the path so we can import modules
# ---------------------------------------------------------------------------
_PHASE2_DIR = os.path.dirname(os.path.abspath(__file__))
if _PHASE2_DIR not in sys.path:
    sys.path.insert(0, _PHASE2_DIR)

import access_risk_model_v1 as arm
import counterfactual_simulation_v1 as cf

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# Mode selection:
#  "A" = One scheme x All personas
#  "B" = One persona x All schemes
BATCH_MODE = "A"

# The target ID for the selected mode:
# If Mode A, target is a scheme_id (e.g. "pmmvy")
# If Mode B, target is a persona_id (e.g. "p05")
BATCH_TARGET_ID = "pmmvy"


# Output directories
_OUTPUTS_DIR = os.path.join(_PHASE2_DIR, "..", "outputs")
OUTPUT_CSV   = os.path.join(_OUTPUTS_DIR, "batch_results_v1.csv")

# ---------------------------------------------------------------------------
# CORE BATCH PROCESSOR
# ---------------------------------------------------------------------------

def _run_single_pair(scheme_row: pd.Series, persona_row: pd.Series, barriers: pd.DataFrame) -> dict:
    """Run baseline and counterfactuals for one (scheme, persona) pair, return flat dict."""
    scheme_id  = scheme_row["scheme_id"]
    persona_id = persona_row["persona_id"]

    # 1. Baseline
    _, _, _, baseline_score = arm.compute_access_risk_score(scheme_row, persona_row, barriers)

    # 2. Counterfactuals
    # We call the individual CF functions from counterfactual_simulation_v1.py
    _, _, _, score_cf1, _ = cf.apply_cf_awareness_boost(scheme_row, persona_row, barriers)
    _, _, _, score_cf2, _ = cf.apply_cf_doc_simplification(scheme_row, persona_row, barriers)
    _, _, _, score_cf3, _ = cf.apply_cf_assisted_removal(scheme_row, persona_row, barriers)
    _, _, _, score_cf4, _ = cf.apply_cf_digital_enablement(scheme_row, persona_row, barriers)

    # 3. Assemble record
    return {
        "scheme_id": scheme_id,
        "persona_id": persona_id,
        "baseline_score": baseline_score,
        "cf_awareness_score": score_cf1,
        "cf_documentation_score": score_cf2,
        "cf_assisted_removal_score": score_cf3,
        "cf_digital_enablement_score": score_cf4,
        "delta_cf_awareness": score_cf1 - baseline_score,
        "delta_cf_documentation": score_cf2 - baseline_score,
        "delta_cf_assisted_removal": score_cf3 - baseline_score,
        "delta_cf_digital_enablement": score_cf4 - baseline_score,
    }

def run_batch() -> None:
    """Execute the configured batch simulation mode."""
    SEP  = "=" * 80
    SEP2 = "-" * 80

    print(SEP)
    print("  BATCH SIMULATION ENGINE v1")
    print(SEP)
    print(f"  Mode      : {BATCH_MODE} " + ("(One Scheme x All Personas)" if BATCH_MODE == "A" else "(One Persona x All Schemes)"))
    print(f"  Target ID : {BATCH_TARGET_ID}")
    print(SEP)

    # --- Load Data ---
    schemes, barriers, personas = arm.load_data()

    # --- Determine run matrix ---
    pairs_to_run = []
    if BATCH_MODE == "A":
        # One scheme x All personas
        scheme_matches = schemes[schemes["scheme_id"] == BATCH_TARGET_ID]
        if scheme_matches.empty:
            raise ValueError(f"Scheme ID '{BATCH_TARGET_ID}' not found.")
        scheme_row = scheme_matches.iloc[0]
        
        for _, persona_row in personas.iterrows():
            pairs_to_run.append((scheme_row, persona_row))
    elif BATCH_MODE == "B":
        # One persona x All schemes
        persona_matches = personas[personas["persona_id"] == BATCH_TARGET_ID]
        if persona_matches.empty:
            raise ValueError(f"Persona ID '{BATCH_TARGET_ID}' not found.")
        persona_row = persona_matches.iloc[0]
        
        for _, scheme_row in schemes.iterrows():
            pairs_to_run.append((scheme_row, persona_row))
    else:
        raise ValueError(f"Invalid BATCH_MODE: {BATCH_MODE}. Use 'A' or 'B'.")

    # --- Execute batch ---
    records = []
    for s_row, p_row in pairs_to_run:
        records.append(_run_single_pair(s_row, p_row, barriers))

    df_results = pd.DataFrame(records)

    # --- Export ---
    os.makedirs(_OUTPUTS_DIR, exist_ok=True)
    df_results.to_csv(OUTPUT_CSV, index=False)
    print(f"  >> Exported {len(df_results)} rows to: {os.path.abspath(OUTPUT_CSV)}")

    # --- Summary Print ---
    print(SEP)
    print("  SUMMARY TABLE (first 10 rows)")
    print(SEP)
    print(df_results.head(10).to_string(index=False, float_format="%.4f"))

    # --- Analytics & Checker ---
    print("\n" + SEP)
    print("  CHECKER -- BATCH VALIDATION SECTION")
    print(SEP)

    # 1. Batch mode used
    print(f"  [1] BATCH MODE USED: {BATCH_MODE}  (Target: {BATCH_TARGET_ID})")

    # 2. Total runs executed
    total_runs = len(df_results)
    print(f"  [2] TOTAL RUNS EXECUTED: {total_runs}")

    # 3. Min / Max baseline score
    min_b = df_results["baseline_score"].min()
    max_b = df_results["baseline_score"].max()
    print(f"  [3] BASELINE SCORE RANGE: Min = {min_b:.4f}, Max = {max_b:.4f}")

    # 4. Confirmation all scores in [0,1]
    score_cols = [
        "baseline_score", "cf_awareness_score", "cf_documentation_score",
        "cf_assisted_removal_score", "cf_digital_enablement_score"
    ]
    all_scores_flat = df_results[score_cols].values.flatten()
    all_in_range = all((all_scores_flat >= 0.0) & (all_scores_flat <= 1.0))
    print(f"  [4] SANITY CHECK All scores in [0,1]? {'YES -- PASS' if all_in_range else 'NO -- FAIL'}")

    # 4b. Mean computations
    mean_baseline = df_results["baseline_score"].mean()
    if BATCH_MODE == "A":
        print(f"      Mean baseline score for scheme '{BATCH_TARGET_ID}' = {mean_baseline:.4f}")
    else:
        print(f"      Mean baseline score for persona '{BATCH_TARGET_ID}' = {mean_baseline:.4f}")

    # 5. Counterfactual effectiveness ranking (average absolute delta)
    print("\n  [5] COUNTERFACTUAL EFFECTIVENESS RANKING (Average Absolute Delta):")
    delta_cols = {
        "CF1: Awareness Improvement":      "delta_cf_awareness",
        "CF2: Documentation Simplification": "delta_cf_documentation",
        "CF3: Assisted Access Removal":      "delta_cf_assisted_removal",
        "CF4: Digital Enablement":           "delta_cf_digital_enablement"
    }
    
    avg_impacts = {}
    for name, col in delta_cols.items():
        avg_impacts[name] = df_results[col].abs().mean()
        
    ranked_impacts = sorted(avg_impacts.items(), key=lambda x: x[1], reverse=True)
    for rank, (name, impact) in enumerate(ranked_impacts, 1):
        print(f"      #{rank} {name:35} | avg |Delta| = {impact:.4f}")

    # 6. One-line interpretation
    print("\n  [6] INTERPRETATION:")
    strongest_cf = ranked_impacts[0][0]
    
    if "Documentation" in strongest_cf:
        print("      >> Documentation dominant: Scheme documentation requirements heavily penalize low document completeness in this batch.")
    elif "Digital" in strongest_cf:
        print("      >> Digital exclusion dominant: Online/hybrid delivery models strictly filter out low-digital access personas.")
    elif "Awareness" in strongest_cf:
        print("      >> Awareness dominant: Complex schemes overwhelmingly penalize low literacy across this cohort.")
    elif "Assisted" in strongest_cf:
        print("      >> Institutional dominant: The presence/absence of assisted access is structurally decisive for this batch.")
    else:
        print("      >> Mixed dominance: Frictions are evenly distributed without a single structural bottleneck in this slice.")

    print(SEP)

if __name__ == "__main__":
    run_batch()
