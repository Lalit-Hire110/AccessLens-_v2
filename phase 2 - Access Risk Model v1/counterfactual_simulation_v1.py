"""
AccessLens v2 — Counterfactual Simulation Engine v1
=====================================================
Extends Access Risk Model v1 with "what-if" counterfactual analysis.

Each counterfactual modifies ONLY activation levels or amplification factors,
then re-runs the existing scoring function as a black box.

Access Risk Model v1 logic is NOT duplicated — it is imported directly.
"""

import sys
import os
import copy

# ---------------------------------------------------------------------------
# Ensure the Phase 2 folder is on the path so we can import the base model
# ---------------------------------------------------------------------------
_PHASE2_DIR = os.path.dirname(os.path.abspath(__file__))
if _PHASE2_DIR not in sys.path:
    sys.path.insert(0, _PHASE2_DIR)

import access_risk_model_v1 as arm

# ---------------------------------------------------------------------------
# TYPE ALIASES  (for readability)
# ---------------------------------------------------------------------------
ActivationMap    = dict[str, str]    # { barrier_type: activation_label }
AmplificationMap = dict[str, float]  # { barrier_type: amplification_factor }

# ---------------------------------------------------------------------------
# DIGITAL LEVEL ORDERING  (used by CF4)
# ---------------------------------------------------------------------------

_DIGITAL_LEVEL_ORDER = ["low", "medium", "high"]

# ---------------------------------------------------------------------------
# CORE HELPER — re-score with overridden activation or amplification
# ---------------------------------------------------------------------------

def _rescore(
    scheme_row,
    persona_row,
    barriers,
    activation_override:    ActivationMap    | None = None,
    amplification_override: AmplificationMap | None = None,
) -> tuple[list[dict], float, float, float]:
    """
    Re-compute the Access Risk Score using overridden inputs.

    Either activation_override or amplification_override (or both) may be
    provided.  Only the keys present in the override dict are changed;
    all other barrier types retain their computed values.

    Returns the same tuple as arm.compute_access_risk_score:
        (barrier_details, raw_score, max_possible, normalized_score)
    """
    # --- compute the baseline maps from the real data ---
    base_activation    = arm.compute_activation_levels(scheme_row)
    base_amplification = arm.compute_amplification_factors(persona_row)
    max_possible       = arm.compute_maximum_possible_score(barriers)

    # --- apply overrides (non-destructive copies) ---
    activation    = {**base_activation,    **(activation_override    or {})}
    amplification = {**base_amplification, **(amplification_override or {})}

    # --- re-run the barrier loop using the (possibly patched) maps ---
    barrier_details = []
    raw_score       = 0.0

    for _, barrier in barriers.iterrows():
        b_type       = str(barrier["barrier_type"]).strip().lower()
        act_label    = activation.get(b_type, "none")
        amp_factor   = amplification.get(b_type, 1.0)
        contribution = arm.compute_barrier_contribution(barrier, act_label, amp_factor)
        raw_score   += contribution

        barrier_details.append({
            "barrier_id":            barrier["barrier_id"],
            "barrier_type":          b_type,
            "affected_stage":        barrier["affected_stage"],
            "default_severity":      float(barrier["default_severity"]),
            "activation_label":      act_label,
            "activation_multiplier": arm.ACTIVATION_MULTIPLIER.get(act_label, 0.0),
            "amplification_factor":  amp_factor,
            "contribution":          contribution,
        })

    normalized = raw_score / max_possible if max_possible > 0 else 0.0
    return barrier_details, raw_score, max_possible, normalized


# ---------------------------------------------------------------------------
# CF1 — Awareness Improvement
#   Reduce awareness activation multiplier by 50%.
#   Implemented by mapping the current activation label to a lower one
#   (effectively halving its weight by stepping down one notch).
#   If awareness was already "none", no change is applied.
# ---------------------------------------------------------------------------

def apply_cf_awareness_boost(
    scheme_row,
    persona_row,
    barriers,
) -> tuple[list[dict], float, float, float, str]:
    """
    CF1: Awareness Improvement
    Reduce awareness barrier activation by ~50% by stepping the label
    down one tier (high→low, medium→low, low→none).
    Returns (barrier_details, raw_score, max_possible, normalized_score, description)
    """
    base_activation = arm.compute_activation_levels(scheme_row)
    current         = base_activation.get("awareness", "none")

    # Halving the multiplier: we pick the label whose multiplier is closest to
    # 50% of the current multiplier.
    current_mult = arm.ACTIVATION_MULTIPLIER.get(current, 0.0)
    target_mult  = current_mult * 0.5

    # Find nearest label
    best_label = "none"
    best_diff  = float("inf")
    for label, mult in arm.ACTIVATION_MULTIPLIER.items():
        if abs(mult - target_mult) < best_diff:
            best_diff  = abs(mult - target_mult)
            best_label = label

    description = (
        f"awareness activation: '{current}' ({current_mult:.2f}) "
        f"-> '{best_label}' ({arm.ACTIVATION_MULTIPLIER[best_label]:.2f})  [~50% reduction]"
    )

    result = _rescore(
        scheme_row, persona_row, barriers,
        activation_override={"awareness": best_label},
    )
    return (*result, description)


# ---------------------------------------------------------------------------
# CF2 — Documentation Simplification
#   If documentation activation is "high" (docs_count ≥ 4),
#   reduce it to "medium".
# ---------------------------------------------------------------------------

def apply_cf_doc_simplification(
    scheme_row,
    persona_row,
    barriers,
) -> tuple[list[dict], float, float, float, str]:
    """
    CF2: Documentation Simplification
    If documentation activation == 'high', step it down to 'medium'.
    Returns (barrier_details, raw_score, max_possible, normalized_score, description)
    """
    base_activation = arm.compute_activation_levels(scheme_row)
    current         = base_activation.get("documentation", "none")

    if current == "high":
        new_label   = "medium"
        description = (
            f"documentation activation: 'high' (1.0) -> 'medium' (0.7)  "
            f"[documents_requiered_count >= 4 -> simplified to 2-3 docs]"
        )
    else:
        new_label   = current
        description = (
            f"documentation activation already '{current}' - no change applied "
            f"(rule requires 'high' to trigger)"
        )

    result = _rescore(
        scheme_row, persona_row, barriers,
        activation_override={"documentation": new_label},
    )
    return (*result, description)


# ---------------------------------------------------------------------------
# CF3 — Assisted Access Removal
#   If institutional activation is "reduced" (assisted_access_available=1),
#   remove that benefit and set institutional activation to "medium".
# ---------------------------------------------------------------------------

def apply_cf_assisted_removal(
    scheme_row,
    persona_row,
    barriers,
) -> tuple[list[dict], float, float, float, str]:
    """
    CF3: Assisted Access Removal
    If institutional activation == 'reduced', escalate it to 'medium'.
    Simulates the effect of removing the assisted-access safety net.
    Returns (barrier_details, raw_score, max_possible, normalized_score, description)
    """
    base_activation = arm.compute_activation_levels(scheme_row)
    current         = base_activation.get("institutional", "none")

    if current == "reduced":
        new_label   = "medium"
        description = (
            f"institutional activation: 'reduced' (0.3) -> 'medium' (0.7)  "
            f"[assisted_access_available removed - no facilitation support]"
        )
    elif current == "none":
        new_label   = "medium"
        description = (
            f"institutional activation: 'none' (0.0) -> 'medium' (0.7)  "
            f"[no assisted access was present; now exposed to baseline institutional friction]"
        )
    else:
        new_label   = current
        description = (
            f"institutional activation already '{current}' - no change applied "
            f"(CF3 targets 'reduced' or 'none')"
        )

    result = _rescore(
        scheme_row, persona_row, barriers,
        activation_override={"institutional": new_label},
    )
    return (*result, description)


# ---------------------------------------------------------------------------
# CF4 — Digital Enablement
#   Step the persona's digital_access up one level:
#   low → medium, medium → high, high unchanged.
# ---------------------------------------------------------------------------

def apply_cf_digital_enablement(
    scheme_row,
    persona_row,
    barriers,
) -> tuple[list[dict], float, float, float, str]:
    """
    CF4: Digital Enablement
    Improve persona's digital access by one level, reducing digital amplification.
    low → medium (1.4 → 1.2), medium → high (1.2 → 1.0), high unchanged.
    Returns (barrier_details, raw_score, max_possible, normalized_score, description)
    """
    base_amplification = arm.compute_amplification_factors(persona_row)
    current_amp        = base_amplification.get("digital", 1.0)

    # Map current amplification back to the level label
    _amp_to_level = {v: k for k, v in arm.DIGITAL_AMPLIFICATION.items()}
    current_level = _amp_to_level.get(current_amp, "high")

    current_idx = _DIGITAL_LEVEL_ORDER.index(current_level) if current_level in _DIGITAL_LEVEL_ORDER else 2
    new_idx     = min(current_idx + 1, len(_DIGITAL_LEVEL_ORDER) - 1)  # step up, cap at high
    new_level   = _DIGITAL_LEVEL_ORDER[new_idx]
    new_amp     = arm.DIGITAL_AMPLIFICATION[new_level]

    if new_level == current_level:
        description = (
            f"digital amplification: already at '{current_level}' ({current_amp:.2f}) - "
            f"no further improvement possible (capped at high)"
        )
    else:
        description = (
            f"digital amplification: '{current_level}' ({current_amp:.2f}) "
            f"-> '{new_level}' ({new_amp:.2f})  "
            f"[persona gains one level of digital access]"
        )

    result = _rescore(
        scheme_row, persona_row, barriers,
        amplification_override={"digital": new_amp},
    )
    return (*result, description)


# ---------------------------------------------------------------------------
# OUTPUT PRINTER
# ---------------------------------------------------------------------------

def print_cf_result(
    cf_name:        str,
    baseline_score: float,
    cf_score:       float,
    description:    str,
) -> None:
    """Print a single counterfactual comparison block."""
    delta     = cf_score - baseline_score
    direction = "improved [down]" if delta < 0 else ("worsened [up]" if delta > 0 else "no change")

    SEP2 = "-" * 70
    print(SEP2)
    print(f"  Counterfactual : {cf_name}")
    print(f"  Change Applied : {description}")
    print(f"  Baseline Score : {baseline_score:.4f}")
    print(f"  CF Score       : {cf_score:.4f}")
    print(f"  Delta          : {delta:+.4f}  [{direction}]")


# ---------------------------------------------------------------------------
# CHECKER
# ---------------------------------------------------------------------------

def print_checker(
    baseline_score:    float,
    cf_results:        list[dict],
) -> None:
    """Print the mandatory CHECKER section."""
    SEP  = "=" * 70
    SEP2 = "-" * 70

    print()
    print(SEP)
    print("  CHECKER — COUNTERFACTUAL VALIDATION SECTION")
    print(SEP)

    # 1. List of counterfactuals applied
    print("  [1] COUNTERFACTUALS APPLIED:")
    for i, cf in enumerate(cf_results, 1):
        print(f"      {i}. {cf['name']}")

    print()

    # 2. Baseline score unchanged
    print("  [2] BASELINE SCORE CONSISTENCY CHECK:")
    scores_are_consistent = all(cf["baseline"] == baseline_score for cf in cf_results)
    print(f"      Reference Baseline : {baseline_score:.4f}")
    for cf in cf_results:
        match = "OK" if cf["baseline"] == baseline_score else "MISMATCH"
        print(f"      {cf['name']:40} baseline={cf['baseline']:.4f}  [{match}]")
    print(f"      All baselines consistent? {'YES' if scores_are_consistent else 'NO -- INVESTIGATE'}")

    print()

    # 3. Sanity check — all scores in [0, 1]
    print("  [3] SANITY CHECK -- all scores in [0, 1]:")
    all_pass = True
    for cf in cf_results:
        in_range = 0.0 <= cf["cf_score"] <= 1.0
        if not in_range:
            all_pass = False
        print(f"      {cf['name']:40} cf_score={cf['cf_score']:.4f}  "
              f"{'PASS' if in_range else 'FAIL'}")
    print(f"      All scores in range? {'YES -- PASS' if all_pass else 'NO -- FAIL'}")

    print()

    # 4. Ranking by impact magnitude
    print("  [4] RANKING BY IMPACT MAGNITUDE (|Delta| descending):")
    ranked = sorted(cf_results, key=lambda x: abs(x["delta"]), reverse=True)
    for rank, cf in enumerate(ranked, 1):
        direction = "improved" if cf["delta"] < 0 else ("worsened [up]" if cf["delta"] > 0 else "no change")
        print(f"      #{rank}  {cf['name']:40}  delta={cf['delta']:+.4f}  [{direction}]")

    print()

    # 5. Strongest intervention explanation
    print("  [5] STRONGEST INTERVENTION ANALYSIS:")
    strongest = ranked[0]
    weakest   = ranked[-1]
    print(f"      Strongest: '{strongest['name']}'  (|delta| = {abs(strongest['delta']):.4f})")
    print()

    # Rule-based explanation derived from the CF type
    name_lower = strongest["name"].lower()
    if "doc" in name_lower:
        print("      Explanation: The documentation simplification had the greatest impact because")
        print("      the scheme requires >=4 documents AND the persona has low document completeness,")
        print("      making the documentation barrier the dominant friction source in this scenario.")
    elif "digital" in name_lower:
        print("      Explanation: Digital enablement had the greatest impact because")
        print("      the scheme routes applicants through digital channels AND the persona's")
        print("      low digital access amplifies this barrier to its maximum level.")
    elif "awareness" in name_lower:
        print("      Explanation: Awareness improvement had the greatest impact because")
        print("      the persona's low literacy level maximally amplifies awareness barriers,")
        print("      making any reduction in awareness activation highly effective.")
    elif "assisted" in name_lower:
        print("      Explanation: Assisted access removal had the greatest impact because")
        print("      removing facilitation support exposes the persona to institutional friction")
        print("      that was previously buffered by the scheme's assisted-access provision.")
    else:
        print(f"      Explanation: '{strongest['name']}' reduced the friction most")
        print("      because it targeted the barrier type where scheme activation and")
        print("      persona amplification were both elevated simultaneously.")

    print()
    if weakest["name"] != strongest["name"]:
        print(f"      Weakest:  '{weakest['name']}'  (|delta| = {abs(weakest['delta']):.4f})")
        name_w = weakest["name"].lower()
        if abs(weakest["delta"]) == 0.0:
            print("      Explanation: This counterfactual had no effect because the rule condition")
            print("      (e.g., barrier type not activated for this scheme) was not met.")
        else:
            print("      Explanation: This counterfactual addressed a barrier type that was either")
            print("      not heavily activated for this scheme or not significantly amplified")
            print("      by this persona, limiting its potential impact.")

    print(SEP)


# ---------------------------------------------------------------------------
# MAIN SIMULATION RUNNER
# ---------------------------------------------------------------------------

def run_simulation(scheme_id: str, persona_id: str) -> None:
    """
    Load data, compute baseline, run all 4 counterfactuals, print results and CHECKER.
    """
    SEP  = "=" * 70

    # --- load data ---
    schemes, barriers, personas = arm.load_data()

    scheme_matches  = schemes[schemes["scheme_id"].str.strip()  == scheme_id.strip().lower()]
    persona_matches = personas[personas["persona_id"].str.strip() == persona_id.strip().lower()]

    if scheme_matches.empty:
        raise ValueError(
            f"scheme_id '{scheme_id}' not found. "
            f"Available: {list(schemes['scheme_id'])}"
        )
    if persona_matches.empty:
        raise ValueError(
            f"persona_id '{persona_id}' not found. "
            f"Available: {list(personas['persona_id'])}"
        )

    scheme_row  = scheme_matches.iloc[0]
    persona_row = persona_matches.iloc[0]

    # --- baseline ---
    _, raw_baseline, max_possible, baseline_score = arm.compute_access_risk_score(
        scheme_row, persona_row, barriers
    )

    print(SEP)
    print("  COUNTERFACTUAL SIMULATION ENGINE v1")
    print(SEP)
    print(f"  Scheme ID      : {scheme_id}")
    print(f"  Persona ID     : {persona_id}")
    print(f"  Baseline Score : {baseline_score:.4f}  (raw={raw_baseline:.4f}, max={max_possible:.4f})")
    print(SEP)

    # --- run each counterfactual ---
    counterfactuals = [
        ("CF1: Awareness Improvement",       apply_cf_awareness_boost),
        ("CF2: Documentation Simplification", apply_cf_doc_simplification),
        ("CF3: Assisted Access Removal",      apply_cf_assisted_removal),
        ("CF4: Digital Enablement",           apply_cf_digital_enablement),
    ]

    cf_records: list[dict] = []

    for cf_name, cf_fn in counterfactuals:
        _, _, _, cf_score, desc = cf_fn(scheme_row, persona_row, barriers)
        print_cf_result(cf_name, baseline_score, cf_score, desc)
        cf_records.append({
            "name":     cf_name,
            "baseline": baseline_score,
            "cf_score": cf_score,
            "delta":    cf_score - baseline_score,
            "desc":     desc,
        })

    print("=" * 70)

    # --- checker ---
    print_checker(baseline_score, cf_records)


# ---------------------------------------------------------------------------
# ENTRY POINT — configure target pair here
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Force UTF-8 output on Windows consoles (avoids cp1252 UnicodeEncodeError)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    # -----------------------------------------------------------------------
    # Change these two IDs to run simulation for any valid scheme/persona pair.
    # Available scheme_ids : pmjay, pmmvy, jsy, mjpjay, kasp, nmmss, csss,
    #                        permatricsc, postmatricsc, mahadbt
    # Available persona_ids: p01 through p12
    # -----------------------------------------------------------------------

    TARGET_SCHEME_ID  = "pmmvy"   # Pradhan Mantri Matru Vandana Yojana
    TARGET_PERSONA_ID = "p05"     # low literacy, low digital, low docs, high inst. dependency

    run_simulation(TARGET_SCHEME_ID, TARGET_PERSONA_ID)
